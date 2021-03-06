# -*- coding: utf-8 -*-



def ltr(a):
    return chr(a + 97)


class Prim:
    @staticmethod
    def indexOfMin(array, VT):
        minVal = float('inf')
        minIndex = -1
        for index, val in enumerate(array):
            if val <= minVal and VT[index] is False:
                minVal = val
                minIndex = index
        return minIndex

    @staticmethod
    def sequential(matrix, printMe=True):
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
            # print "seq i={} u={} included={}".format(i, u, included)
            for v in range(size):  # to można zrównoleglić
                if included[v] is False and matrix.hasEdge(u, v):
                    Wuv = matrix.getWeight(u, v)
                    if Wuv < d[v]:
                        d[v] = Wuv
                        edges[v] = u
                        # print 'seq d[n] at i {} = {}'.format(i, d)
                        # print 'seq included[n] at i {} = {}'.format(i, included)

        if printMe:
            for i in range(1, size):
                print '{}->{}'.format(ltr(i), ltr(edges[i]))
        return edges


class PrimPart:
    def __init__(self, partNumber, matrixData, printMe=True):
        # posiadaj swoją małą macierz na której będziesz mógł wykonac indexOfMin oraz trzymac included itp
        # udostepnij interfejs dla moorglade
        self.partNumber = partNumber
        self.printMe = printMe

        from utils import Matrix

        self.matrix = Matrix(matrixData)
        self.partSize = self.matrix.getNumCols()
        self.partOffset = self.partSize * self.partNumber

        # --- INIT PRIM --- #
        self.r = 0
        self.size = self.partSize
        self.included = [False for i in range(self.size)]  # zbiór krawędzi spinających
        self.d = [float('inf') for i in range(self.size)]
        if self.partNumber == 0:  # tylko dla pierwszego partu dajemy zero
            self.d[self.r] = 0
        self.edges = [-1 for i in range(self.size)]

    def processWeights(self, i, u):

        localU = u - self.partOffset

        if 0 <= localU < self.partSize:
            # print "part size = {}, global u={} on part {} = local {} / offset = {}".format(self.partSize, u,
            #                                                                                self.partNumber, localU,
            #                                                                                self.partOffset)
            self.included[localU] = True

        # print "par i={} included={}".format(i, self.included)
        for v in range(self.size):
            if self.included[v] is False and self.matrix.hasEdge(u, v):
                Wuv = self.matrix.getWeight(u, v)
                if Wuv <= self.d[v]:
                    self.d[v] = Wuv
                    self.edges[v] = u
                    # print 'par d[n] = {}'.format(self.d)
                    # print 'included[n] = {}'.format(self.included)

    def getIndexOfMin(self):
        index = Prim.indexOfMin(self.d, self.included)
        globalIndex = index + self.partOffset
        return globalIndex, self.d[index]

