from socket import *

# Server info
serverPort = 12000

# Create and bind server socket - start server
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print ("The server is ready to receive")

while True:
    # Get message from client via server socket
    message, clientAddress = serverSocket.recvfrom(2048)

    # Make new message and send back to client via server socket
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
