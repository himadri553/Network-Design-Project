"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 1b

    RDT1_client.py

    Utlizes the same UDP sockets as phase 1a
    Breaks the my_cloud.bmp file into chunks and sends them to the server with an end signal when done

"""
# Imports
from socket import *
import os

# Server info, and create client socket 
server_name = 'localhost'
server_port = 12000
client_socket = socket(AF_INET, SOCK_DGRAM)

# Get BMP file and send them as chunks to server via client socket. Send "end" signal when done
pic_path = os.path.join("Himadri_Saha_Phase1", "phase1b", "my_cloud.bmp")
with open(pic_path, "rb") as f:
    file_data = f.read()
chunk_size = 1024
for i in range(0, len(file_data), chunk_size):
    chunk = file_data[i:i+chunk_size]
    client_socket.sendto(chunk, (server_name, server_port))
client_socket.sendto(b"END", (server_name, server_port))