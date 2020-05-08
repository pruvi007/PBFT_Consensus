
class message:
    def __init__(self,state,viewNo,message,digest,Prk=None):
        
        self.state = state
        self.viewNo = viewNo
        self.message = message
        self.digest = digest
        self.Prk = Prk
    
        self.prepareCount = 0
        self.commitCount = 0

    def changeState(self,newState):
        self.state = newState