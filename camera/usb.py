import threading
import time

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
                self.frame.update(cv2.imencode('.jpg', frame)[1].tobytes())
                time.sleep(self.seconds_per_frame)
