class StubCamera(Camera):
    """A camera implementation that writes black frames."""

    def __init__(self):
        pass

    def record(self, buffer):
        pass # TODO write frames to buffer

    def stop(self):
        pass
