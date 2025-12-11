"""
    Represents one packet. 
    Sender will use pack function to convert data into raw bytes to be sent over UDP
    Reciver will use unpack to convert raw bytes back to useable data
"""
import struct
import zlib

# Simple TCP-like segment:
# seq (I), ack (I), flags (B), wnd (H), length (H), checksum (I), payload (variable)
HEADER_FORMAT = "!IIBHHI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

FLAG_SYN = 0b0001
FLAG_ACK = 0b0010
FLAG_FIN = 0b0100
FLAG_DATA = 0b1000  # custom flag for data segment


class PHASE5_PACKET:
    def __init__(self, seq, ack, flags, wnd, payload=b""):
        self.seq = seq
        self.ack = ack
        self.flags = flags
        self.wnd = wnd          # receiver window (rwnd)
        self.payload = payload or b""
        self.length = len(self.payload)
        self.checksum = 0

    def compute_checksum(self, raw):
        # Use CRC32 as a simple checksum
        return zlib.crc32(raw) & 0xffffffff

    def pack(self):
        header_wo_checksum = struct.pack(
            HEADER_FORMAT, self.seq, self.ack, self.flags,
            self.wnd, self.length, 0
        )
        raw = header_wo_checksum + self.payload
        self.checksum = self.compute_checksum(raw)

        header = struct.pack(
            HEADER_FORMAT, self.seq, self.ack, self.flags,
            self.wnd, self.length, self.checksum
        )
        return header + self.payload

    @classmethod
    def unpack(cls, raw):
        header = raw[:HEADER_SIZE]
        seq, ack, flags, wnd, length, checksum = struct.unpack(HEADER_FORMAT, header)
        payload = raw[HEADER_SIZE:HEADER_SIZE + length]

        pkt = cls(seq, ack, flags, wnd, payload)
        pkt.checksum = checksum

        # Verify checksum
        tmp_header = struct.pack(
            HEADER_FORMAT, seq, ack, flags, wnd, length, 0
        )
        calc = zlib.crc32(tmp_header + payload) & 0xffffffff
        pkt.valid = (calc == checksum)
        return pkt
