import logging
import pathlib
from asyncio import Event, get_event_loop, Queue
from datetime import datetime
from os.path import join

import aiofiles
import aiojobs
from aiorwlock import RWLock

from camera.frame import Processor
from video.usb import UsbVideo


def read(video):
    return video.read()


class UsbCameraAsync:
    """A camera implementation that uses an asynchronous USB-based camera."""

    def __init__(self, orientation, rotation, size, source, processor, clips):
        self.source = source
        self.clips_path = clips
        self.width, self.height = size

        self.frame_processor = Processor(orientation=orientation, rotation=rotation, encoding='.jpg', **processor)
        self.event = Event()
        self.lock = RWLock()
        self.loop = get_event_loop()

        self.queue = Queue(loop=self.loop)

        self.reader = None
        self.tasks = None
        self.frame = None

    async def stop(self, _):
        await self.tasks.close()

        self.reader.stop()
        self.tasks = None

    async def record(self, app):
        if self.tasks is None:
            self.tasks = await aiojobs.create_scheduler()
            self.reader = UsbVideo((self.width, self.height), self.source)

            self.reader.start()

            await self.tasks.spawn(self.read())
            await self.tasks.spawn(self.update(app))

    async def read(self):
        while await self.is_recording():
            frame = await self.loop.run_in_executor(None, self.reader.frame)
            if frame is not None:
                await self.queue.put(frame)

    async def is_recording(self):
        return self.reader.is_readable()

    async def update(self, _):
        while await self.is_recording():
            frame = await self.queue.get()
            await self.update_frame(frame)

    async def update_frame(self, frame):
        encoded, motion_detected, image = await self.frame_processor.process(frame)

        if encoded:
            image_bytes = image.tobytes()

            async with self.lock.writer:
                self.frame = image_bytes
                self.event.set()
                self.event.clear()

            if motion_detected:
                await self.tasks.spawn(self.save_image(image_bytes))
        else:
            logging.debug("Failed to encode camera frame as JPEG.")

    async def save_image(self, image):
        now = datetime.now()
        folder = "-".join([str(now.year), str(now.month), str(now.day)])
        filename = "%d-%d.jpg" % (now.minute, now.microsecond)
        path = join(self.clips_path, folder, str(now.hour))

        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(join(path, filename), mode='wb') as f:
            f.write(image)

    async def __aenter__(self):
        await self.event.wait()
        await self.lock.reader.__aenter__()

        return self.frame

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.lock.reader.__aexit__(exc_type, exc_val, exc_tb)
