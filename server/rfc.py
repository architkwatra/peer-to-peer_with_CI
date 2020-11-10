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
                if f.rfcNumber == rfcNumber and f.rfcFileName == rfcFileName and f.peerOwnerHostName == peerOwnerHostName:
                    return True
                f = f.next
            return False

        if isPresent():
            print("This RFC is already present\n\n")
            return
        node = RFC(rfcFileName, rfcNumber, peerOwnerHostName)
        node.next = self.beg
        self.beg = node
        print('RFC added succesfully\n\n')

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
        f = self.beg
        if not self.beg:
            print('The RFC list is empty\n\n')
            return False
        
        
        dummy = RFC('dummy', -1, 'self')
        dummy.next = self.beg
        prev, f = dummy, self.beg

        while f:
            if f.peerOwnerHostName == peerOwnerHostName:
                prev.next = f.next
                print('\nRFC removed successfully\n')
                self.beg = dummy.next
                dummy.next = None
                return True
            f = f.next
            prev = prev.next
        
        print('No RFC entry found for the peer ', peerOwnerHostName)
        dummy.next = None
        return False

    def lookForRFC(self, rfcNumber):
        f = self.beg
        ans = []
        while f:            
            if f.rfcNumber == rfcNumber:
                ans.append({'number': f.rfcNumber, 'Name': f.rfcFileName, 'Owner': f.peerOwnerHostName})
            f = f.next
        if not ans:
            print('No RFC found with the number ', rfcNumber)
        print('\n\n')
        return ans