from io import BytesIO
from threading import Condition


class FrameSplitter:
    def __init__(self):
        self.frame = None
        self.output = BytesIO()
        self.condition = Condition()

    def write(self, buffer):
        if buffer.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.output.truncate()

            with self.condition:
                self.frame = self.output.getvalue()
                self.condition.notify_all()

            self.output.seek(0)

        return self.output.write(buffer)
