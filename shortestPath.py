
from heapq import heappop, heappush, heapify

class shortestPath():
    def __init__(self,graph,source,destination):
        self.source = source
        self.destination = destination
        self.G = graph
        self.X,self.Y,self.W = [],[],[]
    def getPath(self):
        
        # heap contains element of the form -> [ distance,node ]
        heap = [ [0,self.source] ]
        heapify(heap)
        adj = self.G.adjList
        INF = 10**10
        dist = [ INF for i in range(self.G.N+1) ]
        dist[self.source] = 0
        parent = [-1 for i in range(self.G.N+1)]
        while len(heap)>0:
            x = heappop(heap)
            node, d = x[1], x[0]

            # update the distances from popped node (min)
            v = adj[node]
            for i in range(len(v)):
                cur = v[i][0]
                wt = v[i][1]
                if dist[cur] > dist[node]+wt:
                    dist[cur] = dist[node]+wt
                    parent[cur] = node
                    heappush(heap, [dist[cur],cur] )
        path = self.tracePath(parent,self.destination)
        return dist[self.destination], path

    def tracePath(self,parent,j):
        path = []
        while parent[j]!=-1:
            path.append(j)
            j = parent[j]

        
        path = path[::-1]
        path = [self.source] + path
        # print(path)

        # convert this path to set of edges with weights (for plotting)
        for i in range(1,len(path)):
            x,y = path[i-1],path[i]
            w = self.searchForWeight(x,y)
            self.X.append(x)
            self.Y.append(y)
            self.W.append(w)
        return path
    
    def searchForWeight(self,x,y):
        edge = self.G.edge
        w = self.G.W
        for i in range(len(edge)):
            if (edge[i][0]==x and edge[i][1]==y) or (edge[i][1]==x and edge[i][0]==y):
                return w[i]
        return 0
