from view import *
from message import *
from shortestPath import *
from getPlot import *
from view import *
from Graph import *
from cryptography.fernet import Fernet
import matplotlib.pyplot as plt
import random

class pbft:
    def __init__(self,source,destination,graph,faulty=6):
        self.query = [source,destination]

        # private key of Leader Node
        self.key = Fernet.generate_key()

        # objects 
        self.GRAPH = graph
        self.VIEW = view(random.randint(1,self.GRAPH.N),1,[])
        self.SHORTEST_PATH = shortestPath(self.GRAPH,self.query[0],self.query[1])
        

        self.faulty = faulty
        self.falutyNodes = []
        self.faultyLeaders = []
    
        # assign random faulty Nodes 
        for i in range(self.faulty):
            r = random.randint(1,self.GRAPH.N)
            while r in self.falutyNodes:
                r = random.randint(1,self.GRAPH.N)
            self.falutyNodes.append(r)

        # call the Controller Method
        self.controller()

    def genMessageAndDigest(self,path,shortestDistance):
        # Concat the the path and Weight into a single Message
        self.message = "Path: "
        for i in range(len(path)):
            self.message += str(path[i]) + " "
        self.message += "\n" + "Traffic: " + str(shortestDistance) + "\n"
        
        # encrypt the Message and get the digest
        enc_type = Fernet(self.key)
        enc_message = enc_type.encrypt(self.message.encode('ASCII'))
        self.digest = enc_message

        return message("PRE-PREPARE",self.VIEW.viewNo,self.message,self.digest,self.key)

    def phase1(self,leader,leaderMessage):

        print("\nPHASE1::<<PRE_PREPARE>>")
        N = self.GRAPH.N
        messagePhase1 = 0
        # multicast the message to the backups - PRE_PREPARE
        for i in range(N):
            # dont send (if the backup is leader or its a faulty leader)
            if i+1 == leader or i+1 in self.faultyLeaders:
                continue
            else:
                self.VIEW.backups.append([i+1,leaderMessage])
                messagePhase1 += 1
        

        print("Messages sent to all backups\nPHASE1::Complete\n")

    def valid(self,message):
        # get the private Key
        key = message.Prk
        enc_type = Fernet(key)

        # decrypt the digest to get the message
        decrypt_message = enc_type.decrypt(message.digest)

        # match the messages and viewNo's
        crt1 = decrypt_message.decode('ASCII') == message.message
        crt2 = message.viewNo == self.VIEW.viewNo
        return crt1 and crt2

    def phase2(self):
        import string
        # verify the message at each backup (if valid then send a Prepare Request)
        print("\nPHASE2::<<PREPARE>>")
        messagePhase2 = 0

        for i in range(len(self.VIEW.backups)):
            m = self.VIEW.backups[i][1]
            if self.valid(m):
                # print("valid")
                for j in range(len(self.VIEW.backups)):
                    if self.VIEW.backups[j][0] != self.VIEW.backups[i][0]:
                        mess = self.VIEW.backups[i][1].message

                        # if faulty node then wrong message will be sent
                        # then the decrypted message will not be same
                        if j+1 in self.falutyNodes:
                            mess = ''.join(random.choices(string.ascii_uppercase +\
                                string.digits, k = 20))

                        prepMessage = message("Prepare",self.VIEW.viewNo,mess,self.digest)
                        self.VIEW.backups[j].append(prepMessage)
                        self.VIEW.backups[j][2].prepareCount += 1
                        messagePhase2 += 1

        print("PHASE2::Complete")

    def phase3(self):
        # commit if 2f prepare messages matches the pre-Prepare
        print("\nPHASE3::<<COMMIT>>")

        messagePhase3 = 0
        for i in range(len(self.VIEW.backups)):
            if len(self.VIEW.backups[i])>2:
                bp = self.VIEW.backups[i][2]
                num_prepares = self.VIEW.backups[i][2].prepareCount

                # if backup recieved 2F+1 prepares -> commit
                if num_prepares >= 2*self.faulty + 1:
                    mess = bp.message
                    for j in range(len(self.VIEW.backups)):
                        if j!=i:
                            commit_message = message("Commit",self.VIEW.viewNo,mess,self.digest)
                            self.VIEW.backups[j].append(commit_message)
                            self.VIEW.backups[j][3].commitCount += 1
                            messagePhase3+=1

       
        print("Commit messages Sent\nPHASE3::Complete\n")

    def finalCommit(self):
        # if backups have atleast 2f commits then add that commit to final Commit pool
        commit_pool = {}

        for i in range(len(self.VIEW.backups)):
            if len(self.VIEW.backups[i])>3:
                bp = self.VIEW.backups[i][3]
                num_prepares = self.VIEW.backups[i][3].commitCount
                if num_prepares >= 2*self.faulty:
                    mess = bp.message
                    if mess not in commit_pool:
                        commit_pool[mess] = 1
                    else:
                        commit_pool[mess] += 1
        
        # print(commit_pool)
        result = ''
        correct = 0
        for (k,v) in zip(commit_pool.keys(),commit_pool.values()):
            # if commit messages is greater than 2F then only commit
            if v>=2*self.faulty:
                result = k
                break
        if result != '':
            print("Final message reached after PBFT consenus: \nShortestPath:\n{}".format(result))
            print()

            # display the graphs
            Gx, Gy, Gw = self.GRAPH.X, self.GRAPH.Y, self.GRAPH.W
            GPlot = getPlot(Gx,Gy,Gw,[])
            GPlot.show("Actual Network")

            pathx,pathy,pathw,edges = self.SHORTEST_PATH.X, self.SHORTEST_PATH.Y, self.SHORTEST_PATH.W, self.SHORTEST_PATH.edge
            print(edges)
            SPPlot = getPlot(Gx,Gy,Gw,edges)

            
            SPPlot.show("Shortest Path: {}->{}\n{}".format(self.query[0],self.query[1],result))
            plt.show()
        else:
            print("Unable to reach CONSENSUS\n")

    def controller(self):

        shortestDistance,path = self.SHORTEST_PATH.getPath()


        print("FAULTY-NODES:{}".format(self.falutyNodes))
        print("FAULTY-LEADERS:{}\n".format(self.faultyLeaders))

        systemState = "START"
        while systemState!="END":
            print("**************ROUND-{}***************".format(self.VIEW.viewNo))
            print("LEADER:{}\nViewNo:{}\n".format(self.VIEW.leader,self.VIEW.viewNo))

            leaderMessage = self.genMessageAndDigest(path,shortestDistance)
            self.phase1(self.VIEW.leader,leaderMessage)

            if self.VIEW.leader in self.falutyNodes:
                self.faultyLeaders.append(self.VIEW.leader)
                print("Leader:{} is Faulty\nChanging View...\n".format(self.VIEW.leader))
                print("FAULTY-LEADERS:{}\n".format(self.faultyLeaders))
                newLeader,newViewNo = self.VIEW.viewChange(self.VIEW.viewNo,self.GRAPH.N)
                self.VIEW = view(newLeader,newViewNo,[])
                continue

            self.phase2()
            self.phase3()
            self.finalCommit()
            systemState = "END"
        
        


