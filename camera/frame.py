import cv2
import imutils

from metrics.passport import Passport

LOCATION = (10, 20)
COLOR = (0, 0, 255)


class Processor:
    def __init__(self, orientation, rotation, encoding, delta_threshold, min_area):
        self.orientation = orientation
        self.rotation = rotation
        self.encoding = encoding
        self.delta_threshold = delta_threshold
        self.min_area = min_area

        self.passport = Passport()

        self.average_frame = None

    async def process(self, frame):
        flipped = await self.flip_frame(frame)
        rotated = await self.rotate_frame(flipped)
        motion = await self.detect_motion(rotated)
        final_frame = motion

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

    async def detect_motion(self, frame):
        grayed = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grayed, (21, 21), 0)

        if self.average_frame is None:
            self.average_frame = blurred.copy().astype("float")

        cv2.accumulateWeighted(blurred, self.average_frame, 0.5)
        delta = cv2.absdiff(blurred, cv2.convertScaleAbs(self.average_frame))

        thresh = cv2.threshold(delta, self.delta_threshold, 255, cv2.THRESH_BINARY)[1]
        dilated = cv2.dilate(thresh, None, iterations=2)

        contours = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in imutils.grab_contours(contours):
            if cv2.contourArea(c) >= self.min_area:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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
