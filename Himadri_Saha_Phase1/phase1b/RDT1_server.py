"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 1b

    RDT1_server.py
    
    Hosts the server to receive a .bmp file from the client, and reconstructs received.bmp file for every the packets it recieves
    Utlizes the same UDP sockets as phase 1a
    The buffer_size is set to 2048 bytes, which represents the max amount of data the server will read from a client packet in each iteration
    Terminal print messages display the status of the server

"""
# Imports
from socket import *
from PIL import Image
import os

# Create and bind server socket to start server
server_port = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
print ("The server is ready to receive")

## Construct image while serever is running (check if file already exisits)
dest_filepath = os.path.join("Himadri_Saha_Phase1", "phase1b", "received.bmp")
if os.path.exists(dest_filepath):
    os.remove(dest_filepath)
with open(dest_filepath, "wb") as f:
    while True:
        # Get file from client via server socket
        buffer_size = 2048
        client_message, client_address = server_socket.recvfrom(buffer_size)
        print("Got chunk from clinet")

        # Until End message is read, write received chunk to file
        if client_message == b"END":
            print("File transfer done")
            break
        f.write(client_message)