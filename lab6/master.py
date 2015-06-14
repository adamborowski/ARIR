# coding=utf-8
from environment import *
from point import *
import random
from utils import Utils
from utils import Navigator


class Master:
    def __init__(self, env):
        """
        :type env: Environment
        """
        self.env = env
        self.masterProxy = env.getProxyByThreadId(env.threadId)
        self.nav = Navigator(Utils.log2(env.numMasters), self.masterProxy.masterId)
        problem = env.problem
        # losuj swoją pod-populację

        subPopulation = self.generatePopulation()

        for epoch in range(problem.numEpoch):
            parents = self.selectParents(subPopulation)
            random.shuffle(parents)  # dobieramy losowo punkty w part (para to sąsiednie elementy listy)
            parentsChunked = Utils.splitList(parents, self.env.slavesPerMaster)
            for i in range(self.env.slavesPerMaster):
                self.env.worker._send(self.masterProxy.getSlaveProxy(i).threadId, parentsChunked[i])

            children = []
            for i in range(self.env.slavesPerMaster):
                slaveThreadId, slaveChildren = self.env.worker._receive()
                children += slaveChildren
            subPopulation = parents + children

            # co kilka epok następuje ERA
            if epoch % env.interchargeStep == 0:
                nextMaster = self.nav.getNext()
                myMaster = self.masterProxy.masterId
                nextMasterThreadId = self.env.getMasterThreadId(nextMaster)
                myMasterThreadId = self.env.getMasterThreadId(myMaster)
                pointSent = self.getBestPoint(subPopulation)
                # założenie, że master o mniejszym numerze zaczyna wysyłanie
                if myMaster < nextMaster:  # my jestesmy pierwszi - najpierw wyslijmy
                    self.env.worker._send(nextMasterThreadId, [pointSent])
                    (thId, data) = self.env.worker._receive()
                    pointReceived = data[0]
                else:  # my jestesmy o wiekszym numerze - najpierw odbierz
                    (thId, data) = self.env.worker._receive()
                    pointReceived = data[0]
                    self.env.worker._send(nextMasterThreadId, [pointSent])

                self.echo("intercharge {} <> {} / sent {} recv {}\n".format(self.masterProxy.masterId, nextMaster,
                                                                            pointSent,
                                                                            pointReceived))

                # teraz wywal losowy punkt populacji i wstaw ten otrzymany

                # pointToRemove = random.choice(subPopulation)
                # subPopulation.remove(pointToRemove)
                # subPopulation.append(pointReceived)

        # endfor population
        maxPoint = self.getBestPoint(subPopulation)

        self.echo("subPopulation({}) best =({:.2f},{:.2f},{:.2f})".format(len(subPopulation),
                                                                          env.problem.evaluate(maxPoint),
                                                                          maxPoint.x, maxPoint.y))

    def generatePopulation(self):
        problem = self.env.problem
        popSize = problem.subPopulationSize
        population = []
        for i in range(popSize):
            point = Point(random.uniform(problem.x1, problem.x2), random.uniform(problem.y1, problem.y2))
            population.append(point)
        return population

    def echo(self, s):
        print "{:02d} [MASTER {}] {}".format(self.env.threadId, self.masterProxy.masterId, s)

    def selectParents(self, population):

        parents = []
        for i in range(len(population) / 2):
            survived = self.pickRandomPoint(population)
            population.remove(survived)
            parents.append(survived)

        # print self.env.problem.evalArrayStr(tmp), '\n->\n', self.env.problem.evalArrayStr(parents)
        return parents

    def getBestPoint(self, population):
        ev = 0
        best = None
        for point in population:
            pointEv = self.env.problem.evaluate(point)
            if pointEv > ev:
                ev = pointEv
                best = point
        return best

    def pickRandomPoint(self, population):
        # oceń każdy punkt (dystrybuanta oceny, punkt)
        tuplets = []

        evaluations = [self.env.problem.evaluate(point) for point in population]

        minVal = min(evaluations)
        maxVal = max(evaluations)
        spread = abs(maxVal - minVal)  # jak oddalony jest min od max
        offset = -minVal + spread * 0.1  # najmniejsze wartości będą 10x mniej prawdopodobne niz najwieksze
        offset = 0  # zabezpieczenie gdy wszystkie maja taka sama wage
        evalSum = 0
        for point in population:
            evalPt = self.env.problem.evaluate(point) + offset  # dodaj minVal aby nie było ujemnych ocen
            evalSum += evalPt
            tuplets.append((evalSum, point, evalPt))

        randomNumber = random.uniform(0, evalSum)
        # idź od początku listy i sprawdzaj po kolei czy dystrybuanta jest wieksza od losowej liczby
        for triple in tuplets:
            if randomNumber <= triple[0]:
                return triple[1]

        raise Exception("pick random point error {} ".format(len(population)))

    def getNextMaster(self):
        # za kazym razem przekrec iteracje aby byl nowy sasiad
        # xorowanie
        pass


if __name__ == "__main__":
    from math import sin, cos, pow

    def test():
        # problem = Problem(lambda x, y: 0.1 * x + 1000 * y, 0, 1, 0, 1)

        def fn(x, y):
            return (sin(2 * x - 3) * cos(-x + pow(y, 2) - 2) + 3) * (pow((-x + 4), 2) + pow(2 * y - 5, 2) + 1)

        problem = Problem(fn, 0, 10, 0, 10)

        problem.numEpoch = 10
        env = Environment(0, 1, 0, problem)
        problem.subPopulationSize = 1000
        master = Master(env)

    test()
