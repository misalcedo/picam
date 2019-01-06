from io import BytesIO
from camera.frames import LatestFrame


class FrameSplitter(LatestFrame):
    """A latest frame reference that detects the splits frames in a continuous stream of frames."""
    def __init__(self):
        self.output = BytesIO()
        super().__init__()

    def write(self, buffer):
        if buffer.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.output.truncate()

            self.update(self.output.getvalue())

            self.output.seek(0)

        return self.output.write(buffer)
