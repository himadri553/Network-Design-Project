"""
    Nour Fahmy, Himadri Saha 

    packet_phase4.py:
    Contains the packet class that will be used in project phase 4. 
    Includes functions for breaking file into packets with approiate packet tags.
    To be called by main and sender to send the correct packet to the reciver
    Breaks down a BMP image into 1024 bytes (can be changed as well)

    TODO:
    - Check if the packet sending format is right
    - 

"""
## Imports
from socket import *
import os
import struct
import sys
from pathlib import Path
import time
import random

# Vars
chunk_size = 1024

## Packet Class
class GBN_Packet:
    def __init__(self, pic_path):
        self.pic_path = pic_path

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
        """ Get checksum of a chunk """
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

    def make_a_packet(self, chunk):
        """ 
        Make a packet
        Packet Format:
        seq (1 byte) | checksum (2 bytes) | data (up to 1024 bytes)
        """
        # Pack seq and checksum to header
        seq_bytes = struct.pack('!B', self.seq)
        checksum_bytes = struct.pack('!H', self.calc_checksum(chunk))

        # Combine into one packet
        packet = seq_bytes + checksum_bytes + chunk

        return packet

    def get_next_packet(self):
        """ Called by the sender to get next pakcet. Dont use this function if a resend is needed!"""
        # Get all chunks (if not already initalized)
        if not hasattr(self, "all_chunks"):
            self.all_chunks = self.get_all_chunks()

        # Initalize chunk counter. Return none when finished
        if not hasattr(self, "current_index"):
            self.current_index = 0
        if self.current_index >= len(self.all_chunks):
            return None
        
        # Get next chunk and prepare a packet

        # Mark this packet as the last packet sent and return it

    def get_last_packet(self):
        """ Give sender the last packet sent for resending """
        # Return last packet sent