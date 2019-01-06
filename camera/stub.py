from camera.camera import Camera


class StubCamera(Camera):
    """A camera implementation that writes black frames."""

    def __init__(self):
        pass

    def record(self):
        pass

    def stop(self):
        pass

    def frames(self):
        pass
