"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 1

    Project Description:
    The TCP/IP stack has five layers, namely application,
    transport, network, link, and physical. In Phase 1(a) of the project, each student must
    individually implement the standard user datagram protocol (UDP) sockets. The
    intention is to transfer a message (Say “HELLO”) from the UDP client to the UDP
    server and then ECHO the message back from the UDP server to the UDP client.
    Note that the client and server process can reside on the same host but have to use
    different port numbers. Make sure that your program can send and receive
    messages in both directions.

    phase1_UDP_client.py
    - creates a socket 
    - creates a datagram with server IP and port 
    - Send user inputed message to server
    - Recives the same message from server to client (ECHO)
    - closes anytime user presses (ctrl + x)

    Issues:
    - I think server is connected to clinet?? No error message, but no message being sent back to the client

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

# Wait till the echo'd message comes back from the server
modifiedMessage, serverAddress = client_socket.recvfrom(2048)

# Print the echo'd message and close socket and script
echo_message = client_socket.recvfrom(2048)
print("The echoed message from server is: ", echo_message.decode())
client_socket.close()