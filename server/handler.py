from httpstream import StreamingServer, BaseStreamingHandler


class StreamingHandler(BaseStreamingHandler):
    """The handler for the streaming webcam server."""

    @staticmethod
    def read_frame():
        with video_output.condition:
            video_output.condition.wait()
            return video_output.frame

    def send_frame(self):
        self.wfile.write(self.read_frame())

    def send_frames(self):
        try:
            while True:
                frame = self.read_frame()

                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception as e:
            self.log_message('Removed streaming client %s: %s', self.client_address, str(e))
