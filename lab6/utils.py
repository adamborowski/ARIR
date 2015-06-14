__author__ = 'adam'
import math


# noinspection PyClassHasNoInit
class Utils:
    @staticmethod
    def splitList(list, count):
        l = len(list)
        chunkSize = int(math.ceil(float(l) / float(count)))
        lists = []
        for i in range(count):
            lists.append(list[i * chunkSize:(i + 1) * chunkSize])
        return lists

    @staticmethod
    def log2(x):
        return math.log(x) / math.log(2)


class Navigator:
    def __init__(self, cycleCount, nodeId):
        self.cycleCount = cycleCount
        self.nodeId = nodeId
        self.cycle = 0

    def getNeigh(self, node, cycle):
        return node ^ int(math.pow(2, cycle))

    def getNext(self):
        ret = self.getNeigh(self.nodeId, self.cycle)
        self.cycle += 1
        if self.cycle == self.cycleCount:
            self.cycle = 0
        return ret
