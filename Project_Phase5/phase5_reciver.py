"""

"""
import socket
import struct
import traceback
import zlib
from PIL import Image
import os
from packet5 import PHASE5_PACKET

class RECIVER5:
    def __init__(self, plotter):
        """ Handles inital connection """
        # Set up UDP connection
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("", 12000))
            print("UDP connection succesful! Starting reciver")
        except Exception:
            print("Failed to connect to UDP sender: ")
            traceback.print_exc()
            return

        # Class Variables
        self.plotter = plotter
        self.buffer_size = 2048

        # Init recive variables
        self.received_chunks = []
        self.expected_seq = 0 
        self.output_buffer = bytearray()
        self.file_complete = False

    def run_rx(self):
        """ 
        Handles reciver behavior :
        - Unpacks every packet first, and sorts all the data in self.received_chunks
        - Will also remove chunks if needed
        - THEN it will construct the full image
        
        """ 
        
        print("RX: Reciver listening...")
        while True:
            # Extract raw packet from socket and convert back to usable data
            raw_packet, _ = self.sock.recvfrom(self.buffer_size)
            packet = PHASE5_PACKET.unpack(raw_packet) 

            # Flags are in bytes, convert them back for the reciver
            flag_char = ""
            if packet.flags == 0b001: flag_char = "SYN"
            if packet.flags == 0b010: flag_char = "ACK"
            if packet.flags == 0b100: flag_char = "FIN"

            # if recived FIN, stop listening and break to build image
            if flag_char == "FIN":
                break

            # Load paylaod data into received_chunks
            if flag_char == "DATA":
                print("RX: DATA recived, adding payload to image")
                self.received_chunks.append(packet.payload)

            ## TODO: Add the logic to determine wether to keep the chunks or nah

        #### Construct .bmp file with whatever is in received_chunks
        print("RX: Received FIN — writing final BMP file")
        dest_filepath = os.path.join("Project_Phase5", "img", "recived_img.bmp")
        if os.path.exists(dest_filepath):
            os.remove(dest_filepath)
        with open(dest_filepath, "wb") as f:
            for i in self.received_chunks:
                f.write(self.received_chunks[i])