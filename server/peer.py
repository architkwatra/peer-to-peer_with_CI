
class Peer:
    def __init__(self, peerName, port):
        self.peerName = peerName
        self.port = port
        self.next = None
    
class PeerList:
    def __init__(self):
        self.beg = None
    
    def addPeer(self, peerName, port):
        def isPresent():
            f = self.beg
            while f:
                if f.port == port and f.peerName == peerName:
                    return True
                f = f.next
            return False

        if isPresent():
            print("This Peer is already present\n\n")
            return
        node = Peer(peerName, port)
        node.next = self.beg
        self.beg = node
        print('Peer added succesfully\n\n')
    
    def getAllPeers(self):
        if not self.beg:
            return []
        ret = []
        f = self.beg
        while f:
            temp = {'Peer': f.peerName, 'Port': f.port}
            ret.append(temp)
            f = f.next        
        return ret
    
    def deletePeer(self, peerName, port):
        if not self.beg:
            print('The PEER list is empty\n\n')
            return
        
        dummy = Peer('dummy', -1)
        dummy.next = self.beg
        prev, f = dummy, self.beg

        while f:
            if f.port == port and f.peerName == peerName:
                prev.next = f.next
                print('PEER removed successfully\n\n')
                self.beg = dummy.next
                return
            f = f.next
            prev = prev.next
        
        print('No PEER found on the port ', port)
        print('\n\n')
    
    def getPeer(self, port):
        f = self.beg
        while f:
            if f.port == port:
                return {'Peer': f.peerName, 'Port': f.port}
            f = f.next
        return 'No PEER found on the port' + port
    
    def getPortNumber(self, peerName):
        f = self.beg
        port = -1
        while f:
            if f.peerName == peerName:
                port = f.port
                break
            f = f.next
        if port == -1:
            print('No peer found with the name ', peerName)
            print('\n\n')
        return port

# sol = PeerList()
# sol.addPeer("12", 2)
# sol.addPeer("23", 3)
# sol.addPeer("34", 4)
# print(sol.getAllPeers())
# cur = sol.getPeer(3)
# print(cur)
# # print("[host_name= "+ cur['Peer'] + ", port_no = " + 
# #             str(cur['Port'])+ "]", end = " ")
# sol.deletePeer(2)
# print()
# print(sol.getAllPeers())
# sol.deletePeer(4)
# print()
# print(sol.getAllPeers())
# sol.deletePeer(3)
# print()
# print(sol.getAllPeers())