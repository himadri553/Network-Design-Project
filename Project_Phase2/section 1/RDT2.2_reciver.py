"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 2 - Section 1

    RDT2.2_receiver.py

"""
## Imports
from socket import *
import struct
import os

## Receiver Class
class RDT22_Reciver:
    def __init__(self):
        # Set output file path
        self.dest_filepath = os.path.join("Project_Phase2", "section1", "received.jpg")
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
        while True:
            packet, client_address = self.server_socket.recvfrom(2048)

            # Check for end of file
            if packet == b"END":
                print("File transfer complete.")
                self.file.close()
                break

            # Parse packet: seq (1 byte), checksum (2 bytes), data (rest)
            if len(packet) < 3:
                print("Packet too short. Ignoring.")
                continue

            seq_num = struct.unpack('!B', packet[0:1])[0]
            recv_checksum = struct.unpack('!H', packet[1:3])[0]
            data = packet[3:]

            # Recalculate checksum
            calc_checksum = self.calc_checksum(data)

            if calc_checksum == recv_checksum and seq_num == self.expected_seq:
                # Valid packet: write and ACK
                self.file.write(data)
                print(f"Received valid packet with seq {seq_num}")
                self.server_socket.sendto(str(seq_num).encode(), client_address)
                self.expected_seq = 1 - self.expected_seq  # Flip expected sequence
            else:
                # Invalid or duplicate packet: resend last ACK
                print(f"Ignored packet - Checksum error or unexpected seq (Expected: {self.expected_seq}, Got: {seq_num})")
                last_ack = 1 - self.expected_seq  # Send last correct ack
                self.server_socket.sendto(str(last_ack).encode(), client_address)

## Main
if __name__ == "__main__":
    my_receiver = RDT22_Reciver()
    my_receiver.run_receiver()
