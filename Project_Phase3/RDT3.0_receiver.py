"""
Nour Fahmy, Himadri Saha

EECE 4830 - Network Design
Programming Project Phase 3

RDT3.0_receiver.py

Based on the Phase 2 receiver. Adds DATA-packet loss simulation (Scenario 5)
and keeps behavior for data-bit-error injection (Scenario 3).
Writes received file to Project_Phase3/received.jpg
"""

from socket import *
import struct
import os
import time
import random

class RDT30_Receiver:
    def __init__(self):
        # Destination path
        self.dest_filepath = os.path.join("Project_Phase3", "received.jpg")
        os.makedirs(os.path.dirname(self.dest_filepath), exist_ok=True)

        # UDP server socket
        self.server_port = 12000
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))
        print("RDT3.0 receiver ready on port", self.server_port)

        # Expected sequence number
        self.expected_seq = 0

        # Open output file
        self.file = open(self.dest_filepath, "wb")

        # Read scenario and loss_rate
        self.scenario, self.loss_rate = self._read_scenario_file()

        # Retry limits (keeps behavior from Phase2/2.2)
        self.retry_counter = {0: 0, 1: 0}
        self.max_retries = 5

    def _read_scenario_file(self):
        scenario_path = os.path.join("Project_Phase3", "scenario_mode.txt")
        scenario = 1          # default scenario as integer
        loss_rate = 0.2       # default 20%
        if os.path.exists(scenario_path):
            with open(scenario_path, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip() != ""]
            if len(lines) >= 1:
                try:
                    scenario = int(lines[0])   # convert to int
                except:
                    pass
            if len(lines) >= 2:
                try:
                    loss_rate = float(lines[1])
                except:
                    pass
        return scenario, loss_rate

    def calc_checksum(self, data: bytes) -> int:
        if len(data) % 2 != 0:
            data += b'\x00'
        checksum_sum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            checksum_sum += word
        while checksum_sum > 0xFFFF:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
        return (~checksum_sum) & 0xFFFF

    def run_receiver(self):
        start_time = time.time()
        print(f"Running receiver in Scenario {self.scenario} (loss_rate={self.loss_rate})")
        print("Receiver started, waiting for packets...")

        while True:
            packet, client_address = self.server_socket.recvfrom(2048)

            # End marker
            if packet == b"END":
                print("File transfer complete.")
                self.file.close()
                duration = time.time() - start_time
                with open("Project_Phase3/receiver_completion_time.txt", "w") as f:
                    f.write(f"{duration:.4f}")
                break

            if len(packet) < 3:
                print("Packet too short; ignoring.")
                continue

            seq_num = struct.unpack('!B', packet[0:1])[0]
            recv_checksum = struct.unpack('!H', packet[1:3])[0]
            data = packet[3:]

            # Scenario 5: Simulate DATA packet loss
            if self.scenario == 5 and random.random() < self.loss_rate:
                print(f"[Scenario 5] Simulating DATA loss for seq {seq_num} (dropped)")
                continue

            # Scenario 3: Inject bit error into data
            if self.scenario == 3 and random.random() < self.loss_rate:
                print(f"[Scenario 3] Injecting bit error into DATA packet seq {seq_num}")
                if len(data) > 0:
                    corrupted_byte = bytes([data[0] ^ 0b00000001])
                    data = corrupted_byte + data[1:]

            calc_cksum = self.calc_checksum(data)

            if calc_cksum == recv_checksum and seq_num == self.expected_seq:
                # Good packet
                self.file.write(data)
                print(f"Received valid packet seq {seq_num} - writing and ACKing")
                self.server_socket.sendto(str(seq_num).encode(), client_address)
                self.expected_seq = 1 - self.expected_seq
                self.retry_counter[seq_num] = 0
            else:
                # Corrupt or out-of-order packet
                self.retry_counter[seq_num] += 1
                print(f"[Retry] Rejected packet seq {seq_num} ({self.retry_counter[seq_num]} rejects)")

                if self.retry_counter[seq_num] >= self.max_retries:
                    print(f"[WARN] Too many rejects for seq {seq_num}, forcing acceptance")
                    self.file.write(data)
                    self.server_socket.sendto(str(seq_num).encode(), client_address)
                    self.expected_seq = 1 - self.expected_seq
                    self.retry_counter[seq_num] = 0
                else:
                    last_ack = 1 - self.expected_seq
                    print(f"Resending last ACK = {last_ack}")
                    self.server_socket.sendto(str(last_ack).encode(), client_address)


if __name__ == "__main__":
    recv = RDT30_Receiver()  # no arguments here
    recv.run_receiver()       # call the correct method
