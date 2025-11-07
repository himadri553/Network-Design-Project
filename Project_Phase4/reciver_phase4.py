"""
    Nour Fahmy, Himadri Saha 

    reciver_phase4.py
    

"""
## Imports

## Reciver Class
class RECIVER4:
    def __init__(self, scenario = "1"):
        pass

    def get_checksum(self, data):
        """ Compute 16-bit checksum of given data """
        if len(data) % 2 != 0:
            data += b'\x00'
        checksum_sum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum_sum += word
        while checksum_sum > 0xFFFF:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
        return ~checksum_sum & 0xFFFF
    
    def run_receiver(self):
        pass