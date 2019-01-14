import logging
from asyncio import Event

import aiojobs
import cv2
from aiorwlock import RWLock

from camera.frame import Processor


class UsbCameraAsync:
    """A camera implementation that uses an asynchronous USB-based camera."""

    def __init__(self, size, source, processor):
        self.source = source
        self.width, self.height = size

        self.frame_processor = Processor(encoding='.jpg', **processor)
        self.event = Event()
        self.lock = RWLock()

        self.video_stream = None
        self.tasks = None
        self.frame = None

    async def stop(self, _):
        await self.tasks.close()
        await self.release_video()

        self.tasks = None
        self.video_stream = None

    async def release_video(self):
        self.video_stream.release()

    async def record(self, app):
        if not self.tasks:
            self.video_stream = cv2.VideoCapture(self.source)
            self.tasks = await aiojobs.create_scheduler()

            self.video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            await self.tasks.spawn(self.update(app))

    async def update(self, _):
        while await self.is_recording():
            success, frame = self.video_stream.read()
            if success:
                await self.update_frame(frame)
            else:
                logging.debug("Failed to read camera frame.")

    async def is_recording(self):
        return self.video_stream.isOpened()

    async def update_frame(self, frame):
        encoded, image = await self.frame_processor.process(frame)

        if encoded:
            async with self.lock.writer:
                self.frame = image.tobytes()
                self.event.set()
                self.event.clear()
        else:
            logging.debug("Failed to encode camera frame as JPEG.")

    async def __aenter__(self):
        await self.event.wait()
        await self.lock.reader.__aenter__()

        return self.frame

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.lock.reader.__aexit__(exc_type, exc_val, exc_tb)
