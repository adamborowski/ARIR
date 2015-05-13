# -*- coding: utf-8 -*-
__author__ = 'moorglade'

import multiprocessing
import time
import datetime
import sys
import argparse
import random
import math
from matrix import *


def log2(x):
    return math.log(x) / math.log(2)


def _parse_args():
    parser = argparse.ArgumentParser()

    # specify command line options
    parser.add_argument('n_workers', help='number of 2d blocks: for 3x3 you must pass 9', type=int)
    parser.add_argument('delay_connect', help='network connection delay [s]', type=float)
    parser.add_argument('delay_transmit', help='network transmission delay [s]', type=float)
    parser.add_argument('delay_process', help='processing delay [s]', type=float)
    parser.add_argument(
        '--shared-memory-size',
        help='size of the shared memory array [number of ints]',
        type=int,
        default=128
    )
    parser.add_argument(
        '--noprint',
        help='disable printing',
        type=int,
        default=0
    )
    x = parser.parse_args()

    x.old_n_workers = x.n_workers
    x.n_workers = int(math.pow(math.ceil(math.pow(2, math.ceil(log2(math.sqrt(x.n_workers))))), 2))
    print "dla {} komórek wyliczyłem workerów: {}".format(x.old_n_workers, x.n_workers)
    return x


class DistributedSystem(object):
    def __init__(self, configuration):
        object.__init__(self)

        shared = SharedState(configuration.n_workers, configuration.shared_memory_size)
        network = Network(configuration)

        self.__workers = [
            Worker(worker_id, configuration, shared, network.get_endpoint(worker_id))
            for worker_id in range(configuration.n_workers)
        ]

    def run(self):
        print 'Launching {} workers...'.format(len(self.__workers))
        start = datetime.datetime.now()

        for worker in self.__workers:
            worker.start()

        print 'Waiting for the workers to terminate...'
        for worker in self.__workers:
            worker.join()

        stop = datetime.datetime.now()
        print 'All workers terminated.'

        print 'Processing took {} seconds.'.format((stop - start).total_seconds())


class SharedState(object):
    def __init__(self, n_workers, shared_memory_size):
        object.__init__(self)
        self.__barrier = Barrier(n_workers)
        self.__memory = multiprocessing.Array('i', shared_memory_size)
        self.__memory2 = multiprocessing.Array('i', shared_memory_size)

    @property
    def barrier(self):
        return self.__barrier

    @property
    def memory(self):
        return self.__memory

    @property
    def memory2(self):
        return self.__memory2


class Barrier(object):
    def __init__(self, n):
        object.__init__(self)
        self.__counter = multiprocessing.Value('i', 0, lock=False)
        self.__n = n
        self.__condition = multiprocessing.Condition()

    def wait(self):
        with self.__condition:
            self.__counter.value += 1

            if self.__counter.value == self.__n:
                self.__counter.value = 0
                self.__condition.notify_all()

            else:
                self.__condition.wait()


class SharedMemory(object):
    def __init__(self, shared_memory_size):
        object.__init__(self)
        self.__array = multiprocessing.Array('i', shared_memory_size)


class Network(object):
    any_id = -1

    def __init__(self, configuration):
        object.__init__(self)
        channels = [NetworkChannel(configuration) for _ in range(configuration.n_workers)]
        self.__endpoints = [NetworkEndpoint(channel_id, channels) for channel_id in range(configuration.n_workers)]

    def get_endpoint(self, index):
        return self.__endpoints[index]


class NetworkChannel(object):
    def __init__(self, configuration):
        self.__configuration = configuration

        self.__source_id = multiprocessing.Value('i', Network.any_id, lock=False)
        self.__queue = multiprocessing.Queue(maxsize=1)
        self.__enter_lock = multiprocessing.Lock()
        self.__exit_lock = multiprocessing.Lock()
        self.__enter_lock.acquire()
        self.__exit_lock.acquire()

    def send(self, source_id, data):
        while True:
            self.__enter_lock.acquire()

            if self.__source_id.value in [source_id, Network.any_id]:
                self.__source_id.value = source_id
                self.__queue.put(data)
                time.sleep(self.__configuration.delay_connect + len(data) * self.__configuration.delay_transmit)
                self.__exit_lock.release()
                break

            else:
                self.__enter_lock.release()

    def receive(self, source_id=Network.any_id):
        self.__source_id.value = source_id

        self.__enter_lock.release()
        data = self.__queue.get()
        self.__exit_lock.acquire()

        return self.__source_id.value, data


class NetworkEndpoint(object):
    def __init__(self, channel_id, channels):
        self.__channels = channels
        self.__my_id = channel_id
        self.__my_channel = self.__channels[self.__my_id]

    def send(self, destination_id, data):
        if destination_id == self.__my_id:
            raise RuntimeError('Worker {} tried to send data to itself.'.format(self.__my_id))

        self.__channels[destination_id].send(self.__my_id, data)

    def receive(self, worker_id=Network.any_id):
        return self.__my_channel.receive(worker_id)


# noinspection PyPep8Naming
class Worker(multiprocessing.Process):
    def __init__(self, worker_id, configuration, shared, network_endpoint):
        multiprocessing.Process.__init__(self)

        self.__worker_id = worker_id
        self.__configuration = configuration
        self.__shared = shared
        self.__network_endpoint = network_endpoint

    @property
    def __n_workers(self):
        return self.__configuration.n_workers

    def __barrier(self):
        self.__shared.barrier.wait()

    def _send(self, worker_id, data):
        self.__network_endpoint.send(worker_id, data)

    def _receive(self, worker_id=Network.any_id):
        return self.__network_endpoint.receive(worker_id)

    @staticmethod
    def __generate_random_data(length):
        return [random.randint(-2048, 2048) for _ in range(length)]

    def __log(self, message):
        print '[WORKER {}] {}'.format(self.__worker_id, message)

    def __process(self, data):
        # simulates data processing delay by sleeping
        time.sleep(len(data) * self.__configuration.delay_process)


    def mPrint(self, msg):
        self.__barrier()
        if self.__worker_id == 0:
            print msg

    @staticmethod
    def __generate_random_data(length):
        return [random.randint(-2048, 2048) for _ in range(length)]

    def getNeigh(self, node, iter):
        return node ^ int(math.pow(2, iter))

    def genBlock(self):

        myId = self.__worker_id
        x = myId % self.matrix.numBlocks
        y = myId / self.matrix.numBlocks

        if x < self.numBlocks and y < self.numBlocks:
            data = [[random.randint(0, 6) for i in range(3)] for j in range(3)]
            # data = [[1 for i in range(3)] for j in range(3)]
        else:
            data = [[0 for i in range(3)] for j in range(3)]

        # data = [[[x,y] for i in range(3)] for j in range(3)]
        return Block(x, y, data)


    def run(self):

        printing = self.__configuration.noprint != 1


        # print '[WORKER {}] started.'.format(self.__worker_id)

        numProc = self.__n_workers
        numIter = int(log2(numProc))
        num_cells = self.__configuration.old_n_workers
        numBlocks = self.numBlocks = int(math.sqrt(num_cells))

        numBlocksForCommunication = int(math.sqrt(numProc))
        # TODO: implement this method
        myId = self.__worker_id
        self.matrix = Matrix(numBlocksForCommunication, 3)
        block = self.genBlock()
        self.matrix.setBlock(block)  # włóż wygenerowany blok do macierzy

        for i in range(0, numIter):
            # print 'ROUND: {}'.format(i)
            next = self.getNeigh(myId, i)
            if next < numProc:
                if myId < next:  # jestesmy lewy
                    self._send(next, [self.matrix])
                    # odbieramy
                    source_id, data = self._receive()
                    self.matrix.merge(data[0])
                    # print '{} received from {}: {}'.format(myId,source_id, received)

                else:
                    # odbieramy
                    source_id, data = self._receive()
                    # print '{} received from {}: {}'.format(myId,source_id, received)
                    self._send(next, [self.matrix])
                    self.matrix.merge(data[0])

        if printing:
            self.__log("num filled: {}\n".format(self.matrix.numFilled()))


        # koniec komunikacji, teraz zaczyna się wymnażanie
        self.matrix.resize(numBlocks)  # nie chcemy komórek które były konieczne tylko do komunikacji hiperkostki

        self.__barrier()  # teraz wszyscy mają macierz, można niezależnie liczyć blocki

        if myId == 0:
            if printing:
                print "\n-----------------\nMatrix size: {0} x {0}\nMatrix (seen as root) is:\n{1}".format(
                    self.matrix.numBlocks, self.matrix)

        if myId < num_cells:
            # print '[WORKER {}] terminated. Data: {}\n'.format(self.__worker_id, self.allBlocks)

            # tutaj mnozymy macierz
            myX = myId % self.matrix.numBlocks
            myY = myId / self.matrix.numBlocks

            # każdy jest odpowiedzialny za przemnożenie jednego bloku

            # print 'thread {} / {} [{},{}]'.format(myId, num_cells, myX, myY)
            block = self.matrix.mutliplyPartialBlock(myX, myY)

            if myId != 0:
                self._send(0, [block])
            else:
                for i in range(1, num_cells):
                    source_id, data = self._receive()
                    self.matrix.setBlock(data[0])
                if printing:
                    print '-------------------------'
                    print self.matrix


def main():
    random.seed()
    configuration = _parse_args()
    system = DistributedSystem(configuration)
    system.run()


if __name__ == '__main__':
    sys.exit(main())