# Server program

from socket import *

# Set the socket parameters
host = "localhost"
port = 21567
buf = 1024
addr = (host,port)

# Create socket and bind to address
UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.bind(addr)

# Receive messages
while 1:
	data,addr = UDPSock.recvfrom(buf)
	if not data:
		print "Client has exited!"
		break
	else:
		print "\nReceived message '", data,"'"

# Close socket
UDPSock.close()

UDPSock = socket(AF_INET,SOCK_DGRAM)

def_msg = "===Enter message to send to server===";
print "\n",def_msg

# Send messages
while (1):
	data = raw_input('>> ')
	if not data:
		break
	else:
		if(UDPSock.sendto(data,addr)):
			print "Sending message '",data,"'....."

# Close socket
UDPSock.close()
