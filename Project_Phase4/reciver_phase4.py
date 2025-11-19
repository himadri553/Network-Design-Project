"""
    Nour Fahmy, Himadri Saha 

    reciver_phase4.py:
    - Go-Back-N Receiver with loss/bit-error injection for plotting experiments.
"""

import socket
import random

class GBN_Receiver:
    def __init__(self, listen_port, scenario=1, loss_prob=0.0):
        self.listen_port = listen_port
        self.scenario = scenario
        self.loss_prob = loss_prob

        self.expected_seqnum = 1
        self.received_data = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", listen_port))


    # -------------- LOSS / ERROR SIMULATION --------------

    def maybe_drop_data(self):
        """Scenario 5: randomly drop DATA packet completely."""
        if self.scenario == 5:
            return random.random() < self.loss_prob
        return False

    def maybe_corrupt_data(self, payload):
        """Scenario 3: corrupt payload bits randomly."""
        if self.scenario == 3 and random.random() < self.loss_prob:
            # Corrupt by flipping a byte
            if len(payload) > 0:
                corrupt_index = random.randint(0, len(payload) - 1)
                bad_byte = (payload[corrupt_index] + 1) % 256
                payload = payload[:corrupt_index] + bytes([bad_byte]) + payload[corrupt_index+1:]
        return payload

    # -------------- SEND ACK --------------

    def udt_send(self, packet, addr):
        self.sock.sendto(packet, addr)

    # -------------- MAIN RECEIVE LOOP --------------

    def run_receiver(self):
        while True:
            packet, addr = self.sock.recvfrom(2048)

            # Split seq | payload
            try:
                sep = packet.index(b"|")
            except ValueError:
                continue

            seq = int(packet[:sep])
            payload = packet[sep+1:]

            # Scenario 5 — DATA loss (drop packet just like IP layer)
            if self.maybe_drop_data():
                # resend previous ack
                last_good = self.expected_seqnum - 1
                ack = str(last_good).encode()
                self.udt_send(ack, addr)
                continue

            # Scenario 3 — DATA bit errors
            payload = self.maybe_corrupt_data(payload)

            # GBN Logic
            if seq == self.expected_seqnum:
                # SUCCESS
                self.received_data.append(payload)
                ack = str(self.expected_seqnum).encode()
                self.udt_send(ack, addr)
                self.expected_seqnum += 1

            else:
                # OUT-OF-ORDER → resend last ACK
                last_good = self.expected_seqnum - 1
                ack = str(last_good).encode()
                self.udt_send(ack, addr)

            # Optional stop condition — file transfer ends when 0-byte chunk appears
            if len(payload) == 0:
                break

        return b"".join(self.received_data)
