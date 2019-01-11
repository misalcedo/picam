import logging
import threading
import time

from aiorwlock import RWLock
from asyncio import Event, sleep
import cv2


from camera.camera import Camera
from camera.frames import LatestFrame


class UsbCamera(Camera):
    """A camera implementation that uses a USB-based camera."""

    def __init__(self):
        self.video_stream = cv2.VideoCapture(0)
        self.frame = LatestFrame()
        self.thread = threading.Thread(target=self.capture, args=())
        self.seconds_per_frame = 1 / 24

    def record(self):
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.video_stream.release()

    def frames(self):
        return self.frame

    def capture(self):
        while self.video_stream.isOpened():
            success, frame = self.video_stream.read()
            if success:
                encoded, image = cv2.imencode('.jpg', cv2.flip(frame, -1))
                if encoded:
                    self.frame.update(image.tobytes())

                time.sleep(self.seconds_per_frame)


class UsbCameraAsync:
    """A camera implementation that uses an asynchronous USB-based camera."""

    def __init__(self, source=0, frames_per_second=24, orientation=-1):
        self.seconds_per_frame = 1 / frames_per_second
        self.orientation = orientation
        self.video_stream = cv2.VideoCapture(source)
        self.event = Event()
        self.lock = RWLock()
        self.frame = None

    async def is_recording(self):
        return self.video_stream.isOpened()

    async def record(self, app):
        while await self.is_recording():
            success, frame = self.video_stream.read()
            if success:
                await self.encode_frame(frame)
                await sleep(self.seconds_per_frame)
            else:
                logging.debug("Failed to read camera frame.")

    async def encode_frame(self, frame):
        encoded, image = cv2.imencode('.jpg', await self.flip_frame(frame))

        if encoded:
            async with self.lock.writer:
                self.frame = image.tobytes()
                self.event.set()
                self.event.clear()
        else:
            logging.debug("Failed to encode camera frame as JPEG.")

    async def flip_frame(self, frame):
        return cv2.flip(frame, self.orientation)

    async def stop(self, app):
        self.video_stream.release()

    async def __aenter__(self):
        await self.event.wait()
        await self.lock.reader.__aenter__()

        return self.frame

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.lock.reader.__aexit__(exc_type, exc_val, exc_tb)
