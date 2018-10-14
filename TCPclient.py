import socket

target_host = "www.google.com"
target_port = 80

#Assumes that target server expects a request before it
#sends a response

#creation of socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#AF_INET = using IPV4 or hostname
#SOCK_STREAM = TCP Client

#connect to client
client.connect(( target_host, target_port ))

#send data through HTTP request
#This is a bit different from the book, as Python3 requires a byte string
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

#receive response
response = client.recv(4096)

#print the response
#Print function for Python3, which is different than book
print(response)