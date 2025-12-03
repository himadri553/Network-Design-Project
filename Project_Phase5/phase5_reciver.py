"""

"""
import socket
import time
import random
import traceback

class RECIVER5:
    def __init__(self, plotter):
        """ Handles inital connection """
        # Set up UDP connection
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("", 12000))
            print("UDP connection succesful! Starting reciver")
            self.run_rx()
        except Exception:
            print("Failed to connect to UDP sender: ")
            traceback.print_exc()

        # Extract Variables
        self.plotter = plotter

    def run_rx(self, secnario_num):
        print("Reciver ready")
        """ Run secnario """
        # Based on secnario_num, init variables switch case

        pass