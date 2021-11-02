"""Client side of command line application of tcp server developed by Okoko Anainga on the 31/08/2021"""

import socket
import os
import time
import sys

def closeSocket(s):
    """Basic function to close and exit the client socket"""

    s.close()
    exit()

def argChecks():
    """Argument check and setting the host portnumber and filename"""

    if len(sys.argv) != 4:
        print(f'Wrong number of variables given, variable count is {len(sys.argv)}')
        exit()

    host = sys.argv[1]
    portNumber = int(sys.argv[2])
    filename = sys.argv[3]
    tup = (host, portNumber, filename)
    return tup

def socketSetup(host, portNumber, filename):
    """Sets up the socket and does error checking on host name, port number and
    checks weather or not the file exists in the current directory for sending"""

    try:
        socket.gethostbyname(host)
    except:
        print(f"The ip/host name {host} does not exist or is not well formatted")
        exit()

    if portNumber > 64000 or portNumber < 1024:
        print(f"Port number {portNumber} is out of range the connection will terminate now")
        exit()

    if os.path.isfile(filename):
        print('This file already exists')
        exit()

    try:
        serverAddress = (socket.gethostbyname(host), portNumber)
        s = socket.socket(socket.AF_INET, (socket.SOCK_STREAM))
    except:
        print("Socket could not be created you will now be exited")
        exit()

    try:
        s.connect(serverAddress)
        s.settimeout(1)
    except socket.timeout:
        print("Connection has failed the connection will now terminate")
        exit()
    return s

def fileRequest(filename):
    """Creates a fileRequest and sends it to the server"""

    len_filename =  len(filename)
    fileRequest = bytearray((b'I~\x01' + len_filename.to_bytes(2, 'big') + bytes(filename, 'utf-8')))
    s.send(fileRequest)

def fileheaderCheck(s):
    """Checks the file header of a fileResponse from the server and returns the length of the file"""

    try:
        fileheader = s.recv(8)
    except socket.timeout:
        print("Reading the file response has caused a time out error the socket will close and exit")
        closeSocket(s)

    if len(fileheader) != 8:
        print("File header is incomplete")
        return 0

    fileResponse = fileheader
    magicNumber = fileheader[1] | fileheader[0] << 8
    fileType = fileheader[2]
    statusCode = fileheader[3]


    if magicNumber != 0x497E:
        print('The magic number is incorrect')
        return 0

    if fileType != 2:
        print('The file type is incorrect')
        return 0

    if statusCode != 1:
        print('The file could not be read by the server')
        return 0

    filelen = fileheader[7] | fileheader[6] << 8 | fileheader[5] << 16 | fileheader[4] << 24
    return filelen

def finalPrint(counter, filelen):
    """ prints the summary for the filerequest if it failed or if it completed
    if completed prints summary of how many bytes were transferred and written the the file filename"""

    if counter != filelen:
        print(f"file transfer of \"{filename}\" went wrong")
        closeSocket(s)
    else:
        print(f"The transfer of file {filename} was succesful and {counter+8} bytes were transferred and written to file {filename}")
        closeSocket(s)



host, portNumber, filename = argChecks()
s = socketSetup(host, portNumber, filename)
fileRequest(filename)
filelen = fileheaderCheck(s)
if filelen == 0:
    print(f"file transfer of \"{filename}\" went wrong")
    closeSocket(s)
try:
    file = open(filename, 'wb')
except:
    print(f"The file \"{filename}\" could not be opened locally by the client the client will now terminate")
    closeSocket(s)
counter = 0


while True: # recieves the data from the server at 4096 bytes per loop until all the bytes are recieved or there is a timeout error
    try:
        data = s.recv(4096)
        if not data:
            break
        counter += len(data)
        file.write(data)
    except socket.timeout:
        print("Reading the file response has caused a time out error the socket will close and exit")
        closeSocket(s)
finalPrint(counter, filelen)
