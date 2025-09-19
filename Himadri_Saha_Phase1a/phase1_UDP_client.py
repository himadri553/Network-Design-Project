"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 1

    phase1_UDP_client.py

"""
# Imports
from socket import *

# Server info
server_name = 'localhost'
server_port = 12000

# Create and connect client socket
client_socket = socket(AF_INET, SOCK_DGRAM)

## Main user interaction
# Send message to server via client socket
message = input('Input a message: ')
client_socket.sendto(message.encode(), (server_name, server_port))

# Print the echo'd message and close socket and script
echo_message, server_address = client_socket.recvfrom(2048)
print("The echoed message from server is: ", echo_message.decode())
client_socket.close()