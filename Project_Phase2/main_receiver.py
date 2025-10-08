"""
main_receiver.py
Launches the advanced RDT 2.2 Receiver.
"""

from RDT22_Receiver_Advanced import RDT22_Receiver_Advanced

if __name__ == "__main__":
    receiver = RDT22_Receiver_Advanced(port=12000)
    receiver.run()
