"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 2 - Section 1

    RDT2.2_reciver.py

"""
## Imports
from socket import *
import struct
import sys
from pathlib import Path
import os

## Vars

## Receiver Class
class RDT22_Reciver:
    def __init__(self):
        # Set output file path
        self.dest_filepath = os.path.join("Project_Phase2", "section1", "received.jpg")

        # Create and bind server socket to start server
        self.server_port = 12000
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))
        print("The RDT2.2 reciver is ready")

    def rx_send():
        pass

## Main
if __name__ == "__main__":
    pass