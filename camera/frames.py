from threading import Condition


class LatestFrame:
    """A latest frame reference that detects the splits frames in a continuous stream of frames."""
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update(self, frame):
        """Updates the frame reference and notifies listeners."""
        with self.condition:
            self.frame = frame
            self.condition.notify_all()
