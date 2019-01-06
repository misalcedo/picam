from camera.camera import Camera


class UsbCamera(Camera):
    """A camera implementation that uses a USB-based camera."""

    def __init__(self):
        pass

    def record(self, buffer):
        pass # TODO write frames to buffer

    def stop(self):
        pass
