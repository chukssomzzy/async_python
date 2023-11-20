# concurrency with generator

import time
from collections import deque
import heapq


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.sleeping = []
        self.sequence = 0

    def __call__(self, cor):
        self.ready.append(cor)

    async def sleep(self, delay):
        """Coroutines put themselves to sleep"""
        deadline = time.time() + delay
        heapq.heappush(self.sleeping, (deadline, self.sequence, self.current))
        self.current = None
        self.sequence += 1
        await switch()

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, cor = self.sleeping.pop(0)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(cor)
            self.current = self.ready.popleft()
            try:
                self.current.send(None)  # next(self.current)
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass


sched = Scheduler()


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


async def countup(n):
    start = 0
    while start < n:
        print("Up", start)
        await sched.sleep(4)
        start += 1


async def countdown(n):
    stop = 0
    while n > stop:
        print("Down", n)
        await sched.sleep(1)
        n -= 1

sched(countup(4))
sched(countdown(20))
sched.run()
