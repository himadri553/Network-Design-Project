"""

"""
import socket
import struct
import zlib

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

    def tcp_send(self, seq, ack, flags, payload=b""):
        """ 
        Builds and sends a TCP packet with the headers:
        - seq
        - ack
        - flags
        - lenght
        - checksum
        - payload 
        """
        # Set flag bytes
        flag_byte = 0
        if "SYN" in flags: flag_byte |= 0b001
        if "ACK" in flags: flag_byte |= 0b010
        if "FIN" in flags: flag_byte |= 0b100
        length = len(payload)

        # Get checksum and build final header
        header = struct.pack("!IIBHI", seq, ack, flag_byte, length, 0)
        checksum = zlib.crc32(header + payload) & 0xffffffff
        header = struct.pack("!IIBHI", seq, ack, flag_byte, length, checksum)

        # Send segment
        segment = header + payload
        self.sock.sendto(segment, (self.receiver_ip, self.receiver_port))

    def run_tx(self, img_in_chunks, secnario_num=0):
        """ Transmits one file based on secnario_data """
        print("Running Secnario Number:", secnario_num)

        ### TEsting stuff
        if secnario_num == 0:
            print("Testing mode")

        self.tcp_send(seq=1, ack=0, flags="SYN")
        print("sent SYN packet")

        # Assign all self. variables based on yaml file (temp values for now)

        ## Run state machine ##
        # Send SYN, wait for SYN-ACK, then send ACK


        # Send data packet, , unless timeout


