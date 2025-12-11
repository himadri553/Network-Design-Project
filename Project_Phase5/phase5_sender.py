"""

"""
import socket
import struct
import zlib
from PIL import Image
from packet5 import PHASE5_PACKET

class SENDER5:
    def __init__(self, plotter):
        """ Handles inital connection """
        # Class variables
        self.plotter = plotter

        # Setup UDP Connection for sending and reciving
        self.receiver_ip="127.0.0.1"
        self.receiver_port=12000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1) # 1 Sec

        # TCP variables
        self.seq = 0
        self.ack = 0
        self.cwnd = 1
        self.ssthresh = 64
        self.timer = None

        # Sliding window feature variables **
        self.window_size = 5
        self.base = 1
        self.nextseqnum = 1

    def tcp_send_pk(self, seq, ack, flag, length=0, checksum=0, payload=b""):
        """ Use this to send packet over UPD to reciver """
        # Convert flag into bytes
        flag_byte = 0
        if "SYN" in flag: flag_byte |= 0b001
        if "ACK" in flag: flag_byte |= 0b010
        if "FIN" in flag: flag_byte |= 0b100

        # Create a packet and send it
        my_packet = PHASE5_PACKET(seq, ack, flag_byte, length, checksum, payload)
        self.sock.sendto(my_packet.pack(), (self.receiver_ip, self.receiver_port))

    def run_tx(self, img_in_chunks, secnario_num=0):
        """ Transmits one file based on secnario_data """
        self.img_in_chunks = img_in_chunks
        
        print("Running Secnario Number:", secnario_num)
        if secnario_num == 0:
            print("Testing mode")
            self.secnario_0_testing()

    """ Each secnario split into diffrent methods """
    def secnario_0_testing(self):
        ### TEsting stuff - Just send some image data to be constructed
        print("(TESTING) TX: Sending some chunks")
        self.tcp_send_pk(seq=1, ack=0, flag='DATA', payload=self.img_in_chunks[1])
        self.tcp_send_pk(seq=2, ack=0, flag='DATA', payload=self.img_in_chunks[2])
        self.tcp_send_pk(seq=3, ack=0, flag='DATA', payload=self.img_in_chunks[3])
        self.tcp_send_pk(seq=4, ack=0, flag='DATA', payload=self.img_in_chunks[4])
        self.tcp_send_pk(seq=5, ack=0, flag='FIN')