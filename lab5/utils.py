from sequential_prim import SequentialPrim


class Matrix:
    def __init__(self, data):
        self._data = data
        self._size = len(data)

    def getSize(self):
        return self._size

    def getWeight(self, aIndex, bIndex):
        return self._data[aIndex][bIndex]

    def hasEdge(self, aIndex, bIndex):
        w = self.getWeight(aIndex, bIndex)
        return w > 0 and w != float('inf')

    def toString(self):
        str = "";
        for y in range(0, self._size):
            for x in range(0, self._size):
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


def test():
    str2d = """
0 1 3 0 0 2
1 0 5 1 0 0
3 5 0 2 1 0
0 1 2 0 4 0
0 0 1 4 0 5
2 0 0 0 5 0
"""
#     str2d = """
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
    SequentialPrim.calculate(matrix)


if __name__ == "__main__":
    test()