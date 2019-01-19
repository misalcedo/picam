import time

from aiorwlock import RWLock


class Passport:
    def __init__(self):
        self.lock = RWLock()
        self.stamps = {}
        self.start = time.perf_counter()

    async def stamp(self, stamp):
        before = await self.last_time(stamp)
        now = await self.latest_time(stamp)

        return now - before

    async def latest_time(self, stamp):
        async with self.lock.writer:
            now = time.perf_counter()
            self.stamps[stamp] = now
            return now

    async def last_time(self, stamp):
        async with self.lock.reader:
            return self.stamps.get(stamp, self.start)
