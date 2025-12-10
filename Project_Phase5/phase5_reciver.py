"""

"""
import socket
import struct
import traceback
import zlib

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

        # Extract Variables
        self.plotter = plotter

    def run_rx(self):
        """ Handles reciver behavior """
        print("Reciver ready")

        ## Testing stuff
        # Extract and print out what was recived with the headers
        while True:
            packet, addr = self.sock.recvfrom(2048)
            print("Got packet")

            header_size = struct.calcsize("!IIBHI")
            seq, ack, flag_byte, length, checksum = struct.unpack("!IIBHI", packet[:header_size])
            payload = packet[header_size: header_size + length]
            temp_header = struct.pack("!IIBHI", seq, ack, flag_byte, length, 0)
            computed = zlib.crc32(temp_header + payload) & 0xffffffff
            valid = (computed == checksum)
            flags = []
            if flag_byte & 0b001: flags.append("SYN")
            if flag_byte & 0b010: flags.append("ACK")
            if flag_byte & 0b100: flags.append("FIN")

            print("----- RECEIVED SEGMENT -----")
            print("addr: ", addr)
            print("SEQ: ", seq)
            print("ACK: ", seq)
            print("FLAGS: ", flags)
            print("LENGTH: ", length)
            print("CHECKSUM: ", checksum)
            print("PAYLOAD (raw): ", payload)

        # Run state machine