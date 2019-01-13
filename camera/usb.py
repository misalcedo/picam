import logging
from asyncio import Event, sleep

import aiojobs
import cv2
import imutils
from aiorwlock import RWLock


class UsbCameraAsync:
    """A camera implementation that uses an asynchronous USB-based camera."""

    def __init__(self, source, frames_per_second, orientation, rotation, encoding='.jpg'):
        self.seconds_per_frame = 1 / frames_per_second
        self.orientation = orientation
        self.rotation = rotation
        self.encoding = encoding
        self.source = source

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

            self.video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            await self.tasks.spawn(self.update(app))

    async def update(self, _):
        while await self.is_recording():
            success, frame = self.video_stream.read()
            if success:
                await self.update_frame(frame)
                await sleep(self.seconds_per_frame)
            else:
                logging.debug("Failed to read camera frame.")

    async def is_recording(self):
        return self.video_stream.isOpened()

    async def update_frame(self, frame):
        rotated_frame = await self.rotate_frame(frame)
        flipped_frame = await self.flip_frame(rotated_frame)

        fps = self.video_stream.get(cv2.CAP_PROP_FPS)
        width = self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)

        cv2.putText(flipped_frame, "FPS: {}, Size: ({}, {})".format(fps, width, height), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        encoded, image = await self.encode_frame(flipped_frame)

        if encoded:
            async with self.lock.writer:
                self.frame = image.tobytes()
                self.event.set()
                self.event.clear()
        else:
            logging.debug("Failed to encode camera frame as JPEG.")

    async def encode_frame(self, frame):
        return cv2.imencode(self.encoding, frame)

    async def flip_frame(self, frame):
        if self.orientation:
            return cv2.flip(frame, self.orientation)
        else:
            return frame

    async def rotate_frame(self, frame):
        if self.rotation and self.rotation != 0:
            return imutils.rotate_bound(frame, self.rotation)
        else:
            return frame

    async def __aenter__(self):
        await self.event.wait()
        await self.lock.reader.__aenter__()

        return self.frame

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.lock.reader.__aexit__(exc_type, exc_val, exc_tb)
