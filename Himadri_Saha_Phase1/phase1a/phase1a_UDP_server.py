"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 1

    phase1a_UDP_server.py
    
    Run this before running phase1_UDP_client.py
    
"""
# Imports
from socket import *

# Create and bind server socket to start server
server_port = 12000
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
print ("The server is ready to receive")

while True:
    # Get message from client via server socket
    buffer_size = 2048
    client_message, client_address = server_socket.recvfrom(buffer_size)

    # Echo the same message back to clinet via server socket
    echo_message = client_message.decode()
    print("Message recived from the clinet!") 
    server_socket.sendto(echo_message.encode(), client_address)

