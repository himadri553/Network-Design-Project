# phase5_reciver.py
import socket
import os
from packet5 import PHASE5_PACKET, FLAG_SYN, FLAG_ACK, FLAG_FIN, FLAG_DATA

class RECIVER5:
    def __init__(self, plotter, listen_port=12000, rwnd=64):
        self.plotter = plotter
        self.listen_port = listen_port
        self.rwnd = rwnd

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", listen_port))


        # connection state
        self.expected_seq = 1
        self.connected = False
        self.sender_addr = None
        self.received_payloads = []

    def send_packet(self, pkt: PHASE5_PACKET):
        raw = pkt.pack()
        self.sock.sendto(raw, self.sender_addr)

    def handshake(self):
        # wait for SYN
        while True:
            raw, addr = self.sock.recvfrom(2048)
            pkt = PHASE5_PACKET.unpack(raw)
            if pkt.valid and (pkt.flags & FLAG_SYN):
                self.sender_addr = addr
                # send SYN-ACK
                synack = PHASE5_PACKET(
                    seq=100, ack=pkt.seq + 1,
                    flags=FLAG_SYN | FLAG_ACK,
                    wnd=self.rwnd
                )
                self.send_packet(synack)
                break

        # wait for final ACK
        while True:
            raw, _ = self.sock.recvfrom(2048)
            pkt = PHASE5_PACKET.unpack(raw)
            if pkt.valid and (pkt.flags & FLAG_ACK):
                self.connected = True
                return

    def write_image(self):
        dest_dir = os.path.join("Project_Phase5", "img")
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, "received_img.bmp")
        with open(dest_path, "wb") as f:
            for chunk in self.received_payloads:
                f.write(chunk)
        print(f"RX: wrote image to {dest_path}")

    def run_rx(self):
        print("RX: listening for Phase 5 TCP-over-UDP...")

        self.handshake()
        print("RX: handshake complete, receiving data")

        while True:
            raw, addr = self.sock.recvfrom(4096)
            self.sender_addr = addr
            pkt = PHASE5_PACKET.unpack(raw)
            if not pkt.valid:
                # checksum failed → send ACK for last in-order seq
                ack_pkt = PHASE5_PACKET(
                    seq=0, ack=self.expected_seq, flags=FLAG_ACK, wnd=self.rwnd
                )
                self.send_packet(ack_pkt)
                continue

            if pkt.flags & FLAG_FIN:
                # send ACK to FIN and break
                fin_ack = PHASE5_PACKET(
                    seq=0, ack=pkt.seq + 1, flags=FLAG_ACK, wnd=self.rwnd
                )
                self.send_packet(fin_ack)
                break

            if pkt.flags & FLAG_DATA:
                if pkt.seq == self.expected_seq:
                    self.received_payloads.append(pkt.payload)
                    self.expected_seq += 1
                # else out-of-order → just ignore payload
                # send cumulative ACK for last in-order seq
                ack_pkt = PHASE5_PACKET(
                    seq=0, ack=self.expected_seq, flags=FLAG_ACK, wnd=self.rwnd
                )
                self.send_packet(ack_pkt)

        self.write_image()
        self.sock.close()
