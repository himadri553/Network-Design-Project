"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 1

    phase1_UDP_client.py
    - Creates socket and connects to port
    - read datagram (user input) from client via socket 
    - Send message (user input) back to client via socket
    - close socket
    
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
    client_message, client_address = server_socket.recvfrom(2048)

    # Echo the same message back to clinet via server socket
    echo_message = client_message.decode()
    server_socket.sendto(echo_message.encode(), client_address)

