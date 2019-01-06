from camera.camera import Camera
from camera.splitter import FrameSplitter
from picamera import PiCamera as PiCam


class PiCamera(Camera):
    """A camera implementation that relies on the Raspberry Pi's camera module."""
    def __init__(self):
        self.splitter = FrameSplitter()
        self.pi_camera = PiCam(framerate=24)
        self.pi_camera.hflip = True
        self.pi_camera.vflip = True
        self.pi_camera.start_preview()

    def record(self):
        self.pi_camera.start_recording(self.splitter, format='mjpeg')

    def stop(self):
        self.pi_camera.stop_recording()

    def frames(self):
        return self.splitter
