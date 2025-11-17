"""
    Nour Fahmy, Himadri Saha 

    reciver_phase4.py
    - Implementation of Go-Back-N reciver
    

"""
# GBN_Receiver.py
import socket

class GBN_Receiver:
    def __init__(self, listen_port, scenario=1):
        self.listen_port = listen_port
        self.scenario = scenario
        self.expected_seqnum = 1
        self.received_data = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', listen_port))

        print(f"[RECEIVER] Listening on port {listen_port}...")

    # ------------------------------------------------------------------
    def udt_send(self, packet, addr):
        self.sock.sendto(packet, addr)

    # ------------------------------------------------------------------
    def run_receiver(self):
        """Main GBN receiver loop."""
        print("[RECEIVER] Waiting for file...")

        while True:
            packet, addr = self.sock.recvfrom(2048)

            try:
                sep = packet.index(b'|')
            except:
                continue

            seq = int(packet[:sep])
            payload = packet[sep+1:]

            if seq == self.expected_seqnum:
                self.received_data.append(payload)
                ack = str(self.expected_seqnum).encode()
                self.udt_send(ack, addr)
                self.expected_seqnum += 1

            else:
                # Resend last ACK
                last_good = self.expected_seqnum - 1
                ack = str(last_good).encode()
                self.udt_send(ack, addr)

            # End condition (optional)
            if len(payload) == 0:
                break

        print("[RECEIVER] File reception complete.")
        return b''.join(self.received_data)