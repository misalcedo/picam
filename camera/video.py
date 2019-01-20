from threading import Thread
import cv2


class VideoCaptureFrameReader:
    def __init__(self, source, width, height):
        self.video_stream = cv2.VideoCapture(source)

        self.video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.success = False
        self.frame = None

    def start(self):
        t = Thread(target=self.update, args=(), daemon=True)
        t.start()

    def update(self):
        # keep looping infinitely until the thread is stopped
        while self.video_stream.isOpened():
            # otherwise, read the next frame from the stream
            (self.success, self.frame) = self.video_stream.read()
            self.event.set()
            self.event.clear()

    def stop(self):
        self.video_stream.release()
