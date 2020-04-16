import random

class view:
    def __init__(self,leader=1,viewNo=1,backups=[]):
        self.leader = leader
        self.viewNo = viewNo
        self.backups = backups
    
    def viewChange(self,viewNo,N):
        r = random.randint(1,N)
        return r,viewNo+1
