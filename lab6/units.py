class Environment:
    def __init__(self, numMasters, slavesPerMaster):
        self.numMasters = numMasters
        self.slavesPerMaster = slavesPerMaster

    def getMasterThreadId(self, masterId):
        # msss msss msss msss msss
        return masterId * (self.slavesPerMaster + 1)

    def getSlaveThreadId(self, masterId, slaveLocalId):
        # msss msss msss msss msss
        return masterId * (self.slavesPerMaster + 1) + slaveLocalId + 1

    def getMasterProxy(self, masterId):
        return MasterProxy(self.getMasterThreadId(masterId), masterId, self.environment)

    def getSlaveProxy(self, masterId, slaveLocalId):
        return SlaveProxy(self.getSlaveThreadId(masterId, slaveLocalId))


class UnitProxy:
    def __init__(self, threadId, environment):
        self.threadId = threadId
        self.environment = environment


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

