from aiohttp.web import View, StreamResponse


class CameraView(View):
    """The handler for the streaming web-cam server."""
    async def get(self):
        resp = StreamResponse(status=200, reason='OK', headers={
            'Age': '0',
            'Cache-Control': 'no-cache, private',
            'Pragma': 'no-cache',
            'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME'
        })

        # The StreamResponse is a FSM. Enter it with a call to prepare.
        await resp.prepare(self.request)

        while True:
            try:
                frame = self.request.app['camera'].frames.frame

                await resp.write(b'--FRAME\r\n')
                await resp.write(b'Content-Type: image/jpeg\r\n')
                await resp.write(b'Content-Length: ')
                await resp.write(bytes(str(len(frame))))
                await resp.write(b'\r\n')

                await resp.write(frame)
                await resp.write(b'\r\n')
            except Exception as e:
                print('Removed streaming client: %s', repr(e))
                raise
