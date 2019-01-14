import asyncio

from aiorwlock import RWLock


class Passport:
    def __init__(self, loop=asyncio.get_event_loop()):
        self.loop = loop
        self.lock = RWLock()
        self.stamps = {}
        self.start = loop.time()

    async def stamp(self, stamp):
        before = await self.last_time(stamp)
        now = await self.latest_time(stamp)

        return now - before

    async def latest_time(self, stamp):
        async with self.lock.writer:
            now = self.loop.time()
            self.stamps[stamp] = now
            return now

    async def last_time(self, stamp):
        async with self.lock.reader:
            return self.stamps.get(stamp, self.start)
