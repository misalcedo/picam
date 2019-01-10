from camera.camera import Camera
from camera.frames import LatestFrame


class StubCamera(Camera):
    """A camera implementation that writes black frames."""

    def __init__(self):
        self.buffer = LatestFrame()
        
        with open('stub.jpg', 'rb') as f:
            self.frame = f.read()
    
    @property
    def condition(self):
        return self

    def record(self):
        pass

    def stop(self):
        pass

    def frames(self):
        return self
    
    def wait(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
