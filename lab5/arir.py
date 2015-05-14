# -*- coding: utf-8 -*-
"""
Parallel & Distributed Algorithms - laboratory

Examples:

- Launch 8 workers with default parameter values:
	> python arir.py 8

- Launch 12 workers with custom parameter values:
	> python arir.py 12 --shared-memory-size 128 --delay-connect 2.0 --delay-transmit 0.5 --delay-process 0.75

"""

__author__ = 'moorglade'

import multiprocessing
import time
import datetime
import sys
import argparse
import random
from utils import *
from prim import *


def _parse_args():
    parser = argparse.ArgumentParser()

    # specify command line options
    parser.add_argument(
        'n_workers',
        help='number of workers in the distributed system',
        type=int
    )
    parser.add_argument(
        'n_vertices',
        help='number of vertices of graph',
        type=int
    )
    parser.add_argument(
        '--shared-memory-size',
        help='size of the shared memory array [number of ints]',
        type=int,
        default=16
    )
    parser.add_argument(
        '--delay-connect',
        help='network connection delay [s]',
        type=float,
        default=0.1
    )
    parser.add_argument(
        '--delay-transmit',
        help='network transmission delay [s]',
        type=float,
        default=0.1
    )
    parser.add_argument(
        '--delay-process',
        help='processing delay [s]',
        type=float,
        default=0.1
    )
    parser.add_argument(
        '--noprint',
        help='pass 1 to disable printing',
        type=int,
        default=0
    )

    return argparse.Namespace(**{
        key.replace('-', '_'): value
        for key, value in vars(parser.parse_args()).items()
    })


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

    @property
    def barrier(self):
        return self.__barrier

    @property
    def memory(self):
        return self.__memory


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

    def run(self):
        self.__log('Started.')
        printMe = True  # self.__configuration.noprint == 0
        checkMe = True
        wid = self.__worker_id
        numParts = self.__configuration.n_workers - 1

        matrixSize = self.__configuration.n_vertices
        partSize = matrixSize / numParts
        if wid == 0:
            matrixData = Utils.genSymArray(matrixSize)
            # display info
            if printMe:
                self.__log(
                    "Parallel Prim's algorithm for graph of size {} splitted into {} parts of {} vertices.".format(
                        matrixSize,
                        numParts, partSize))
                print 'The matrix is:\n{}'.format(Matrix(matrixData).toString())
            # seq test
            if checkMe:
                if printMe:
                    print "SEQ:"
                seqMatrix = Matrix(matrixData)
                seqEdgesResult = str(Prim.sequential(seqMatrix))
            if printMe:
                print "PAR:"
            # roześlij wszystkim cząstkowe macierze
            for partNumber in range(numParts):
                partMatrix = Utils.subarray2d(matrixData, partNumber * partSize, 0, partSize, matrixSize)
                self._send(partNumber + 1, [partNumber, partMatrix])
            # rozpocznij algorytm Prima
            for i in range(matrixSize - 1):
                minDist = float('inf')
                u = -1
                # pozbieranie opcji z partów
                for partNumber in range(numParts):
                    indexOfMin, minValue = self._receive(partNumber + 1)[1]
                    if printMe:
                        self.__log(
                            "iter #{} part #{} returned local minimum at {} = {}".format(i, partNumber, indexOfMin,
                                                                                         minValue))
                    if minValue <= minDist:
                        minDist = minValue
                        u = indexOfMin
                # w u mamy indeks który musimy ewentualnie przekazać podczas aktualizcji d[n]s
                # print 'par i={} u={}'.format(i, u)
                for partNumber in range(numParts):
                    self._send(partNumber + 1, [u])  # to pozwoli aktualizować to co mają!!!
            # zbieranie danych
            globalEdges = []
            for partNumber in range(numParts):
                globalEdges += self._receive(partNumber + 1)[1]
            # wyświetlenie wyniku
            if printMe:
                for i in range(1, matrixSize):
                    print "{}->{}".format(ltr(i), ltr(globalEdges[i]))


        else:

            myPartNumber, matrixData = self._receive(0)[1]
            primPart = PrimPart(myPartNumber, matrixData)
            # każdy slave przesyła do rodzica dane o najtańszym połączeniu
            for i in range(matrixSize - 1):
                self._send(0, primPart.getIndexOfMin())
                includedIndex = self._receive(0)[1][0]
                # print 'part {} i {} includedIndex {}'.format(myPartNumber, i, includedIndex)
                primPart.processWeights(i, includedIndex)
            # każdy na koniec odsyła wektor edges
            self._send(0, primPart.edges)
        self.__log('Terminated.')


def main():
    random.seed()
    configuration = _parse_args()
    system = DistributedSystem(configuration)
    system.run()


if __name__ == '__main__':
    sys.exit(main())