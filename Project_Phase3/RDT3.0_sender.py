"""
Nour Fahmy, Himadri Saha
EECE 4830 - Network Design
Programming Project Phase 3
RDT3.0_sender.py

Implements sender-side RDT3.0 features:
 - Timeout-based retransmission (stop-and-wait)
 - Simulated ACK bit-errors (Scenario 2) and ACK loss (Scenario 4)
 - Works with the RDT3.0_receiver above

"""

from socket import *
import struct
import os
import sys
import time
import random

class RDT30_Sender:
    def __init__(self, pic_path, server_name='localhost', server_port=12000):
        self.server_name = server_name
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.settimeout(0.5)  # 500 ms timeout (recommended 300-500ms)
        print("RDT3.0 sender ready (timeout=0.05s)")

        self.seq = 0  # current sequence number

        self.pic_path = pic_path
        self.scenario, self.loss_rate = self._read_scenario_file()

    def _read_scenario_file(self):
        scenario_path = os.path.join("Project_Phase3", "scenario_mode.txt")
        scenario = "1"
        loss_rate = 0.2
        if os.path.exists(scenario_path):
            with open(scenario_path, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip() != ""]
            if len(lines) >= 1:
                scenario = lines[0]
            if len(lines) >= 2:
                try:
                    loss_rate = float(lines[1])
                except:
                    pass
        return scenario, loss_rate

    def get_all_chunks(self):
        chunk_size = 1024
        all_chunks = []
        with open(self.pic_path, "rb") as f:
            file_data = f.read()
        for i in range(0, len(file_data), chunk_size):
            all_chunks.append(file_data[i:i+chunk_size])
        return all_chunks

    def calc_checksum(self, chunk: bytes) -> int:
        if len(chunk) % 2 != 0:
            chunk += b'\x00'
        checksum_sum = 0
        for i in range(0, len(chunk), 2):
            word = (chunk[i] << 8) + chunk[i+1]
            checksum_sum += word
        while checksum_sum > 0xFFFF:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
        return (~checksum_sum) & 0xFFFF

    def make_packet(self, chunk: bytes, checksum: int) -> bytes:
        seq_bytes = struct.pack('!B', self.seq)
        checksum_bytes = struct.pack('!H', checksum)
        return seq_bytes + checksum_bytes + chunk

    def send_full_file(self):
        start_time = time.time()
        all_chunks = self.get_all_chunks()
        print(f"Sending {len(all_chunks)} chunks in Scenario {self.scenario} (loss_rate={self.loss_rate})")

        for chunk_idx, chunk in enumerate(all_chunks):
            checksum = self.calc_checksum(chunk)
            packet = self.make_packet(chunk, checksum)

            while True:
                # Send the packet
                self.client_socket.sendto(packet, (self.server_name, self.server_port))

                try:
                    ack_msg, _ = self.client_socket.recvfrom(2048)
                    # Scenario 4: Simulate ACK loss at sender by pretending we didn't receive it
                    if self.scenario == "4" and random.random() < self.loss_rate:
                        print(f"[Scenario 4] Simulating ACK loss: ignoring incoming ACK '{ack_msg.decode()}'")
                        # Treat as if timeout occurred: continue waiting/retransmit
                        # We simply go to next iteration of while (which will retransmit)
                        continue

                    ack_number = int(ack_msg.decode())

                    # Scenario 2: Inject ACK bit-error (flip ack) with probability loss_rate
                    if self.scenario == "2" and random.random() < self.loss_rate:
                        print(f"[Scenario 2] Injecting ACK bit-error: {ack_number} -> {ack_number ^ 1}")
                        ack_number ^= 1

                    if ack_number == self.seq:
                        # Correct ACK; move on
                        print(f"Received ACK {ack_number} for seq {self.seq} (chunk {chunk_idx+1}/{len(all_chunks)})")
                        self.seq = 1 - self.seq
                        break
                    else:
                        # Duplicate or wrong ACK: resend
                        print(f"Received wrong ACK {ack_number} (expected {self.seq}); retransmitting")
                        # loop continues -> retransmit

                except timeout:
                    # No ACK received in timeout window: retransmit
                    print("Timeout waiting for ACK; retransmitting")
                    continue

        # After all chunks sent, send END marker
        self.client_socket.sendto(b"END", (self.server_name, self.server_port))
        print("Full file sent (END transmitted)")
        duration = time.time() - start_time
        # Save completion time to a file for plots if desired
        with open("Project_Phase3/sender_completion_time.txt", "w") as f:
            f.write(f"{duration:.4f}")

if __name__ == "__main__":
    # Prepare scenario file existence check
    scenario_path = os.path.join("Project_Phase3", "scenario_mode.txt")
    if not os.path.exists(scenario_path):
        print("No scenario_mode.txt found under Project_Phase3. Defaulting to scenario 1 with 20% loss rate.")
        # create a default file for convenience
        os.makedirs("Project_Phase3", exist_ok=True)
        with open(scenario_path, "w") as f:
            f.write("1\n0.2\n")

    image_path = "test_img.JPG"
    if not os.path.exists(image_path):
        print(f"Test image not found at {image_path}. Please add a file named 'test_img.JPG' under Project_Phase3 and rerun.")
        sys.exit(1)

    sender = RDT30_Sender("test_img.JPG", server_name="localhost", server_port=12000)
