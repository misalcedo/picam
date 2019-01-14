import cv2
import imutils

from metrics.passport import Passport

LOCATION = (10, 20)
COLOR = (0, 0, 255)


class Processor:
    def __init__(self, orientation, rotation, encoding):
        self.orientation = orientation
        self.rotation = rotation
        self.encoding = encoding
        self.passport = Passport()

    async def process(self, frame):
        flipped = await self.flip_frame(frame)
        rotated = await self.rotate_frame(flipped)
        final_frame = rotated

        await self.annotate(final_frame)

        return await self.encode_frame(final_frame)

    async def flip_frame(self, frame):
        if self.orientation:
            return cv2.flip(frame, self.orientation)
        else:
            return frame

    async def rotate_frame(self, frame):
        if self.rotation and self.rotation != 0:
            return imutils.rotate_bound(frame, self.rotation)
        else:
            return frame

    async def annotate(self, final_frame):
        duration = await self.passport.stamp("frame")
        height, width = final_frame.shape[:2]

        cv2.putText(final_frame,
                    "FPS: {}, Size: ({}, {})".format(int(1 / duration), width, height),
                    LOCATION,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    COLOR,
                    2)

    async def encode_frame(self, frame):
        return cv2.imencode(self.encoding, frame)
