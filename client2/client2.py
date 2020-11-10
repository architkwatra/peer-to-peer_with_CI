import socket
import os
from datetime import datetime
from pytz.reference import LocalTimezone
from platform import platform
from random import randint
import _thread

class Client:
    def __init__(self):

        # gethostbyname: Translate a host name to IPv4 address format. If it is already
        # in the form of a.b.c.d, it is returned unchanged

        self.serverPort = 7734
        self.serverIP = socket.gethostbyname('localhost')
        print("self.serverIP = ", self.serverIP)
        ploadServerPortRandomNumber = randint(1, 48000)
        clientNumber = randint(1, 1000)
        self.clientSocket = socket.socket()        
        self.clientName = socket.gethostname() + "@" + str(clientNumber)
        self.isConnected = False
        self.uploadServerPort = 1024 + ploadServerPortRandomNumber
        self.uploadServerSocket = socket.socket()
        self.uploadServerSocket.bind(('', self.uploadServerPort))
        

    def peerToPeeerGet(self, request):
        response = self.sendRequest(request)
        print(response)
        content = response.split('\n')
        
        if not response or len(content) < 2:
            return

        rfc = []
        for x in content[1].split():
            rfc.append(x.strip())

        peerHostName = rfc[2]
        peerPort = int(rfc[3])
        rfcNumber = rfc[0]
        rfcTitle = rfc[1]
        
        #AF_INET is an address family that is used to designate the type of addresses that your socket can 
        # communicate with (in this case, Internet Protocol v4 addresses). When you create a socket, you have 
        # to specify its address family, and then you can only use addresses of that type with the socket

        #TCP ( SOCK_STREAM ) is a connection-based protocol. The connection is established and the two parties 
        # have a conversation until the connection is terminated by one of the parties or by a network error
        recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp = peerHostName.split('@')
        peerHostName = temp[0].strip()
        recvSocket.connect((peerHostName, peerPort))
        recvSocket.send(rfcTitle.encode())
        data = recvSocket.recv(4096).decode()
        if data in ('P2P-CI/1.0 404 Not Found', 'P2P-CI/1.0 400 Bad Request'):
            print(data)
            return

        # Need to check this, since recv is a blocking call, this while loop won't exit, unless something 
        # like a empty string or EOF(maybe) is received
        # Ans: once the other side closes the connection, the received data field would get 0 bytes  
        # and then this loop exits if you don't call c.close() then this loop doesn't terminate
        fileName = rfcTitle + ".txt"
        f = open(fileName, 'w')
        recvData = recvSocket.recv(4096).decode()
        while True:
            f.write(recvData)
            recvData = recvSocket.recv(4096).decode()
            if not recvData:
                break

        f.close()
        print('RFC downloaded')

        protocol = 'ADD RFC ' + rfcNumber + ' P2P-CI/1.0'                
        title = 'Title: ' + rfcTitle
        host = 'Host: ' + self.clientName
        port = 'Port: ' + str(self.uploadServerPort)
        addRequest = [protocol, host, port, title]

        req = ''
        for i, res in enumerate(addRequest):
            req += res
            if i != len(response)-1:
                req += '\n'        
        response = self.sendRequest(req)
        print(response)
        recvSocket.close()

    def connectToServer(self):
        temp = (self.serverIP, self.serverPort)
        self.clientSocket.connect(temp)
        request = "Host: " + self.clientName + "\n" + "Port: " + str(self.uploadServerPort)
        self.clientSocket.send(request.encode())
        response = self.clientSocket.recv(4096).decode()
        return response

    def sendRequest(self, request):
        self.clientSocket.send(request.encode())
        response = self.clientSocket.recv(4096).decode()
        return response

    def uploadServerProcess(self):
        self.uploadServerSocket.listen(5)
        check = True
        while check:
            c, addr = self.uploadServerSocket.accept()
            rfcTitle = c.recv(4096).decode().strip()
            if rfcTitle:
                try:
                    fileName = rfcTitle + '.txt'
                    info = os.stat(fileName)
                    lastModified = datetime.fromtimestamp(info.st_mtime).strftime('%a, %d %b %Y %H:%M:%S %Z')

                    protocol = "P2P-CI/1.0 200 OK"                    
                    dateAndTime = "Date:" + datetime.now().strftime('%a,%d %b %Y %H:%M:%S') + " " + LocalTimezone().tzname(datetime.now())
                    lastModified = "Last-Modified:" + lastModified + " " + LocalTimezone().tzname(datetime.now())
                    operatingSys = "OS:" + platform()
                    contentType = "Content-Type:text/text"
                    contentLength = "Content-Length:" + str(info.st_size)

                    reply = [protocol, dateAndTime, lastModified, operatingSys, contentType, contentLength]

                    ret = ''
                    for i, res in enumerate(reply):
                        ret += res
                        if i != len(response)-1:
                            ret += '\n'
                            
                    c.send(ret.encode())

                    with open(fileName) as file:
                        for line in file:
                            c.send(line.encode())
                    c.close()

                except Exception as e:
                    print(e)
                    return "P2P-CI/1.0 400 Bad Request"


if __name__ == '__main__':
    client = Client()
    check = True
    connect = 'Do you want to connect to Server, (y/n)?: '
    options = "\n Please choose any pne of the above options\n\n 1. ADD \n 2. LOOKUP\n 3. LIST\n 4. GET\n 5. EXIT\n"
    while check:
        response = ''
        if not client.isConnected:
            print(connect)
            option = input()
            if (option == 'Y' or option == 'y'):
                _thread.start_new_thread(client.uploadServerProcess, ())
                response = client.connectToServer()
                if response:
                    client.isConnected = True
            elif option == 'n' or option == 'N':
                break
            else:
                print('Please enter the correct input (y/n)')
        else:
            print(options)
            option = input()
            request = []
            rfcNumber = 0
            rfcTitle = ''            
            if option == '1':
                print("Enter RFC number: ")
                rfcNumber = input()
                print("Enter RFC title: ")
                rfcTitle = input()
                protocol = 'ADD RFC ' + rfcNumber + ' P2P-CI/1.0'                
                title = 'Title: ' + rfcTitle
                host = 'Host: ' + client.clientName
                port = 'Port: ' + str(client.uploadServerPort)
                request = [protocol, host, port, title]

            elif option == '2':
                print("Enter RFC number: ")
                rfcNumber = input()
                print("Enter RFC title: ")
                
                protocol = 'LOOKUP RFC ' + rfcNumber + ' P2P-CI/1.0'                
                title = 'Title: ' + rfcTitle
                host = 'Host: ' + client.clientName
                port = 'Port: ' + str(client.uploadServerPort)
                request = [protocol, host, port, title]

            elif option == '3':
                protocol = 'LIST ALL P2P-CI/1.0'                
                title = 'Title: ' + rfcTitle
                host = 'Host: ' + client.clientName
                port = 'Port: ' + str(client.uploadServerPort)
                request = [protocol, host, port]

            elif option == '4':
                print("Enter RFC number: ")
                rfcNumber = input()
                
                protocol = 'LOOKUP RFC ' + rfcNumber + ' P2P-CI/1.0'               
                title = 'Title: ' + rfcTitle
                host = 'Host: ' + client.clientName
                operatingSys = 'OS: ' + platform()
                request = [protocol, host, operatingSys]
                
                req = ''
                for i, res in enumerate(request):
                    req += res
                    if i != len(response)-1:
                        req += '\n'
                req = (req, )
                _thread.start_new_thread(client.peerToPeeerGet, req)

            elif option == '5':
                
                protocol = 'EXIT RFC 123 P2P-CI/1.0'               
                port = 'Port: ' + str(client.uploadServerPort)
                host = 'Host: ' + client.clientName

                request = [protocol, host, port]

            if option in '1235' and request:
        
                ret = ''
                for i, res in enumerate(request):
                    ret += res
                    if i != len(response)-1:
                        ret += '\n'
                if ret:
                    response = client.sendRequest(ret)


            if option == '5':
                print('\033' + response + '\033')
                print("\n")
                client.clientSocket.close()
                break

        print(response)
