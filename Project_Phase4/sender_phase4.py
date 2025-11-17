"""
    Nour Fahmy, Himadri Saha 

    sender_phase4.py:
    - Implementation of Go-Back-N sender

"""
# GBN_Sender.py
import socket
import time

class GBN_Sender:
    def __init__(self, receiver_ip, receiver_port, scenario=1, window_size=10, timeout_interval=0.05):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.window_size = window_size
        self.scenario = scenario

        # One socket for send + receive
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.01)

        print("[SENDER] Initialized.")

        # GBN variables
        self.base = 1
        self.nextseqnum = 1
        self.sndpkt = {}              # seq → packet bytes

        # Timer
        self.timer_running = False
        self.timer_start_time = None
        self.timeout_interval = timeout_interval

    # ------------------------------------------------------------------
    def start_timer(self):
        self.timer_running = True
        self.timer_start_time = time.time()

    # ------------------------------------------------------------------
    def stop_timer(self):
        self.timer_running = False
        self.timer_start_time = None

    # ------------------------------------------------------------------
    def timer_expired(self):
        if not self.timer_running:
            return False
        return (time.time() - self.timer_start_time) >= self.timeout_interval

    # ------------------------------------------------------------------
    def udt_send(self, packet):
        """Send packet unreliably (UDP)."""
        self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))

    # ------------------------------------------------------------------
    def resend_window(self):
        """On timeout: resend all unacked packets."""
        print("[SENDER] Timeout! Resending window.")
        for seq in range(self.base, self.nextseqnum):
            self.udt_send(self.sndpkt[seq])
        self.start_timer()

    # ------------------------------------------------------------------
    def run_sender(self, file_bytes):
        """
        Main GBN loop.
        file_bytes: raw image file loaded in main
        """
        CHUNK = 1024
        file_chunks = [file_bytes[i:i+CHUNK] for i in range(0, len(file_bytes), CHUNK)]

        print("[SENDER] Starting transfer...")
        total = len(file_chunks)

        while self.base <= total:

            # Send new packets while window is open
            if self.nextseqnum < self.base + self.window_size and self.nextseqnum <= total:
                payload = file_chunks[self.nextseqnum - 1]

                # Packet creation (simplified)
                packet = b'%d|' % self.nextseqnum + payload

                self.sndpkt[self.nextseqnum] = packet
                self.udt_send(packet)

                if self.base == self.nextseqnum:
                    self.start_timer()

                self.nextseqnum += 1

            # Receive ACK if available
            try:
                ackpkt, _ = self.sock.recvfrom(2048)
                acknum = int(ackpkt.decode())

                if acknum >= self.base:
                    self.base = acknum + 1
                    if self.base == self.nextseqnum:
                        self.stop_timer()
                    else:
                        self.start_timer()

            except socket.timeout:
                pass

            # Timer expiration
            if self.timer_expired():
                self.resend_window()

        print("[SENDER] File transfer completed.")