# coding=utf-8
from environment import *
from point import *
import random


class Slave:
    def __init__(self, env):
        """
        :type env: Environment
        """
        self.env = env
        self.slaveProxy = env.getProxyByThreadId(env.threadId)
        self.masterProxy = env.getMasterProxyForSlave(env.threadId)
        problem = env.problem
        for epoch in range(problem.numEpoch):
            parents = self.receiveParents()

            children = self.crossover_and_mutate(parents)
            self.responseChildren(children)

    def crossover_and_mutate(self, parents):
        # random.shuffle(parents)
        children = []
        numParents = len(parents)
        for i in range(0, numParents, 2):
            if i + 1 == numParents:
                children.append(parents[i])
            else:
                tpl = self.crossTwoParents(parents[i], parents[i + 1])
                children.append(tpl[0])
                children.append(tpl[1])
        self.mutate(random.choice(children))
        return children

    def crossTwoParents(self, parent1, parent2):
        # pierwszy punkt jest średnim wektorem
        # drugi punkt jest średnią tylko jednego wymiaru (x lub y)
        # przy zachowaniu pozostałej współrzędnej (rodzic 1 lub rodzic 2)
        p1 = (parent1 + parent2) / 2
        r = random.random()
        if r < 0.25:
            p2 = Point((parent1.x + parent2.x) / 2, parent1.y)
        elif r < 0.5:
            p2 = Point((parent1.x + parent2.x) / 2, parent2.y)
        elif r < 0.75:
            p2 = Point(parent1.x, (parent1.y + parent2.y) / 2)
        else:
            p2 = Point(parent2.x, (parent1.y + parent2.y) / 2)
        return p1, p2

    def mutate(self, point):
        px = point.x
        py = point.y
        # mutacja polega na zamianie x z y i symetrię przez ox i oy
        point.x = self.env.problem.x2 - (py - self.env.problem.x1)
        point.y = self.env.problem.y2 - (px - self.env.problem.y1)

        if random.random() < 0.95:
            point.x = random.uniform(self.env.problem.x1, self.env.problem.x2)
            point.y = random.uniform(self.env.problem.y1, self.env.problem.y2)

    def receiveParents(self):

        sender, data = self.env.worker._receive(self.masterProxy.threadId)
        # self.echo("receive part {}".format(data))
        return data

    def responseChildren(self, children):
        # self.echo("response part {}".format(children))
        self.env.worker._send(self.masterProxy.threadId, children)

    def echo(self, s):
        print "{:02d} [SLAVE {}.{}] {}\n".format(self.env.threadId, self.masterProxy.masterId,
                                               self.slaveProxy.slaveLocalId,
                                               s)
