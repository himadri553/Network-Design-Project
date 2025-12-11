"""
    Represents one packet. 
    Sender will use pack function to convert data into raw bytes to be sent over UDP
    Reciver will use unpack to convert raw bytes back to useable data
"""
import struct
import zlib

class PHASE5_PACKET:
    def __init__(self, seq, ack, flags, lenght, checksum, payload):
        """ Assignes all the headers """
        self.seq = seq
        self.ack = ack
        self.flags = flags
        self.length = lenght
        self.checksum = checksum
        self.payload = payload      # The image data itself

    def pack(self):
        """ Converts all the info to raw bytes so that they can be sent, returns raw data"""
        header = struct.pack("!IIBHI", 
            self.seq,
            self.ack,
            self.flags,
            self.length,
            0  # temporary checksum
        )
        checksum = zlib.crc32(header + self.payload) & 0xffffffff

        header = struct.pack("!IIBHI", 
            self.seq,
            self.ack,
            self.flags,
            self.length,
            checksum
        )

        raw_bytes = header + self.payload
        return raw_bytes

    @staticmethod
    def unpack(raw_bytes):
        """ Converts all the raw bytes back into data that the reciver can use """
        header_size = struct.calcsize("!IIBHI")
        seq, ack, flags, length, checksum = struct.unpack("!IIBHI", raw_bytes[:header_size])
        payload = raw_bytes[header_size:header_size + length]

        # Return a packet that the reciver can use
        clean_packet = PHASE5_PACKET(seq, ack, flags, length, checksum, payload)
        return clean_packet