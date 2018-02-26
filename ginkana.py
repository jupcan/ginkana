#!/usr/bin/python3

'''
/// Ginkana - Computer Networks II \\\
/// 	Juan Perea Campos 2A		\\\
///			 71229899A				 \\\
'''

from socket import *
import urllib.request
import struct, time
import socketserver
import threading

# Functions
def cksum(data):

    def sum16(data):
        "sum all the the 16-bit words in data"
        if len(data) % 2:
            data += '\0'.encode()

        return sum(struct.unpack("!%sH" % (len(data) // 2), data))

    retval = sum16(data)                       # sum
    retval = sum16(struct.pack('!L', retval))  # one's complement sum
    retval = (retval & 0xFFFF) ^ 0xFFFF        # one's complement
    return retval
	
def thread_loop(proxy_http):

	while True:
		
		threading.Thread(name = 'loop_threads', target = http_stuff, args = (client_sck,)).start()
		(client_sck, address) = proxy_http.accept()
		
def http_stuff(client_sck):

	txt7 = client_sck.recv(1024)
	txt8 = txt7.split()
	url_needed = txt8[1]

	download = urllib.request.urlopen(url_needed)
	client_sck.sendto(download, ("atclab.esi.uclm.es", 9000))
	download.close()
	client_sck.close()
	
# Stages
def stage_0():

	sck1 = socket(AF_INET, SOCK_STREAM)
	sck1.connect(("atclab.esi.uclm.es", 2000))
	txt1 = sck1.recv(1024).decode()
	print(txt1 + '\n')
	sck1.close()
	
	id = txt1.split('\n', 1)
	return id[0]
	
def stage_1(id):

	server_port = 15500
	sck2 = socket(AF_INET, SOCK_DGRAM)
	sck2.bind(('', int(server_port)))

	txt_sent = id + ' ' + str(server_port)
	sck2.sendto((txt_sent.encode()), ("atclab.esi.uclm.es", 2000))
	txt2 = sck2.recv(1024).decode()
	print(txt2 + '\n')
	sck2.close()
	
	port1 = txt2.split('\n', 1)
	return port1[0]

def stage_2(port1):

	sck3 = socket(AF_INET, SOCK_STREAM)
	sck3.connect(("atclab.esi.uclm.es", int(port1)))
	file = sck3.recv(1024).decode()

	while file[0] == '(':
		
		if file.count('(') != file.count(')'):
			file = file + sck3.recv(1024).decode()
			
		file = file.replace('/', '//')
		op_result = eval(file)
		op_result = '(' + str(op_result) + ')'
		print(file + ' = ' + op_result + '\n')
		sck3.sendto((op_result.encode()), ("atclab.esi.uclm.es", int(port1)))
		file = sck3.recv(1024).decode()
		
	print(file + '\n')
	sck3.close()
	
	http = file.split('"', 2)
	http = http[1].split('"', 1)
	return http[0]
	
def stage_3(http):

	download = urllib.request.urlopen(http)
	txt3 = download.read()
	print(txt3.decode())
	download.close()
	
	port2 = txt3.decode().split('\n', 1)
	return port2[0]
	
def stage_4(port2):

	sck4 = socket(AF_INET, SOCK_RAW, getprotobyname('ICMP'))
	header1 = struct.pack('!bbHHh', 8, 0, 0, 0, 1)
	payload = struct.pack("d5s", time.time(), port2.encode('utf-8'))
	
	checksum = cksum(header1 + payload)
	header2 = struct.pack("!bbHHh", 8, 0, checksum, 0, 1)
	
	packet = header2 + payload
	sck4.sendto(packet, ("atclab.esi.uclm.es", 1))
	header3 = sck4.recv(2048)
	txt4 = sck4.recv(2048)
	print(txt4[36:].decode())
	sck4.close()
	
	port3 = txt4[36:].decode().split('\n', 1)
	return port3[0]
	
def stage_5(port3):

	sck5 = socket(AF_INET, SOCK_STREAM)
	sck5.connect(("atclab.esi.uclm.es", 9000))
	txt5 = port3  + " " + str(15500)
	sck5.send(txt5.encode())

	proxy_http = socket(AF_INET, SOCK_STREAM)
	proxy_http.bind(('', 15500))
	proxy_http.listen(35)
	threading.Thread(name = 'main_thread', target = thread_loop, args = (proxy_http,)).start()
	
	txt6 = sck5.recv(1024)
	print(txt6.decode())
	sck5.close()
	
# Main
if __name__ == "__main__":

	print("\n--------------------\n CN II - Ginkana\n--------------------")
	print(" Stage 0\n--------------------\n")
	id = stage_0()
	
	print("--------------------\n Stage 1\n--------------------\n")
	port1 = stage_1(id)
	
	print("--------------------\n Stage 2\n--------------------\n")
	http = stage_2(port1)
	
	print("--------------------\n Stage 3\n--------------------\n")
	port2 = stage_3(http)
	
	print("--------------------\n Stage 4\n--------------------\n")
	port3 = stage_4(port2)
	
	print("--------------------\n Stage 5\n--------------------\n")
	stage_5(port3)
	
'''
--------------------
Webography
--------------------
http://stackoverflow.com
https://docs.python.org/3/
--------------------
Stage 3
--------------------
https://docs.python.org/3.0/library/urllib.request.html
--------------------
Stage 4
--------------------
https://support.microsoft.com/es-es/kb/170292/es
http://en.wikipedia.org/wiki/Internet_Control_Message_Protocol
https://docs.python.org/3/tutorial/datastructures.html
https://bitbucket.org/arco_group/python-net/src/tip/raw/icmp_checksum.py
https://docs.python.org/3.0/library/struct.html
http://stackoverflow.com/questions/17218357/python-3-3-struct-pack-wont-accept-strings
--------------------
Stage 5
--------------------
https://docs.python.org/3.2/library/socket.html
https://docs.python.org/3/howto/sockets.html
https://docs.python.org/3/library/threading.html
http://stackoverflow.com/questions/16199793/python-3-3-simple-threading-event-example
https://docs.python.org/3/library/socket.html
http://stackoverflow.com/questions/15143837/how-to-multi-thread-an-operation-within-a-loop-in-python
http://www.troyfawkes.com/learn-python-multithreading-queues-basics/

* The manual our teacher gave us has also been used to create all the stages.
'''