"""Build Your Own Async"""
import heapq
import time
import threading
import queue
import dis
from collections import deque
# import pdb
# pdb.set_trace()

# Scheduler
# the function to a scheduler ends or return immediately while still scheduling
# another instance of the function to run immediately after it done running.
# the function would only end when it meets a particular condition


#
#
# def countdown(n):
#     """just count down arg"""
#     while n > 0:
#         print("Down", n)
#         time.sleep(1)
#         n -= 1
#
#
# def countup(stop):
#     x = 0
#     while x < stop:
#         print("Up", x)
#         time.sleep(1)
#         x += 1
#

# Sequential execution
# countdown(5)
# countup(5)

# concurrent execution
# classic solution: use threads

# threading.Thread(target=countdown, args=(5,)).start()
# threading.Thread(target=countup, args=(5,)).start()

# How do you do concurrency without thread
# gotchas
# thread are hard to kill, control and manage

# let try run countDown and countUp without threading


# problem: How to achieve concurrency without threads?
# issue: find a way to switch back and forth between task (context switching)

# Approach


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.sleeping = []
        self.sequence = 0
        self.current = None

    def __call__(self, func, delay=0):
        if delay:
            self.sequence += 1
            deadline = time.time() + delay
            heapq.heappush(self.sleeping, (deadline, self.sequence, func))
        else:
            self.ready.append(func)

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # find the nearest deadline
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)
            while self.ready:
                func = self.ready.popleft()
                func()

    def new_task(self, cor):
        self.ready.append(Task(cor))

    async def sleep(self, delay):
        self.__call__(self.current, delay)
        self.current = None
        await switch()


class Task:
    def __init__(self, cor):
        self.cor = cor

    def __call__(self):
        try:
            sched.current = self
            self.cor.send(None)
            if sched.current:
                sched.ready.append(Task(self.cor))
        except StopIteration:
            pass

#
# sched = Scheduler()
#

# def countdown(n):
#     if n > 0:
#         print('Down', n)
#         # time.sleep(1)  # Blocking call (nothing else can run)
#         sched(lambda: countdown(n - 1), 1)
#
#
# def countup(stop, x=0):
#     if x < stop:
#         print('Up', x)
#         sched(lambda: countup(stop, x + 1), 4)
#
#
# sched(lambda: countdown(20))
# sched(lambda: countup(5))
# sched.run()
#

# Corner Cases

# let say you have a function f and g

# def f():
#   pass
#
# def g():
#   pass
#
# sleeping = [(f, 2), (g, 2)]  # same deadline. Two functions
# sleeping.sort()
# Error:
#    TypeError: '<' not supported instances of 'function' and 'function'
# solution:
#    add a sequence to the heapq argumement for tie breaking so
# function never get compared

# Producer - Consumer problem
# Challenge: How to implement the same functionality, but no threads
# Use Scheduler
# yield scheduler

# class Scheduler:
#     def __init__(self):
#         self.ready = deque()
#         self.sleeping = []
#         self.sequence = 0
#
#     def new_task(self, cor):
#         self.ready.append(cor)
#
#     async def sleep(self, delay):
#         """Coroutines put themselves to sleep"""
#         deadline = time.time() + delay
#         self.sequence += 1
#         heapq.heappush(
#             self.sleeping, (deadline, self.sequence, self.current))
#         self.current = None
#         await switch()
#
#     def run(self):
#         while self.ready or self.sleeping:
#             if not self.ready:
#                 deadline, _, cor = self.sleeping.pop(0)
#                 delta = deadline - time.time()
#                 if delta > 0:
#                     time.sleep(delta)
#                 self.ready.append(cor)
#             self.current = self.ready.popleft()
#             try:
#                 self.current.send(None)  # next(self.current)
#                 if self.current:
#                     self.ready.append(self.current)
#             except StopIteration:
#                 pass
#


sched = Scheduler()


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


class QueueClosed(Exception):
    pass


class AsyncQueue:
    """async queue"""

    def __init__(self):
        self.items = deque()
        self.waiting = deque()
        self._closed = False

    def close(self):
        self._closed = True
        if self.waiting:
            sched.ready.append(self.waiting.popleft())

    async def put(self, item):
        """Put an item on the queue"""
        if not self._closed:
            self.items.append(item)
        if self.waiting:
            sched.ready.append(self.waiting.popleft())

    async def get(self):
        """Put an item on the queue"""
        while not self.items:
            if self._closed:
                raise QueueClosed()
            self.waiting.append(sched.current)
            sched.current = None
            await switch()
        return self.items.popleft()


async def producer(q, n):
    """Produce events"""
    start = 0
    while start < n:
        print("Producing", start)
        await q.put(start)
        await sched.sleep(0.5)
        start += 1
    q.close()


async def consumer(q):
    """Consume events"""
    try:
        while True:
            item = await q.get()
            print("Cosumed by 0 item", item)
            await sched.sleep(1)
    except QueueClosed:
        print("Consumer Done")


async def consumer_1(q):
    """Consume events"""
    try:
        while True:
            item = await q.get()
            print("Cosumed by 1 item", item)
            await sched.sleep(1)
    except QueueClosed:
        print("Consumer Done")


async def consumer_2(q):
    """Consume events"""
    try:
        while True:
            item = await q.get()
            print("Cosumed by 2 item", item)
            await sched.sleep(1)
    except QueueClosed:
        print("Consumer Done")
q = AsyncQueue()
sched.new_task(producer(q, 100))
sched.new_task(consumer(q))
sched.new_task(consumer_1(q))
sched.new_task(consumer_2(q))
dis.dis(sched.run())
