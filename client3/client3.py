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
        self.response = ""
        self.peerAddress = None
        print("serverIP = ", self.serverIP)
        self.listhead = None
        ploadServerPortRandomNumber = randint(1, 48000)
        clientNumber = randint(1, 1000)
        self.clientSocket = socket.socket()        
        temp = socket.gethostname() + "@" + str(clientNumber)
        self.clientName = temp
        self.user = ""
        self.isServerUp = False
        self.isClientReady = False
        self.connected = False
        temp = 1024 + ploadServerPortRandomNumber
        self.uploadServerPort = temp
        self.uploadServerSocket = socket.socket()
        portInfo = ('', self.uploadServerPort)
        self.uploadServerSocket.bind(portInfo)
        self.data = []

    def connectAndSend(self, recvSocket, peerInfo, encodedRfcTitle):
        recvSocket.connect(peerInfo)        
        recvSocket.send(encodedRfcTitle)

    def peerToPeeerGet(self, request):
        response = self.sendRequest(request)
        # print(response)
        content = response.split('\n')
        rfc = []
        if not response or len(content) < 2:
            return

        for x in content[1].split():
            temp = ""
            if x:
                temp = x.strip()
            if temp:
                rfc.append(temp)

        if rfc[2]:
            peerHostName = rfc[2]
        if rfc[3]:
            peerPort = int(rfc[3])
        if rfc[0]:
            rfcNumber = rfc[0]
        if rfc[1]:
            rfcTitle = rfc[1]
        fileName = rfcTitle + ".txt"
        encodedRfcTitle = rfcTitle.encode()
        #AF_INET is an address family that is used to designate the type of addresses that your socket can 
        # communicate with (in this case, Internet Protocol v4 addresses). When you create a socket, you have 
        # to specify its address family, and then you can only use addresses of that type with the socket

        #TCP ( SOCK_STREAM ) is a connection-based protocol. The connection is established and the two parties 
        # have a conversation until the connection is terminated by one of the parties or by a network error
        
        recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        temp = peerHostName.split('@')
        peerHostName = temp[0].strip()
        peerInfo = (peerHostName, peerPort)
        self.connectAndSend(recvSocket, peerInfo, encodedRfcTitle)
        data = recvSocket.recv(4096).decode()
        if data in ('P2P-CI/1.0 404 Not Found', 'P2P-CI/1.0 400 Bad Request'):
            print(data)
            return

        # Need to check this, since recv is a blocking call, this while loop won't exit, unless something 
        # like a empty string or EOF(maybe) is received
        # Ans: once the other side closes the connection, the received data field would get 0 bytes  
        # and then this loop exits if you don't call c.close() then this loop doesn't terminate
        
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
        print('\n')
        print(response)
        print("\nFile transfer complete, terminating peer to peer connection\n")
        recvSocket.close()

    def getResponse(self, request):
        self.clientSocket.send(request.encode())        
        response = self.clientSocket.recv(4096).decode()
        return response

    def connectToServer(self):
        temp = (self.serverIP, self.serverPort)
        if temp:
            self.clientSocket.connect(temp)        
        if self.clientName and self.uploadServerPort:
            response = self.getResponse("Host: " + self.clientName + "\n" + "Port: " + str(self.uploadServerPort))
        
        return response

    def sendRequest(self, request):
        response = self.getResponse(request)
        return response

    def formReply(self, rfcTitle):
        if rfcTitle:
            try:
                
                fileName = rfcTitle + '.txt'
                info = os.stat(fileName)
                tFormat = '%a, %d %b %Y %H:%M:%S %Z'
                lastModified = datetime.fromtimestamp(info.st_mtime).strftime(tFormat)
                typee = "dateAndSystemInfo"
                protocol = "P2P-CI/1.0 200 OK"                    
                dateAndTime = "Date:" + datetime.now().strftime('%a,%d %b %Y %H:%M:%S') + " " + LocalTimezone().tzname(datetime.now())
                lastModified = "Last-Modified:" + lastModified + " " + LocalTimezone().tzname(datetime.now())
                operatingSys = "OS:" + platform()
                sysInfo = "OS:" + str(platform()) + str(os.stat(fileName))
                contentType = "Content-Type:text/text"
                contentInfo = "python-text"
                contentLength = "Content-Length:" + str(info.st_size)
                reply = [protocol, dateAndTime, lastModified, operatingSys, contentType, contentLength]
            
            except Exception as e:
                print(e)
            
            return reply, fileName

    def uploadServerThread(self):
        check = True
        self.uploadServerSocket.listen(5) 
        while check:
            conn, addr = self.uploadServerSocket.accept()
            rfcTitle = conn.recv(4096).decode().strip()
            if rfcTitle:
                try:                    
                    reply, fileName = self.formReply(rfcTitle)
                    ret = ''
                    for i, res in enumerate(reply):
                        ret += res
                        if i != len(response)-1:
                            ret += '\n'
                    conn.send(ret.encode())
                    with open(fileName) as file:
                        for line in file:
                            conn.send(line.encode())
                    conn.close()

                except Exception as e:
                    print(e)
                    badReq = "P2P-CI/1.0 400 Bad Request"
                    return badReq


if __name__ == '__main__':
    client = Client()
    check = True
    connect = 'Do you want to connect to Server, (y/n)?: '
    options = "\n Please choose any pne of the above options\n\n 1. ADD \n 2. LOOKUP\n 3. LIST\n 4. GET\n 5. EXIT\n"
    while check:
        try:
            response = ''
            if not client.connected:
                print(connect)
                option = input()
                if (option == 'Y' or option == 'y'):
                    _thread.start_new_thread(client.uploadServerThread, ())
                    response = client.connectToServer()
                    if response:
                        client.connected = True
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
                    # print(response)
                    print("\n")
                    client.clientSocket.close()
                    break
        except Exception as e:
            print(e)
            break

        print(response)
