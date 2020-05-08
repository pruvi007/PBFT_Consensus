from collections import defaultdict


class Graph():
    
    def __init__(self,fileName):
        self.file = fileName
        self.adjList = defaultdict(list)
        self.X, self.Y, self.W = [], [], []
        self.edge = []
        self.N = 0
        
    def generate(self):
        file = open(self.file)
        for line in file.readlines():
            x, y, w = map(int,line.split())
            self.adjList[x].append([y,w])
            self.adjList[y].append([x,w])
            self.X.append(x)
            self.Y.append(y)
            self.W.append(w)
            self.edge.append([x,y])
            self.N = max(self.N,x,y)
