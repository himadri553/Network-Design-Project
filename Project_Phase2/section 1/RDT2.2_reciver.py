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

## Receiver Class
class RDT22_Reciver:
    def __init__(self):
        # Set output file path
        self.dest_filepath = os.path.join("Project_Phase2", "section1", "received.jpg")

        # Create and bind server socket to start server
        self.server_port = 12000
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('', self.server_port))
        print("The RDT2.2 reciver is ready!")

    def recive_message(self):
        buffer_size = 2048
        client_message, _ = self.server_socket.recvfrom(buffer_size)

        return client_message

    def test_get_message(self):
        """ Testing if connection between sender and reciver is working... """
        while True:
            test_message = self.recive_message()
            print("Got chunk from sender")

            # Until end message is read
            if test_message == b"END":
                print("File transfer done")
                break

        return test_message

## Main
if __name__ == "__main__":
    my_reciver = RDT22_Reciver()
    my_reciver.test_get_message()
    