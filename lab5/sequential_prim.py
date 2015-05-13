# -*- coding: utf-8 -*-
def ltr(a):
    return chr(a + 97)


class SequentialPrim:
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
    def calculate(matrix):
        r = 0  # pierwszy wierzchołek
        size = matrix.getSize()
        included = [False for i in range(size)]  # zbiór krawędzi spinających
        d = [float('inf') for i in range(size)]
        d[r] = 0
        edges = [-1 for i in range(size)]
        for i in range(size - 1):
            u = SequentialPrim.indexOfMin(d, included)  # jak zrównoleglić: global minimum comes from reduction
            included[u] = True
            for v in range(size):  # to można zrównoleglić
                if included[v] is False and matrix.hasEdge(u, v):
                    Wuv = matrix.getWeight(u, v)
                    if Wuv < d[v]:
                        d[v] = Wuv
                        edges[v] = u

        for i in range(1, size):
            print '{}->{}'.format(ltr(i), ltr(edges[i]))