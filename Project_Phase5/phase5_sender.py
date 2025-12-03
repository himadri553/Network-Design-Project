"""

"""
import socket
import random

class SENDER5:
    def __init__(self, plotter):
        """ Handles inital connection """
        # Setup UDP Connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.01)

    def run_tx(self, secnario_num, image_path):
        """ Run secnario """
        print("Running secnario", secnario_num)
        