class RFC:
    def __init__(self, rfcFileName, rfcNumber, peerOwnerHostName):        
        self.next = None
        self.rfcFileName = rfcFileName
        self.rfcNumber = rfcNumber
        self.peerOwnerHostName = peerOwnerHostName

class RFCList:
    
    def __init__(self):
        self.beg = None
    
    def addRFC(self, rfcFileName, rfcNumber, peerOwnerHostName):
        def isPresent():
            f = self.beg
            while f:
                if f.rfcNumber == rfcNumber:
                    return True
                f = f.next
            return False

        if isPresent():
            print("This RFC is already present")
            return
        node = RFC(rfcFileName, rfcNumber, peerOwnerHostName)
        node.next = self.beg
        self.beg = node
        print('RFC added succesfully')

    def getAllRFCs(self):
        if not self.beg:
            return []
        ret = []
        f = self.beg
        while f:
            temp = {'number': f.rfcNumber, 'Name': f.rfcFileName, 'Owner': f.peerOwnerHostName}
            ret.append(temp)
            f = f.next        
        return ret
    
    def deleteRFC(self, peerOwnerHostName):

        if not self.beg:
            print('The RFC list is empty')
            return
        
        dummy = RFC('dummy', -1, 'self')
        dummy.next = self.beg
        prev, f = dummy, self.beg

        while f:
            if f.peerOwnerHostName == peerOwnerHostName:
                prev.next = f.next
                print('RFC removed successfully')
                self.beg = dummy.next
                return
            f = f.next
            prev = prev.next
        
        print('No RFC entry found for the peer ', peerOwnerHostName)

    def getRFC(self, rfcNumber):
        f = self.beg
        while f:
            if f.rfcNumber == rfcNumber:
                return {'number': f.rfcNumber, 'Name': f.rfcFileName, 'Owner': f.peerOwnerHostName}
            f = f.next
        print('No RFC found with the number ', rfcNumber)
        return None

sol = RFCList()
# rfcFileName, rfcNumber, peerOwnerHostName
sol.addRFC('12', 1, 'ab')
sol.addRFC('23', 2, 'bc')
sol.addRFC('34', 3, 'cd')
print(sol.getAllRFCs())
cur = sol.getRFC(3)
print('\n\n', cur)
sol.deleteRFC('cd')
print(sol.getAllRFCs())
print('\n')
sol.deleteRFC('bc')
print(sol.getAllRFCs())
sol.deleteRFC('ab')
print(sol.getAllRFCs())













        

