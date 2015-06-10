# coding=utf-8
from environment import *
from point import *
import random


class Master:
    def __init__(self, env):
        """
        :type env: Environment
        """
        self.env = env
        problem = env.problem
        # losuj swoją pod-populację
        subPopulation = self.generatePopulation()
        for epoch in range(problem.numEpoch):  # kolejne przybliżenia
            # dokonaj selekcji
            parents = self.selectParents(subPopulation)
            children = self.__slave__crossover_and_mutate(parents)
            subPopulation = parents + children
            print parents, children
            pass

    def generatePopulation(self):
        problem = self.env.problem
        popSize = problem.subPopulationSize
        population = []
        for i in range(popSize):
            point = Point(random.uniform(problem.x1, problem.x2), random.uniform(problem.y1, problem.y2))
            population.append(point)
        return population

    def selectParents(self, population):

        parents = []
        for i in range(len(population) / 2):
            survived = self.pickRandomPoint(population)
            population.remove(survived)
            parents.append(survived)
        return parents

    def __slave__crossover_and_mutate(self, parents):
        random.shuffle(parents)
        children = []
        for i in range(0, len(parents), 2):
            tpl = self.__slave__crossTwoParents(parents[i], parents[i + 1])
            children.append(tpl[0])
            children.append(tpl[1])
        self.__slave_mutate(random.choice(children))
        return children

    def __slave__crossTwoParents(self, parent1, parent2):
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

    def __slave_mutate(self, point):
        px = point.x
        py = point.y
        # mutacja polega na zamianie x z y i symetrię przez ox i oy
        point.x = self.env.problem.x2 - (py - self.env.problem.x1)
        point.y = self.env.problem.y2 - (px - self.env.problem.y1)

    def pickRandomPoint(self, population):
        # oceń każdy punkt (dystrybuanta oceny, punkt)
        tuplets = []

        evaluations = [self.env.problem.evaluate(point) for point in population]

        minVal = min(evaluations)
        maxVal = max(evaluations)
        spread = abs(maxVal - minVal)  # jak oddalony jest min od max
        offset = -minVal + spread * 0.1  # najmniejsze wartości będą 10x mniej prawdopodobne niz najwieksze
        evalSum = 0
        for point in population:
            evalPt = self.env.problem.evaluate(point) + offset  # dodaj minVal aby nie było ujemnych ocen
            evalSum += evalPt
            tuplets.append((evalSum, point, evalPt))

        randomNumber = random.uniform(0, evalSum)
        # idź od początku listy i sprawdzaj po kolei czy dystrybuanta jest wieksza od losowej liczby
        for triple in tuplets:
            if randomNumber < triple[0]:
                return triple[1]
        raise Exception("pick random point error")

    def getNextMaster(self):
        # za kazym razem przekrec iteracje aby byl nowy sasiad
        # xorowanie
        pass


if __name__ == "__main__":
    def test():
        problem = Problem(lambda x, y: 100 * x + y, -1, 1, -1, 1)
        problem.numEpoch = 100
        env = Environment(0, 1, 0, problem)
        master = Master(env)

    test()