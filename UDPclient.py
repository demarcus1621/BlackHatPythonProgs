import socket

target_host = "127.0.0.1" #Localhost
target_port = 80

#create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send data
client.sendto(b"AAABBBCCC", (target_host, target_port) )
#UDP is a connectionless protocol, thus there is no need to 
#connect to the server

#receive data response
data, addr = client.recvfrom(4096)

print(data)