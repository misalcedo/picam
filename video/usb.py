import logging

import cv2


class UsbVideo:
    """A camera implementation that uses an asynchronous USB-based camera."""

    def __init__(self, size, source):
        self.source = source
        self.width, self.height = size

        self.video_stream = None

    def stop(self):
        if self.video_stream is not None:
            self.video_stream.release()
            self.video_stream = None

    def start(self):
        if self.video_stream is None:
            self.video_stream = cv2.VideoCapture(self.source)
            self.video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def is_readable(self):
        return self.video_stream is not None and self.video_stream.isOpened()

    def frame(self):
        if self.is_readable():
            success, frame = self.video_stream.read()

            if success:
                return frame
            else:
                logging.debug("Failed to read camera frame.")

        return None
