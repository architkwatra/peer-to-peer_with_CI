import _thread
import traceback
import socket
from rfc import RFCList
from peer import PeerList

def addRFC(request, client, clientPort):
    # request =  ['ADD RFC 1 P2P-CI/1.0', 'Host: Archit@75', 
    # 'Port: 36985', 'Title: rfc1.txt']
    if len(request) >= 4:
        protocol = request[0]
        protocol = protocol.strip().split(' ')
        rfcNumber = protocol[2].strip()

        title = request[3]
        title = title.strip().split(':')
        rfcTitle = title[1].strip()
        
        rfcNode.addRFC(rfcTitle, rfcNumber , client)
        info = rfcNumber + ' ' + rfcTitle + ' ' + client + ' ' + clientPort
        response = ['P2P-CI/1.0 200 OK',  info]
        ret = ''
        for i, res in enumerate(response):
            ret += res
            if i != len(response) -1:
                ret += '\n'
        return ret
    return "ERROR"

def listAllRFCs():
    rfcList = rfcNode.getAllRFCs()
    response = ['P2P-CI/1.0 200 OK']
    for i, rfc in enumerate(rfcList):
        peerPort = peerNode.getPortNumber(rfc['Owner'])
        if peerPort:
            entry = rfc['number'] + ' ' + rfc['Name'] + ' ' + rfc['Owner'] + ' ' + str(peerPort)
            response.append(entry)
    if not rfcList:
        return "P2P-CI/1.0 404 Not Found"
    ret = ''
    for i, res in enumerate(response):
        ret += res
        if i != len(response) -1:
            ret += '\n'
    return ret

def searchForRFC(request):
    temp = request[0].strip().split()
    # print('temp = ', temp)
    rfcNumber = temp[2].strip()
    matchingRfcList = rfcNode.lookForRFC(rfcNumber)
    response = ['P2P-CI/1.0 200 OK']
    for i, peer in enumerate(matchingRfcList):
        peer_port_no = peerNode.getPortNumber(peer['Owner'])
        temp = rfcNumber + ' ' + peer['Name'] + ' ' + peer['Owner'] + ' ' + str(peer_port_no)
        response.append(temp)
    if not matchingRfcList:
        return "P2P-CI/1.0 404 Not Found"
    ret = ''
    for i, res in enumerate(response):
        ret += res
        if i != len(response) -1:
            ret += '\n'
    return ret

def handleVersionIssue(conn):
    resposne = "505 P2P-CI Version Not Supported"
    response = response.encode() 
    conn.send(response)

def runThread(conn):
    conn.send("P2P-CI/1.0 200 OK".encode())
    while True:

        # Note For best match with hardware and network realities, the value of bufsize should be a relatively 
        # small power of 2, for example, 4096.

        request = conn.recv(4096)
        request = request.decode()
        version = None
        method = None
        protocol = None
        # request =  ADD RFC 2 P2P-CI/1.0 \n Host: Archit@834 \n Port: 31962 \n Title: b
        try:
            if request:
                request = request.split('\n')
            method = request[0].strip().split()[0].strip()
            protocol = request[0].strip().split()
            
            # LIST ALL P2P-CI/1.0
            version = protocol[2].strip() if method == 'LIST' else protocol[3].strip()
                
        except Exception as e:
            print(e)
            resposne = "P2P-CI/1.0 400 Bad Request"
            response = response.encode() 
            conn.send(response)
            # traceback.print_exc()
            continue

        hostNumber = None
        portNumber = None
        
        try:            
            hostName = request[1].strip().split(':')[1].strip()
            portNumber = request[2].strip().split(':')[1].strip()
        except Exception as e:
            print(e)
            resposne = "P2P-CI/1.0 400 Bad Request"
            response = response.encode() 
            conn.send(response)
            continue
        
        if version != 'P2P-CI/1.0':
            handleVersionIssue(conn)
            continue
        
        if method == 'ADD':
            try:
                response = addRFC(request, hostName, portNumber)
                conn.send(response.encode())
            except Exception as e:
                print(e)
                resposne = "P2P-CI/1.0 400 Bad Request"
                response = response.encode() 
                conn.send(response)
        elif method == 'LOOKUP':
            try:
                response = searchForRFC(request)
                conn.send(response.encode())
            except Exception as e:
                print(e)
                resposne = "P2P-CI/1.0 400 Bad Request"
                response = response.encode() 
                conn.send(response)
        elif method == 'LIST':
            try:
                response = listAllRFCs()
                conn.send(response.encode())
            except Exception as e:
                print(e)
                resposne = "P2P-CI/1.0 400 Bad Request"
                response = response.encode() 
                conn.send(response)
        elif method == 'EXIT':
            try:
                peerNode.deletePeer(hostName, portNumber)
                while True: 
                    if rfcNode.deleteRFC(hostName):
                        continue
                    else:
                        break
                conn.send("P2P-CI/1.0 200 OK".encode())
                conn.close()
                print('<------------A thread has been terminated------------>')
                break
            except Exception as e:
                print(e)


if __name__ == '__main__':
    sckt = socket.socket()
    port = 7734
    if sckt:        
        #(host, port)
        sckt.bind(('', port))
        #Listen for connections made to the socket. The backlog argument specifies the maximum number of 
        # queued connections and should be at least 0; the maximum value is system-dependent (usually 5), 
        # the minimum value is forced to 0.   
        sckt.listen(5)
        print("Server listening on port number 7743!")
        peerNode = PeerList()
        rfcNode = RFCList()
        while True:
            #Below is what the conn looks like
            #<socket.socket fd=436, family=AddressFamily.AF_INET, 
            # type=SocketKind.SOCK_STREAM, proto=0, laddr=('0.0.0.0', 7734)>

            # Accept a connection. The socket must be bound to an address and listening for connections. 
            # The return value is a pair (conn, address) where conn is a new socket object usable to send 
            # and receive data on the connection, and address is the address bound to the socket on the other 
            # end of the connection.
            conn, addr = 0, 0
            if sckt:
                conn, addr = sckt.accept()
            print('Connected with ', addr)
            request = None
            if conn:
                request = conn.recv(4096).decode().split('\n')
            #_request  =  ['Host: Archit@551', 'Port: 33569']
            
            if request and request[1]:
                clientPort = request[1].split(':')[1].strip()
            if request and request[0]:
                clientName = request[0].split(':')[1].strip()        

            peerNode.addPeer(clientName, clientPort)
            _thread.start_new_thread(runThread, (conn, ))