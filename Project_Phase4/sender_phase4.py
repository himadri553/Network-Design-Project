"""
    Nour Fahmy, Himadri Saha 

    sender_phase4.py:
    - Go-Back-N Sender with loss/bit-error injection for plotting experiments.
"""

import socket
import time
import random

class GBN_Sender:
    def __init__(self, receiver_ip, receiver_port,
                 scenario=1, loss_prob=0.0,
                 window_size=10, timeout_interval=0.05):

        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.window_size = window_size
        self.timeout_interval = timeout_interval

        # NEW: scenario + loss probability
        self.scenario = scenario
        self.loss_prob = loss_prob

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.01)


        # GBN variables
        self.base = 1
        self.nextseqnum = 1
        self.sndpkt = {}  # seq → bytes

        # Timer
        self.timer_running = False
        self.timer_start_time = None

    # -------------- TIMER --------------
    def start_timer(self):
        self.timer_running = True
        self.timer_start_time = time.time()

    def stop_timer(self):
        self.timer_running = False
        self.timer_start_time = None

    def timer_expired(self):
        if not self.timer_running:
            return False
        return (time.time() - self.timer_start_time) >= self.timeout_interval

    # -------------- LOSS / ERROR SIMULATION --------------

    def maybe_drop_ack(self):
        """Scenario 4: ACK loss — randomly drop ACK before processing."""
        if self.scenario == 4:
            return random.random() < self.loss_prob
        return False

    def maybe_corrupt_ack(self, ack_bytes):
        """Scenario 2: ACK bit error — corrupt ack with probability."""
        if self.scenario == 2 and random.random() < self.loss_prob:
            # Corrupt by replacing with nonsense
            return b'999999'
        return ack_bytes

    # -------------- SEND PACKET (NO LOSS HERE FOR GBN SENDER) --------------
    # NOTE: Packet *loss* for DATA packets belongs ONLY to the RECEIVER (scenario 5).

    def udt_send(self, packet):
        self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))

    def resend_window(self):
        for seq in range(self.base, self.nextseqnum):
            self.udt_send(self.sndpkt[seq])
        self.start_timer()

    # -------------- MAIN SEND LOOP --------------

    def run_sender(self, file_bytes):
        CHUNK = 1024
        file_chunks = [file_bytes[i:i+CHUNK] for i in range(0, len(file_bytes), CHUNK)]
        total = len(file_chunks)

        while self.base <= total:

            # Send new packets while window is open
            if self.nextseqnum < self.base + self.window_size and self.nextseqnum <= total:

                payload = file_chunks[self.nextseqnum - 1]
                packet = b'%d|' % self.nextseqnum + payload
                self.sndpkt[self.nextseqnum] = packet

                # ALWAYS allow send — sender does no data loss here
                self.udt_send(packet)

                if self.base == self.nextseqnum:
                    self.start_timer()

                self.nextseqnum += 1

            # Receive ACK
            try:
                ackpkt, _ = self.sock.recvfrom(2048)

                # Scenario 4: randomly drop ACK completely
                if self.maybe_drop_ack():
                    continue

                # Scenario 2: maybe corrupt the ack
                ackpkt = self.maybe_corrupt_ack(ackpkt)

                # Parse ACK
                try:
                    acknum = int(ackpkt.decode())
                except:
                    # corrupted ack, ignore
                    continue

                if acknum >= self.base:
                    self.base = acknum + 1
                    if self.base == self.nextseqnum:
                        self.stop_timer()
                    else:
                        self.start_timer()

            except socket.timeout:
                pass

            # Timeout → resend window
            if self.timer_expired():
                self.resend_window()

        return  # completion time is measured in the caller
