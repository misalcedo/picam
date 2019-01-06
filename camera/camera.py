from abc import ABC, abstractmethod


class Camera(ABC):
    """An abstraction for a camera that captures frames and exposes the latest frame captured."""
    @abstractmethod
    def record(self):
        """Records video frames to the buffer returned by #frames()."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the video recording."""
        pass

    @abstractmethod
    def frames(self):
        """Gets the buffer for the most recent frame captured by the camera."""
        pass
