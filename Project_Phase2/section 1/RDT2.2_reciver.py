"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 2 - Section 1

    RDT2.2_receiver.py

    Scenario 2 Implementation:
        When data bits of ACK packets are changed by sender (stop-and-wait):
         - dectes wrong seq number
         - resends last ACK number
         - Does not rewrite data

    Scenario 3 Implementation: 
        When the data bits of the received DATA packet are changed by the receiver, 
        - reciver will detect mismatch
        - ignore data and not write to file
        - resends the last ACK message
        To ensure there is no infinite loop in scenario 3:
        - reciver will retry a max of 5 times

"""
## Imports
from socket import *
import struct
import os
import time
import random

## Receiver Class
class RDT22_Reciver:
    def __init__(self, scenario="1"):
        # Set output file path
        self.dest_filepath = os.path.join("Project_Phase2",  "received.jpg")
        os.makedirs(os.path.dirname(self.dest_filepath), exist_ok=True)

        # Create and bind server socket to start server
        self.server_port = 12000
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))
        print("The RDT2.2 receiver is ready!")

        # Expected sequence number
        self.expected_seq = 0

        # Open file for writing binary
        self.file = open(self.dest_filepath, "wb")

        # Vars
        self.scenario = scenario

    def calc_checksum(self, data):
        """ Compute 16-bit checksum of given data """
        if len(data) % 2 != 0:
            data += b'\x00'
        checksum_sum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum_sum += word
        while checksum_sum > 0xFFFF:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
        return ~checksum_sum & 0xFFFF

    def run_receiver(self):
        """ Main loop to receive and process packets """
        # Start time for plotting
        start_time = time.time()

        # init for max retries
        self.retry_counter = {0: 0, 1: 0}
        self.max_retries = 5

        while True:
            packet, client_address = self.server_socket.recvfrom(2048)

            # Check for end of file
            if packet == b"END":
                print("File transfer complete.")
                self.file.close()

                # End time for plotting
                end_time = time.time()
                duration = end_time - start_time
                with open("Project_Phase2/receiver_completion_time.txt", "w") as f:
                    f.write(f"{duration:.4f}")

                break

            # Parse packet: seq (1 byte), checksum (2 bytes), data (rest)
            if len(packet) < 3:
                print("Packet too short. Ignoring.")
                continue
            
            # Unpack Packet
            seq_num = struct.unpack('!B', packet[0:1])[0]
            recv_checksum = struct.unpack('!H', packet[1:3])[0]
            data = packet[3:]

            # For scenario 3: Inject bit error into received DATA packet by flippin least significant bit (20% of the time)
            if self.scenario == "3" and random.random() < 0.2:
                print(f"[Scenario 3] Injecting bit error into DATA packet with seq {seq_num}")
                if len(data) > 0:
                    corrupted_byte = bytes([data[0] ^ 0b00000001])  # Flip least significant bit
                    data = corrupted_byte + data[1:]

            # Recalculate checksum
            calc_checksum = self.calc_checksum(data)

            if calc_checksum == recv_checksum and seq_num == self.expected_seq:
                # Valid packet: write and ACK
                self.file.write(data)
                print(f"Received valid packet with seq {seq_num}")
                self.server_socket.sendto(str(seq_num).encode(), client_address)
                self.expected_seq = 1 - self.expected_seq  # Flip expected sequence
            else:
                # Track retrys
                self.retry_counter[seq_num] += 1
                print(f"[Retry] Packet with seq {seq_num} rejected {self.retry_counter[seq_num]} time(s)")

                if self.retry_counter[seq_num] >= self.max_retries:
                    print(f"[WARN] Too many failed attempts for seq {seq_num}. Forcing acceptance.")

                    # Force accept to break loop (optional for demo)
                    self.file.write(data)
                    self.server_socket.sendto(str(seq_num).encode(), client_address)
                    self.expected_seq = 1 - self.expected_seq
                    self.retry_counter[seq_num] = 0  # Reset after acceptance
                else:
                    # Normal recovery: resend last ACK
                    last_ack = 1 - self.expected_seq
                    self.server_socket.sendto(str(last_ack).encode(), client_address)

## Main
if __name__ == "__main__":
    # Check if its scenario 3 otherwise its just 1 
    scenario_file_path = os.path.join("Project_Phase2", "scenario_mode.txt")
    if os.path.exists(scenario_file_path):
        with open(scenario_file_path, "r") as f:
            scenario = f.read().strip()

    # Run receiver
    my_receiver = RDT22_Reciver(scenario)
    print(f"Receiver running in Scenario {scenario}")
    my_receiver.run_receiver()