from socket import *

# Server info
serverName = 'localhost'
serverPort = 12000

# Create client socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Send message
message = input('Input lowercase sentence:')

# Send message to server via socket
clientSocket.sendto(message.encode(), (serverName, serverPort))

# Get message from sever via clinet socket
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

# Print and close
print(modifiedMessage.decode())
clientSocket.close()
