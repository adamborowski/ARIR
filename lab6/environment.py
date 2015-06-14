# coding=utf-8
class Problem:
    def __init__(self, func, x1, x2, y1, y2):
        self.func = func
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.numEpoch = 3  # można zmienić zanim odpali się Environment
        self.subPopulationSize = 8  # można zmienić zanim odpali się Environment

    def evaluate(self, point):
        return self.func(point.x, point.y)

    def evalArrayStr(self, points):
        return ["[{:.2f} {:.2f} {:.2f}]".format(self.evaluate(point), point.x, point.y) for point in points]


class Environment:
    def __init__(self, numMasters, slavesPerMaster, threadId, problem):
        self.numMasters = numMasters
        self.slavesPerMaster = slavesPerMaster
        self.threadId = threadId
        self.problem = problem

    def getMasterThreadId(self, masterId):
        # msss msss msss msss msss
        return masterId * (self.slavesPerMaster + 1)

    def getSlaveThreadId(self, masterId, slaveLocalId):
        # msss msss msss msss msss
        return masterId * (self.slavesPerMaster + 1) + slaveLocalId + 1

    def getMasterProxy(self, masterId):
        return MasterProxy(self.getMasterThreadId(masterId), masterId, self)

    def getSlaveProxy(self, masterId, slaveLocalId):
        return SlaveProxy(self.getSlaveThreadId(masterId, slaveLocalId), masterId, slaveLocalId, self)

    def getProxyByThreadId(self, threadId):
        nodesPerMaster = self.slavesPerMaster + 1
        masterId = int(threadId / nodesPerMaster)
        slaveId = threadId % nodesPerMaster - 1
        print "master: {} slave: {}".format(masterId, slaveId)
        if slaveId == -1:
            return self.getMasterProxy(masterId)
        return self.getSlaveProxy(masterId, slaveId)


class UnitProxy:
    def __init__(self, threadId, environment):
        self.threadId = threadId
        self.environment = environment

    def getThreadId(self):
        return self.threadId


class MasterProxy(UnitProxy):
    def __init__(self, threadId, masterId, environment):
        UnitProxy.__init__(self, threadId, environment)
        self.masterId = masterId

    def getSlaveProxy(self, slaveLocalId):
        return self.environment.getSlaveProxy(self.masterId, slaveLocalId)


class SlaveProxy(UnitProxy):
    def __init__(self, threadId, masterId, slaveLocalId, environment):
        self.masterId = masterId
        self.slaveLocalId = slaveLocalId
        UnitProxy.__init__(self, threadId, environment)
        pass


if __name__ == "__main__":
    def test():
        env = Environment(8, 10, 0, Problem(lambda x, y: x - y, -1, 1, -1, 1))
        master0 = env.getMasterProxy(0)
        master1 = env.getMasterProxy(1)
        master2 = env.getMasterProxy(2)
        master3 = env.getMasterProxy(3)
        slave00 = master0.getSlaveProxy(0)
        slave01 = master0.getSlaveProxy(1)
        slave10 = master1.getSlaveProxy(0)

        print master0.threadId
        print master1.threadId
        print master2.threadId
        print master3.threadId
        print slave00.threadId
        print slave01.threadId
        print slave10.threadId

        print env.getProxyByThreadId(11)

    test()
