# -*- coding: utf-8 -*-



def ltr(a):
    return chr(a + 97)


class Prim:
    @staticmethod
    def indexOfMin(array, VT):
        minVal = float('inf')
        minIndex = -1
        for index, val in enumerate(array):
            if val < minVal and VT[index] is False:
                minVal = val
                minIndex = index
        return minIndex

    @staticmethod
    def sequential(matrix):
        r = 0  # pierwszy wierzchołek
        size = matrix.getSize()
        included = [False for i in range(size)]  # zbiór krawędzi spinających
        d = [float('inf') for i in range(size)]
        d[r] = 0
        edges = [-1 for i in range(size)]
        for i in range(size - 1):
            # parallel: pobierz najtańsze wierzchołki z partów i zredukuj jako master
            # następnie aktualizuj rozproszone d przekazując informację o tym jaki indeks został włączony
            u = Prim.indexOfMin(d, included)  # jak zrównoleglić: global minimum comes from reduction
            included[u] = True
            for v in range(size):  # to można zrównoleglić
                if included[v] is False and matrix.hasEdge(u, v):
                    Wuv = matrix.getWeight(u, v)
                    if Wuv < d[v]:
                        d[v] = Wuv
                        edges[v] = u

        for i in range(1, size):
            print '{}->{}'.format(ltr(i), ltr(edges[i]))


class PrimPart:
    def __init__(self, partNumber, matrixData):
        # posiadaj swoją małą macierz na której będziesz mógł wykonac indexOfMin oraz trzymac included itp
        # udostepnij interfejs dla moorglade
        self.partNumber = partNumber

        from utils import Matrix

        self.matrix = Matrix(matrixData)
        self.partSize = self.matrix.getSize()
        # --- INIT PRIM --- #
        self.r = 0
        self.size = self.partSize
        self.included = [False for i in range(self.size)]  # zbiór krawędzi spinających
        self.d = [float('inf') for i in range(self.size)]
        self.d[self.r] = 0
        self.edges = [-1 for i in range(self.size)]

    def processWeights(self, globalVertexIndex):
        includedLocalVertex = globalVertexIndex % self.partSize
        u = includedLocalVertex
        self.included[u] = True
        for v in range(self.size):
            if self.included[v] is False and self.matrix.hasEdge(u, v):
                Wuv = self.matrix.getWeight(u, v)
                if Wuv < self.d[v]:
                    self.d[v] = Wuv
                    self.edges[v] = u

    def getIndexOfMin(self):
        index = Prim.indexOfMin(self.d, self.included)
        globalIndex = index + self.partSize * self.partNumber
        return globalIndex

