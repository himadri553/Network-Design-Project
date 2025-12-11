import socket
import time
import random
from packet5 import PHASE5_PACKET, FLAG_SYN, FLAG_ACK, FLAG_FIN, FLAG_DATA

class SENDER5:
    def __init__(
        self,
        plotter,
        receiver_ip="127.0.0.1",
        receiver_port=12000,
        loss_prob=0.0,
        init_cwnd=1.0,
        max_cwnd=50.0,
        init_rto=0.2,
        mode="reno"
    ):
        self.plotter = plotter
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.loss_prob = loss_prob
        self.mode = mode  # "reno" or "tahoe"

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.01)

        # Congestion control
        self.cwnd = init_cwnd       # in segments
        self.ssthresh = 32.0
        self.max_cwnd = max_cwnd

        # RTT / RTO
        self.estimated_rtt = init_rto
        self.dev_rtt = init_rto / 2
        self.rto = init_rto
        self.alpha = 0.125
        self.beta = 0.25

        # Sender state
        self.send_base = 1          # first unacked seq
        self.next_seq = 1           # next seq to assign
        self.unacked = {}           # seq -> (packet_bytes, first_send_time, last_send_time, valid_for_rtt)
        self.mss = 1                # each packet counts as "1 segment" for cwnd

        self.connected = False
        self.time0 = time.time()    # reference time for plotting

        # For Reno fast retransmit
        self.last_acked = 0
        self.dup_ack_count = 0

        # Logging
        self.cwnd_series = []       # (t, cwnd)
        self.rtt_series = []        # (t, rtt)
        self.rto_series = []        # (t, rto)

    # ---------- helpers ----------

    def now(self):
        return time.time() - self.time0

    def send_packet(self, pkt: PHASE5_PACKET):
        raw = pkt.pack()
        # simulate loss on DATA packets only
        if pkt.flags & FLAG_DATA and random.random() < self.loss_prob:
            return
        self.sock.sendto(raw, (self.receiver_ip, self.receiver_port))

    def log_state(self):
        t = self.now()
        self.cwnd_series.append((t, self.cwnd))
        self.rto_series.append((t, self.rto))

    # ---------- handshake / teardown ----------

    def three_way_handshake(self):
        # 1. send SYN
        syn = PHASE5_PACKET(seq=0, ack=0, flags=FLAG_SYN, wnd=0)
        self.send_packet(syn)

        # 2. wait for SYN-ACK
        while True:
            try:
                raw, _ = self.sock.recvfrom(2048)
            except socket.timeout:
                # retransmit SYN
                self.send_packet(syn)
                continue

            pkt = PHASE5_PACKET.unpack(raw)
            if pkt.valid and (pkt.flags & FLAG_SYN) and (pkt.flags & FLAG_ACK):
                # 3. send final ACK
                ack = PHASE5_PACKET(seq=1, ack=pkt.seq + 1, flags=FLAG_ACK, wnd=0)
                self.send_packet(ack)
                self.connected = True
                return

    def teardown(self):
        fin = PHASE5_PACKET(seq=self.next_seq, ack=0, flags=FLAG_FIN, wnd=0)
        self.send_packet(fin)

        # wait for ACK to FIN (best-effort)
        end_time = time.time() + 1.0
        while time.time() < end_time:
            try:
                raw, _ = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            pkt = PHASE5_PACKET.unpack(raw)
            if pkt.valid and (pkt.flags & FLAG_ACK) and pkt.ack == fin.seq + 1:
                break

    # ---------- RTT / RTO update ----------

    def update_rtt_rto(self, sample_rtt):
        # EWMA per TCP
        self.estimated_rtt = (1 - self.alpha) * self.estimated_rtt + self.alpha * sample_rtt
        self.dev_rtt = (1 - self.beta) * self.dev_rtt + self.beta * abs(sample_rtt - self.estimated_rtt)
        self.rto = self.estimated_rtt + 4 * self.dev_rtt
        if self.rto < 0.05:
            self.rto = 0.05
        if self.rto > 1.0:
            self.rto = 1.0

        t = self.now()
        self.rtt_series.append((t, sample_rtt))
        self.rto_series.append((t, self.rto))

    # ---------- congestion control ----------

    def on_new_ack(self, ack_seq):
        # called when we advance send_base
        if self.cwnd < self.ssthresh:
            # Slow Start: cwnd += 1 MSS per ACK
            self.cwnd += 1.0
        else:
            # Congestion avoidance: cwnd += MSS^2 / cwnd (~1 MSS per RTT)
            self.cwnd += 1.0 / self.cwnd

        if self.cwnd > self.max_cwnd:
            self.cwnd = self.max_cwnd

        self.log_state()

    def on_timeout(self):
        # multiplicative decrease
        self.ssthresh = max(self.cwnd / 2.0, 1.0)
        if self.mode == "tahoe" or self.mode == "reno":
            # both Tahoe & Reno drop to cwnd = 1 on timeout
            self.cwnd = 1.0
        self.log_state()

    def on_triple_dup_ack(self):
        # Fast retransmit + fast recovery (Reno)
        if self.mode == "reno":
            self.ssthresh = max(self.cwnd / 2.0, 1.0)
            self.cwnd = self.ssthresh + 3.0
        elif self.mode == "tahoe":
            self.ssthresh = max(self.cwnd / 2.0, 1.0)
            self.cwnd = 1.0
        self.log_state()

    # ---------- main transmission ----------

    def run_tx(self, img_in_chunks, scenario_num=0):
        """
        Returns a dict with:
          - cwnd_series, rtt_series, rto_series, completion_time
        """
        self.time0 = time.time()
        self.log_state()

        # handshake
        self.three_way_handshake()

        file_chunks = img_in_chunks
        total_pkts = len(file_chunks)
        next_data_index = 0

        # main loop
        start_time = time.time()
        while self.send_base <= total_pkts or self.unacked:
            # send new packets while window allows
            while (self.next_seq - self.send_base) < int(self.cwnd) and next_data_index < total_pkts:
                payload = file_chunks[next_data_index]
                seq = self.next_seq
                pkt = PHASE5_PACKET(seq=seq, ack=0, flags=FLAG_DATA, wnd=0, payload=payload)
                now = time.time()
                self.unacked[seq] = [pkt.pack(), now, now, True]  # bytes, first_send, last_send, valid_for_rtt
                self.sock.sendto(self.unacked[seq][0], (self.receiver_ip, self.receiver_port))
                if self.send_base == seq:
                    self.send_base_timer_start = now
                self.next_seq += 1
                next_data_index += 1

            # receive ACKs
            try:
                raw, _ = self.sock.recvfrom(2048)
                pkt = PHASE5_PACKET.unpack(raw)
            except socket.timeout:
                pkt = None

            if pkt and pkt.valid and (pkt.flags & FLAG_ACK):
                ack_num = pkt.ack
                # cumulative ACK for all seq < ack_num
                if ack_num > self.last_acked:
                    self.dup_ack_count = 0
                    # compute RTT for the highest newly-acked seq (lowest in unacked)
                    newly_acked = [s for s in list(self.unacked.keys()) if s < ack_num]
                    newly_acked.sort()
                    for s in newly_acked:
                        bytes_, first_send, last_send, valid_for_rtt = self.unacked.pop(s)
                        if valid_for_rtt:
                            sample_rtt = time.time() - first_send
                            self.update_rtt_rto(sample_rtt)
                    self.send_base = ack_num
                    self.last_acked = ack_num
                    self.on_new_ack(ack_num)
                elif ack_num == self.last_acked:
                    # dup ACK
                    self.dup_ack_count += 1
                    if self.dup_ack_count == 3:
                        # fast retransmit last_acked
                        lost_seq = self.last_acked
                        if lost_seq in self.unacked:
                            bytes_, first_send, last_send, valid_for_rtt = self.unacked[lost_seq]
                            # do not use this retransmission for RTT
                            self.unacked[lost_seq][3] = False
                            self.sock.sendto(bytes_, (self.receiver_ip, self.receiver_port))
                        self.on_triple_dup_ack()
                # else older ACK – ignore

            # handle timeouts
            now = time.time()
            for seq, (bytes_, first_send, last_send, valid_rtt) in list(self.unacked.items()):
                if now - last_send >= self.rto:
                    # timeout
                    self.on_timeout()
                    # retransmit all unacked packets
                    for s2 in sorted(self.unacked.keys()):
                        pk_bytes, fs, ls, vr = self.unacked[s2]
                        self.unacked[s2][2] = now
                        self.unacked[s2][3] = False  # retransmissions not used for RTT
                        self.sock.sendto(pk_bytes, (self.receiver_ip, self.receiver_port))
                    break  # only handle one timeout per loop

            self.log_state()

        # teardown
        self.teardown()
        completion_time = time.time() - start_time
        return {
            "cwnd_series": self.cwnd_series,
            "rtt_series": self.rtt_series,
            "rto_series": self.rto_series,
            "completion_time": completion_time,
        }
