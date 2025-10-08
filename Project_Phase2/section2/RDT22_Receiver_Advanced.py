"""
Author: Nour Fouad Fahmy
EECE 4830 - Network Design
Programming Project Phase 2 - Section II
RDT22_Receiver_Advanced.py

Implements RDT 2.2 Receiver w/ extra credit:
 - CRC-16 Error Detection
 - Random Packet Delay
 - Multi-threading (Receive + ACK)
 - Logging and Performance Tracking
"""

import socket
import threading
import time
import struct
import random
import os
from datetime import datetime

class RDT22_Receiver_Advanced:
    def __init__(self, port=12000, out_file="Project_Phase2/section2/received_advanced.jpg"):
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))
        print(f"[Receiver] Listening on port {self.server_port}...")

        self.expected_seq = 0
        self.out_file = out_file
        self.file = open(self.out_file, "wb")

        # Logging
        self.log_file = open("Project_Phase2/section2/log.txt", "w")
        self.log(f"Receiver started at {datetime.now()}")
        
        # Thread control
        self.running = True
        self.lock = threading.Lock()

        # Statistics
        self.total_packets = 0
        self.corrupted_packets = 0
        self.retransmissions = 0
        self.start_time = time.time()

    # CRC-16 Calculation (0x8005 polynomial)
    def crc16(self, data: bytes, poly=0x8005):
        crc = 0x0000
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) & 0xFFFF) ^ poly
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc & 0xFFFF

    def log(self, msg):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"
        self.log_file.write(line)
        self.log_file.flush()
        print(line, end="")

    def simulate_delay(self):
        """Simulate network delay (0–500 ms)"""
        delay = random.randint(0, 500) / 1000.0
        time.sleep(delay)
    
    def calc_checksum(self, data):
        """Compute 16-bit checksum (same as Himadri's sender)."""
        if len(data) % 2 != 0:
            data += b'\x00'
        checksum_sum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum_sum += word
        while checksum_sum > 0xFFFF:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
        return ~checksum_sum & 0xFFFF


    def process_packet(self, packet, client_address):
        """Handle each received packet according to RDT 2.2 logic."""
        if packet == b"END":
            self.log("End of file received. Closing receiver.")
            self.file.close()
            self.running = False
            return

        if len(packet) < 3:
            self.log("Received invalid packet (too short).")
            return

        seq_num = struct.unpack('!B', packet[0:1])[0]
        recv_checksum = struct.unpack('!H', packet[1:3])[0]
        data = packet[3:]

        # Introduce random processing delay
        self.simulate_delay()

        # Calculate CRC-16 on data
        calc_checksum = self.calc_checksum(data)


        self.total_packets += 1

        # Check corruption and sequence correctness
        if calc_checksum == recv_checksum and seq_num == self.expected_seq:
            self.file.write(data)
            self.log(f"✅ Packet {seq_num} received correctly.")
            self.expected_seq = 1 - self.expected_seq
            ack = str(seq_num).encode()
            self.server_socket.sendto(ack, client_address)
        else:
            self.corrupted_packets += 1
            self.retransmissions += 1
            self.log(f"❌ Packet corrupted or unexpected seq (Got: {seq_num}, Expected: {self.expected_seq}). Resending last ACK.")
            last_ack = str(1 - self.expected_seq).encode()
            self.server_socket.sendto(last_ack, client_address)

    def receiver_thread(self):
        """Main thread for listening and processing packets."""
        while self.running:
            try:
                packet, client_address = self.server_socket.recvfrom(2048)
                threading.Thread(target=self.process_packet, args=(packet, client_address)).start()
            except Exception as e:
                self.log(f"Error: {e}")
                continue

    def run(self):
        """Run the receiver with multi-threading."""
        t = threading.Thread(target=self.receiver_thread)
        t.start()

        while self.running:
            time.sleep(0.1)

        elapsed = time.time() - self.start_time
        self.log(f"\n--- Transfer Stats ---\n"
                 f"Total Packets: {self.total_packets}\n"
                 f"Corrupted Packets: {self.corrupted_packets}\n"
                 f"Retransmissions: {self.retransmissions}\n"
                 f"Completion Time: {elapsed:.2f}s\n")
        self.log_file.close()
        print("Receiver terminated successfully.")
