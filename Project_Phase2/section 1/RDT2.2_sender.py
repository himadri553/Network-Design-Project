"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 2 - Section 1

    RDT2.2_sender.py

"""
## Imports
from socket import *
import os
import struct
import sys
from pathlib import Path
import time
import random

## Sender Class
class RDT22_Sender:
    def __init__(self, pic_path, server_name, server_port, scenario):
        # Server info, timeout, and create client socket
        self.server_name = server_name
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.settimeout(1) # 1s
        print("The RDT2.2 sender is ready!")

        # Init protocol vars
        self.seq = 0
        self.ack = 0

        # Class Vars
        self.pic_path = pic_path
        self.scenario = scenario

    def get_all_chunks(self):
        """ Split the whole file into 1024 bit chunks """
        chunk_size = 1024
        all_chunks = []
        with open(self.pic_path, "rb") as f:
            file_data = f.read()
        for i in range(0, len(file_data), chunk_size):
            chunk = file_data[i:i+chunk_size]  
            all_chunks.append(chunk)

        return all_chunks

    def calc_checksum(self, chunk):
        """ Get checksum of the chunk """
        # if chunk length is odd, add 0 byte to make it even
        if len(chunk) % 2 != 0:
            chunk += b'\x00'
        checksum_sum = 0

        # Add all 16 bit words
        for i in range(0, len(chunk), 2):
            word = (chunk[i] << 8) + chunk[i + 1]  # Big endian
            checksum_sum += word

        # Wrap overflow
        while checksum_sum > 0xFFFF:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)

        # Ones complement and 16 bit mask
        checksum = ~checksum_sum & 0xFFFF

        return checksum

    def make_packet(self, chunk, checksum):
        """ 
        Make a packet to send over UDP
        Packet Format:
        seq (1 byte) | checksum (2 bytes) | data (up to 1024 bytes)
        """
        # Pack seq and checksum to header
        seq_bytes = struct.pack('!B', self.seq)
        checksum_bytes = struct.pack('!H', checksum)

        # Combine into one packet
        packet = seq_bytes + checksum_bytes + chunk

        return packet

    def send_packet(self, packet):
        """ Send one packet """
        self.client_socket.sendto(packet, (self.server_name, self.server_port))
        return

    def send_full_file(self):
        """ Main running method to be called in main """
        # Start time for plotting
        start_time = time.time()
        
        # Itirate thru all chunks, for one chunk
        all_chunks = self.get_all_chunks()
        for current_chunk in all_chunks:
            # Prepare a packet
            checksum = self.calc_checksum(current_chunk)
            current_packet = self.make_packet(current_chunk, checksum)
            
            # Stop and wait loop
            while True:
                # Send packet and wait for ACK from reciver (until timeout)
                self.send_packet(current_packet)
                
                try:
                    # Get ACK number from message from socket**
                    ack_msg, _ = self.client_socket.recvfrom(2048)
                    ack_number = int(ack_msg.decode())

                    # Scenario 2: Inject bit error into ACK at sender side (1 in 5 ACKs)
                    if self.scenario == "2":
                        if random.random() < 0.2:
                            print(f"[Scenario 2] Injecting bit error into ACK: {ack_number} to {ack_number ^ 1}")
                            ack_number ^= 1

                    # Check that ACK number matches the right sequence number
                    if ack_number == self.seq:
                        # Flip seq number for next packet and go to next chunk
                        self.seq = 1 - self.seq
                        break 

                    else:
                        # Resend packet if it doesnt match
                        self.send_packet(current_packet)
                
                # No ACK recived, resend packet
                except timeout: 
                    self.send_packet(current_packet)
                    print("Timed out, resent packet")
                    continue
        
        # Send END message after all chunks are sent
        self.client_socket.sendto(b"END", (self.server_name, self.server_port))
        print("Full fle sent")

        # End time a for plotting
        end_time = time.time()
        duration = end_time - start_time
        with open("Project_Phase2/sender_completion_time.txt", "w") as f:
            f.write(f"{duration:.4f}")

## Main - Send JPEG image
if __name__ == "__main__":
    # User prompts for secnarios
    print("Select scenario to run:")
    print("1 - No loss/bit errors")
    print("2 - Inject bit error into ACK packet (Sender)")
    print("3 - Inject bit error into DATA packet (Receiver)")
    scenario = input("Enter option number (1/2/3): ").strip()

    if scenario not in ["1", "2", "3"]:
        print("Invalid option. Exiting.")
        sys.exit(1)

    

    my_pic = os.path.join("Project_Phase2", "test_img.JPG")
    my_sender = RDT22_Sender(my_pic, 'localhost', 12000, scenario)
    my_sender.send_full_file()