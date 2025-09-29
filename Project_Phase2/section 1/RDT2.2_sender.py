"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 2 - Section 1

    RDT2.2_sender.py

"""
## Imports
from socket import *
import struct
import sys
from pathlib import Path

## Sender Class
class RDT22_Sender:
    def __init__(self, pic_path):
        # Server info, create client socket
        self.server_name = 'localhost'
        self.server_port = 12000
        self.client_socket = socket(AF_INET, SOCK_DGRAM)

        # Class Vars
        self.pic_path = pic_path

    def make_packets(self):
        ''' 
        Breaks down image file into 1024 bytes chunks
        '''
        chunk_size = 1024
        self.all_chunks = []
        with open(self.pic_path, "rb") as f:
            file_data = f.read()
        for i in range(0, len(file_data), chunk_size):
            chunk = file_data[i:i+chunk_size]
            self.all_chunks.append(chunk)

        return self.all_chunks

## Main - Send JPEG image
if __name__ == "__main__":
    pass