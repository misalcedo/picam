from camera.camera import Camera
from picamera import PiCamera as PiCam


class PiCamera(Camera):
    """A camera implementation that relies on the Raspberry Pi's camera module."""

    def __init__(self):
        self.pi_camera = PiCam(framerate=24)
        self.pi_camera.hflip = True
        self.pi_camera.vflip = True
        self.pi_camera.start_preview()

    def record(self, buffer):
        self.pi_camera.start_recording(buffer, format='mjpeg')

    def stop(self):
        self.pi_camera.stop_recording()
