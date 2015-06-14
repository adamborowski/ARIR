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
import math


def _parse_args():
    parser = argparse.ArgumentParser()

    # specify command line options
    parser.add_argument(
        'n_workers',
        help='number of workers in the distributed system',
        type=int
    )
    parser.add_argument(
        '--shared-memory-size',
        help='size of the shared memory array [number of ints]',
        type=int,
        default=128
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

    return argparse.Namespace(**{
        key.replace('-', '_'): value
        for key, value in vars(parser.parse_args()).items()
    })


# up to
def bitonic_sort(up, x):
    if len(x) <= 1:
        return x
    else:
        first = bitonic_sort(True, x[:len(x) / 2])
        second = bitonic_sort(False, x[len(x) / 2:])
        return bitonic_merge(up, first + second)


def bitonic_merge(up, x):
    # assume input x is bitonic, and sorted list is returned
    if len(x) == 1:
        return x
    else:
        bitonic_compare(up, x)
        first = bitonic_merge(up, x[:len(x) / 2])
        second = bitonic_merge(up, x[len(x) / 2:])
        return first + second


def bitonic_compare(up, x):
    dist = len(x) / 2
    for i in range(dist):
        if (x[i] > x[i + dist]) == up:
            x[i], x[i + dist] = x[i + dist], x[i]  # swap


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

    def run(self):


        wid = self.__worker_id
        myVal = random.randint(0, 1000)
        self.__shared.memory2[wid] = myVal
        numVals = self.__configuration.n_workers
        numOutRounds = int(math.log(numVals, 2))
        for i in range(1, numOutRounds + 1):
            self.mPrint("round {}".format(i))
            ip = int(math.pow(2, numOutRounds - i))
            for j in range(numOutRounds - i, numOutRounds):
                self.mPrint("\titer {}".format(j))
                numGroups = int(math.pow(2, j))
                groupSize = int(numVals / numGroups)
                groupNr = int(math.floor(wid / (numVals / numGroups)))
                firstInGroup = groupNr * groupSize
                halfSize = int(groupSize / 2)
                middleInGroup = firstInGroup + halfSize
                self.__barrier()
                if j == numOutRounds - i:
                    upMustBeLower = groupNr % 2 == 0
                amIEarlier = wid < middleInGroup
                if amIEarlier:
                    # I am earlier, send and receive
                    target = wid + halfSize
                    self._send(target, [myVal])
                    tmp = self._receive(target)[1][0]
                else:
                    # I am later, receive and send
                    target = wid - halfSize
                    tmp = self._receive(target)[1][0]
                    self._send(target, [myVal])

                rewriteIfLower = (wid < middleInGroup) == upMustBeLower
                print "\t\t{}->{} {}\n".format(wid, target, 'L' if rewriteIfLower else 'G')
                if (tmp < myVal) == rewriteIfLower:
                    myVal = tmp
                elif (tmp > myVal) and not rewriteIfLower:
                    myVal = tmp
                    # print "thread {} round: {} gsize: {} gr {} first: {} target: {}\n".format(wid, i, numGroups, groupNr,
                    # firstInGroup, target)

        self.__shared.memory[wid] = myVal
        # at the end, show results
        self.__barrier()
        if wid == 0:
            sh2 = self.__shared.memory2
            print '================================================================================'
            print 'old / new'
            for i in range(0, numVals):
                print "{:3d}".format(sh2[i]),
            sh = self.__shared.memory
            print ''
            for i in range(0, numVals):
                print "{:3d}".format(sh[i]),
            print "\n"


def main():
    random.seed()
    configuration = _parse_args()
    system = DistributedSystem(configuration)
    system.run()


if __name__ == '__main__':
    sys.exit(main())
