from prim import Prim


class Matrix:
    def __init__(self, data):
        self._data = data
        self._size = len(data)
        self._numCols = len(data[0])

    def getSize(self):
        return self._size

    def getNumCols(self):
        return self._numCols

    def getWeight(self, aIndex, bIndex):
        return self._data[aIndex][bIndex]

    def hasEdge(self, aIndex, bIndex):
        w = self.getWeight(aIndex, bIndex)
        return w > 0 and w != float('inf')

    def toString(self):
        str = "";
        for y in range(0, self._size):
            for x in range(0, self._numCols):
                str += self._data[y][x].__str__() + ' '
            str += '\n'
        return str


class VectorD:
    def __init__(self, matrix):
        self._data = [0] * matrix.getSize()


class Utils:
    @staticmethod  # sprawdzone
    def array2dFromStr(str):
        str_rows = str.splitlines()
        rows = []
        for row in str_rows:
            if row != "":
                rows.append([int(num) for num in row.split(' ')])
        return rows

    @staticmethod
    def findMaxPlaces2d(array2d):
        ret = 0
        for row in array2d:
            for cell in row:
                ret = max(ret, len(str(cell)))
        return ret

    @staticmethod
    def resize2d(array2d, width, height):
        return [[array2d[y][x] for x in range(width)] for y in range(height)]

    @staticmethod  # sprawdzone
    def subarray2d(array, ax, ay, w, h):
        rows = [[None for x in range(w)] for y in range(h)]
        for y in range(ay, ay + h):
            print ''
            for x in range(ax, ax + w):
                rows[y - ay][x - ax] = array[y][x]
        return rows

    @staticmethod
    def genSymArray(size):
        str2 = """
0 8 6 1 4 5 8 5 1 2 7 6 1 4 4 3 3 2 1 2
8 0 6 5 1 5 8 3 2 0 1 5 2 0 1 1 2 7 5 3
6 6 0 4 8 1 8 4 7 8 8 2 4 0 3 6 4 7 8 2
1 5 4 0 3 5 0 8 5 3 2 2 1 2 6 0 7 0 6 3
4 1 8 3 0 0 4 2 0 4 1 0 5 4 8 5 0 1 4 2
5 5 1 5 0 0 4 0 7 8 0 0 4 6 5 1 1 3 3 0
8 8 8 0 4 4 0 3 8 1 2 0 1 6 6 3 5 7 1 7
5 3 4 8 2 0 3 0 8 7 5 6 5 5 3 7 1 6 0 6
1 2 7 5 0 7 8 8 0 4 2 6 5 1 4 6 0 3 5 8
2 0 8 3 4 8 1 7 4 0 6 2 6 2 3 8 0 3 6 7
7 1 8 2 1 0 2 5 2 6 0 1 8 1 7 0 3 3 4 3
6 5 2 2 0 0 0 6 6 2 1 0 2 4 2 4 8 4 5 3
1 2 4 1 5 4 1 5 5 6 8 2 0 8 5 1 7 1 4 0
4 0 0 2 4 6 6 5 1 2 1 4 8 0 6 7 4 6 6 0
4 1 3 6 8 5 6 3 4 3 7 2 5 6 0 6 4 8 4 6
3 1 6 0 5 1 3 7 6 8 0 4 1 7 6 0 4 5 2 8
3 2 4 7 0 1 5 1 0 0 3 8 7 4 4 4 0 6 4 1
2 7 7 0 1 3 7 6 3 3 3 4 1 6 8 5 6 0 5 3
1 5 8 6 4 3 1 0 5 6 4 5 4 6 4 2 4 5 0 4
2 3 2 3 2 4 7 6 8 7 3 3 0 0 6 8 1 3 4 0
"""
        return Utils.subarray2d(Utils.array2dFromStr(str2), 0, 0, size, size)

    @staticmethod
    def genSymArray2(size):
        b = [[0] * size for i in range(size)]
        from random import randint

        for i in range(size):
            for j in range(i, size):
                if i == j:
                    b[i][j] = 0
                else:
                    b[i][j] = randint(0, 8)
                b[j][i] = b[i][j]
        return b

    @staticmethod
    def getMockup():
        str2d = """
0 8 6 1 4 0 8 5 1 2 7 6 1 4 4 3 3 2 1 2
8 0 6 5 1 5 8 3 2 0 1 5 2 0 1 1 2 7 5 3
6 6 0 4 8 1 8 4 7 8 8 2 4 0 3 6 4 7 8 0
1 5 4 0 3 5 0 8 0 3 2 2 1 2 6 0 7 0 6 3
4 1 8 3 0 0 4 2 0 4 1 0 5 4 8 5 0 1 4 2
0 5 1 5 0 0 4 0 7 8 0 0 4 6 5 1 1 3 3 0
8 8 8 0 4 4 0 3 8 1 2 0 1 6 6 3 5 7 1 7
5 3 4 8 2 0 3 0 8 7 5 6 5 5 3 7 1 6 0 6
1 2 7 0 0 7 8 8 0 4 2 6 5 1 4 6 0 3 5 8
2 0 8 3 4 8 1 7 4 0 6 2 6 2 3 8 0 3 6 7
7 1 8 2 1 0 2 5 2 6 0 1 8 1 7 0 3 3 4 3
6 5 2 2 0 0 0 6 6 2 1 0 2 4 2 4 8 4 5 3
1 2 4 1 5 4 1 5 5 6 8 2 0 8 5 1 7 1 4 0
4 0 0 2 4 6 6 5 1 2 1 4 8 0 6 7 4 6 6 0
4 1 3 6 8 5 6 3 4 3 7 2 5 6 0 6 4 8 4 6
3 1 6 0 5 1 3 7 6 8 0 4 1 7 6 0 4 5 2 8
3 2 4 7 0 1 5 1 0 0 3 8 7 4 4 4 0 6 4 1
2 7 7 0 1 3 7 6 3 3 3 4 1 6 8 5 6 0 5 3
1 5 8 6 4 3 1 0 5 6 4 5 4 6 4 2 4 5 0 4
2 3 0 3 2 0 7 6 8 7 3 3 0 0 6 8 1 3 4 0
"""
        # str2d = """
        # 0 5 8 0
        # 5 0 3 2
        # 8 3 0 1
        # 0 2 1 0
        # """
        return Utils.array2dFromStr(str2d)


def test():
    # str2d = """
    # 0 1 3 0 0 2
    # 1 0 5 1 0 0
    # 3 5 0 2 1 0
    # 0 1 2 0 4 0
    # 0 0 1 4 0 5
    # 2 0 0 0 5 0
    # """
    str2d = """
0 8 6 1 4 0 8 5 1 2 7 6 1 4 4 3 3 2 1 2
8 0 6 5 1 5 8 3 2 0 1 5 2 0 1 1 2 7 5 3
6 6 0 4 8 1 8 4 7 8 8 2 4 0 3 6 4 7 8 0
1 5 4 0 3 5 0 8 0 3 2 2 1 2 6 0 7 0 6 3
4 1 8 3 0 0 4 2 0 4 1 0 5 4 8 5 0 1 4 2
0 5 1 5 0 0 4 0 7 8 0 0 4 6 5 1 1 3 3 0
8 8 8 0 4 4 0 3 8 1 2 0 1 6 6 3 5 7 1 7
5 3 4 8 2 0 3 0 8 7 5 6 5 5 3 7 1 6 0 6
1 2 7 0 0 7 8 8 0 4 2 6 5 1 4 6 0 3 5 8
2 0 8 3 4 8 1 7 4 0 6 2 6 2 3 8 0 3 6 7
7 1 8 2 1 0 2 5 2 6 0 1 8 1 7 0 3 3 4 3
6 5 2 2 0 0 0 6 6 2 1 0 2 4 2 4 8 4 5 3
1 2 4 1 5 4 1 5 5 6 8 2 0 8 5 1 7 1 4 0
4 0 0 2 4 6 6 5 1 2 1 4 8 0 6 7 4 6 6 0
4 1 3 6 8 5 6 3 4 3 7 2 5 6 0 6 4 8 4 6
3 1 6 0 5 1 3 7 6 8 0 4 1 7 6 0 4 5 2 8
3 2 4 7 0 1 5 1 0 0 3 8 7 4 4 4 0 6 4 1
2 7 7 0 1 3 7 6 3 3 3 4 1 6 8 5 6 0 5 3
1 5 8 6 4 3 1 0 5 6 4 5 4 6 4 2 4 5 0 4
2 3 0 3 2 0 7 6 8 7 3 3 0 0 6 8 1 3 4 0
"""
    # str2d = """
    # 0 2 0 6 0
    # 2 0 3 8 5
    # 0 3 0 0 7
    # 6 8 0 0 9
    # 0 5 7 9 0
    # """
    # ==== prepare data ====
    rows = Utils.array2dFromStr(str2d)
    matrix = Matrix(rows)
    # print matrix.toString()
    # print matrix.hasEdge(1, 5)
    # print matrix.getWeight(3, 4)
    Prim.sequential(matrix)


if __name__ == "__main__":
    test()