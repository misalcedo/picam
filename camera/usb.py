from camera.camera import Camera
from camera.frames import LatestFrame
import cv2
import asyncio
from contextlib import suppress


class Periodic:
    """Periodically executes a task."""
    def __init__(self, func, time):
        self.func = func
        self.time = time
        self.is_started = False
        self._task = None

    async def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            await asyncio.sleep(self.time)
            self.func()


class UsbCamera(Camera):
    """A camera implementation that uses a USB-based camera."""

    def __init__(self):
        self.video_stream = cv2.VideoStream(src=0).start()
        self.frame = LatestFrame()
        self.task = Periodic(self.capture, 1/24)

    def record(self):
        self.video_stream.start()

    def stop(self):
        self.task.stop()
        self.video_stream.release()

    def frames(self):
        return self.frame

    def capture(self):
        self.frame.update(self.video_stream.read())
