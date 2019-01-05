from abc import ABC, abstractmethod

class Camera(ABC):
    @abstractmethod
    def record(self, buffer):
        """Records video frames to the given buffer."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the video recording."""
        pass
