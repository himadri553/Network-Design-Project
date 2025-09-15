# Imports
from socket import *

# Set server and ports
serverName = 'hostname'
serverPort = 12000

# Create UDP scoket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Get user import
message = input('Intput lowercase sentence: ')

# Attach server name, port to message, send into socket
clientSocket.sendto(message.encode(), (serverName, serverPort))

# Read reply characters from socket into a string
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

# Print and close socket
print(modifiedMessage.decode())
clientSocket.close()