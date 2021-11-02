"""Server side of command line application for TCP server developed by Okoko Anainga on the 31/08/2021"""

import socket
import time
import sys
import os


def closeS():
    """Closes the client socket"""
    clientsocket.close()

def preChecks():
    """does prechecks of arguments given then if all is correct returns the
                                port number"""
    if len(sys.argv) != 2:
        print('Not enough variables given')
        exit()

    portNumber = int(sys.argv[1])

    if portNumber > 64000 or portNumber < 1024:
        print(f"Port number {portNumber} is out of range the connection will terminate now")
        exit()
    else:
        return portNumber


def checkData(clientsocket):
    """gets a file request and processes the request checking the header then
    returning a file name if the header is correct"""

    try:
        fileRequest = clientsocket.recv(4096)
    except socket.timeout:
        print("clientsocket has timed out the socket will terminate")
        return 0

    magicNumber = fileRequest[1] | fileRequest[0] << 8

    if magicNumber != 0x497E:
        print("This file request is not safe abort!")
        return 0

    try:
        fileRequest[2] == 1
    except:
        print("The file type field is incorrect")
        clientsocket.close()

    n = fileRequest[4] | fileRequest[3] << 8
    filename = fileRequest[5::].decode('utf-8')

    if n > 1024 or n < 1:
        print("Filename is to large")
        return 0
    else:
        return filename


def fileResponse(filename):
    """ Function for processing a recieved file into a file response to
    send back to the client will return 0 if there is an error or will send the
    file if no error exists"""

    try:
        file = open(filename, 'rb')
    except:
        response = 0
        len_data = 0
        fileResponse = bytearray((b'I~\x02' + response.to_bytes(1, 'big') + len_data.to_bytes(4, 'big')))
        clientsocket.send(fileResponse)
        print(f"The file \"{filename}\" could not be opened and an appropriate respose has been sent to the client")
        closeS()
        return 0


    len_data = os.path.getsize(filename)
    response = 1
    counter = 0
    fileResponse = bytearray((b'I~\x02' + response.to_bytes(1, 'big') + len_data.to_bytes(4, 'big')))
    clientsocket.send(fileResponse)
    while True: # reads the file by 4096 bytes per loop and sends it until all the data is read from the file
        data = file.read(4096)
        clientsocket.send(data)
        if not data:
            break
        counter += len(data)
    file.close()


    print(f"The fileRespose for file {filename} was completed and {len_data+8} bytes of data were transferred")
    closeS()



port = preChecks()
host = socket.gethostname()
print(f"Server ip {socket.gethostbyname(host)}")
print(f"Server port {port}")
server_address = (host, port)
s = socket.socket(socket.AF_INET, (socket.SOCK_STREAM))

try:
     s.bind(server_address)

except:
     print(f"There was an error binding to address {server_address}")
     exit()

try:
    s.listen()
except:
    print(f"Could not find client at address {server_address}")
    closeS()
    exit()

while True:
    t = time.localtime()
    currentTime = time.strftime("%H:%M:%S", t)
    clientsocket, address = s.accept()
    clientsocket.settimeout(1)
    print(f"Connection from {address} has been astablished at time {currentTime}")
    filename = checkData(clientsocket)
    if filename != 0:
        fileResponse(filename)
    else:
        closeS()
closeS()
exit()
