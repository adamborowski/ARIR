import copy


class Matrix:
    def __init__(self, numBlocks, blockSize):
        self.numBlocks = numBlocks
        self.blockSize = blockSize
        self.blockRows = [[None for i in range(numBlocks)] for j in range(numBlocks)]
        pass

    def numFilled(self):
        n = 0
        for row in self.blockRows:
            if row is not None:
                for block in row:
                    if block is not None:
                        n += 1
        return n

    def resize(self, newNumBlocks):
        self.blockRows = Utils.resize2d(self.blockRows, newNumBlocks, newNumBlocks)
        self.numBlocks = newNumBlocks

    def __str__(self):
        restored = Utils.restoreFromBlocks(self.blockRows)

        maxPlaces = Utils.findMaxPlaces2d(restored)
        fmt = '{:>' + str(maxPlaces) + '}'

        ret = ""
        for row in restored:
            ret += ' '.join([fmt.format(cell) for cell in row])
            ret += '\n'
        return ret

    def merge(self, matrix):
        for blockRow in matrix.blockRows:
            if blockRow is not None:
                for block in blockRow:
                    if block is not None:
                        self.setBlock(block)

    def getBlock(self, x, y):
        return self.blockRows[y][x]

    def setBlock(self, block):
        self.blockRows[block.y][block.x] = block
        pass

    def getValue(self, x, y):
        b = self.blockSize
        return self.getBlock(x / b, y / b).getValue(x % b, y % b)

    def setValue(self, x, y, value):
        b = self.blockSize
        self.getBlock(x / b, y / b).setValue(x % b, y % b, value)

    def mutliplyPartialBlock(self, x, y):
        block = self.getBlock(x, y).clone()
        size = self.blockSize
        for blockY in range(size):
            for blockX in range(size):
                # dla kazdego bloku wykonujemy
                sum = 0
                matX = x * self.blockSize + blockX
                matY = y * self.blockSize + blockY

                for i in range(self.numBlocks * self.blockSize):
                    # print '[{},{}] : {} = {}'.format(matX, matY, i, sum)
                    sum += self.getValue(i, matY) * self.getValue(matX, i)
                # print '[{},{} = {}]'.format(matX, matY, sum)
                block.setValue(blockX, blockY, sum)
        self.setBlock(block)
        return block


class Block:
    def clone(self):
        return Block(self.x, self.y, [copy.copy(row) for row in self.data])

    def __init__(self, x, y, data):
        self.x = x
        self.y = y
        self.size = len(data)
        self.data = data

    def __str__(self):
        ret = ""
        for row in self.data:
            ret += '\n'
            ret += ' '.join([str(cell) for cell in row])
        return ret

    def __repr__(self):
        return self.__str__()

    def getValue(self, x, y):
        return self.data[y][x]

    def setValue(self, x, y, value):
        self.data[y][x] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def multiplyBy(self, block):
        size = self.size
        newBlock = Block(self.x, self.y, [[None for i in range(size)] for j in range(size)])
        for x in range(0, size):
            for y in range(0, size):
                sum = 0
                for i in range(0, size):
                    sum += self.getValue(i, y) * block.getValue(x, i)
                newBlock.setValue(x, y, sum)

        return newBlock


class Utils:
    @staticmethod  # sprawdzone
    def subarray2d(array, ax, ay, w, h):
        rows = [[None for x in range(w)] for y in range(h)]
        for y in range(ay, ay + h):
            print ''
            for x in range(ax, ax + w):
                rows[y - ay][x - ax] = array[y][x]
        return rows

    @staticmethod  # sprawdzone
    def array2dFromStr(str):
        str_rows = str.splitlines()
        rows = []
        for row in str_rows:
            if row != "":
                rows.append([int(num) for num in row.split(' ')])
        return rows

    @staticmethod  # sprawdzone
    def makeBlocks(rows, blockSize):
        newRows = []

        for y in range(0, len(rows), blockSize):
            row = []
            newRows.append(row)
            for x in range(0, len(rows[0]), blockSize):
                row.append(Utils.subarray2d(rows, x, y, blockSize, blockSize))
        return newRows

    @staticmethod  # sprawdzone
    def restoreFromBlocks(blockRows):
        numBlocks = len(blockRows)
        blockSize = len(blockRows[0][0])
        realSize = numBlocks * blockSize
        array2d = [[None for i in range(realSize)] for j in range(realSize)]
        for y, row in enumerate(blockRows):
            for x, block in enumerate(row):
                for iy, blockRow in enumerate(block):
                    for ix, blockValue in enumerate(blockRow):
                        array2d[y * blockSize + iy][x * blockSize + ix] = blockValue
        return array2d

    @staticmethod
    def flatten2d(array2d):
        width = len(array2d[0])
        height = len(array2d)
        array = [None for i in range(height * width)]
        for y, row in enumerate(array2d):
            for x, val in enumerate(row):
                array[y * width + x] = val
        return array

    @staticmethod
    def extrudeFlattened(flattened, width):
        height = len(flattened) / width
        array2d = [[None for i in range(width)] for j in range(height)]
        for y in range(height):
            for x in range(width):
                i = y * width + x
                array2d[y][x] = flattened[i]
        return array2d

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
0 5 6 4 5 6 8 9 2
1 0 9 2 3 4 5 6 7
4 3 4 6 5 6 3 4 4
1 1 1 1 2 1 1 0 0
0 0 2 2 2 3 3 4 5
9 0 9 0 9 0 9 3 3
2 3 4 5 6 5 5 5 5
1 3 4 5 4 5 5 5 1
2 2 2 5 6 5 5 2 5
"""
    # ==== prepare data ====
    rows = Utils.array2dFromStr(str2d)
    blockSize = 3
    numBlocks = len(rows) / blockSize
    blockRows = Utils.makeBlocks(rows, blockSize)
    # ==== create matrix ====
    matrix = Matrix(numBlocks, blockSize)
    for y, blockedRow in enumerate(blockRows):
        for x, block in enumerate(blockedRow):
            matrix.setBlock(Block(x, y, block))

    print matrix

    print matrix.getBlock(0, 0).multiplyBy(matrix.getBlock(0, 0))


if __name__ == "__main__":
    test()