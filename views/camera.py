import logging

from aiohttp.web import View, StreamResponse


class CameraView(View):
    """The handler for the streaming web-cam server."""

    async def get(self):
        response = StreamResponse(status=200, reason='OK', headers={
            'Age': '0',
            'Cache-Control': 'no-cache, private',
            'Pragma': 'no-cache',
            'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME'
        })

        await response.prepare(self.request)

        while True:
            try:
                frame = self.request.app['camera'].frames().frame

                await response.write(b'--FRAME\r\n')
                await response.write(b'Content-Type: image/jpeg\r\n')
                await response.write(b'Content-Length: ')
                await response.write(str(len(frame)).encode('utf-8'))
                await response.write(b'\r\n\r\n')

                await response.write(frame)
                await response.write(b'\r\n')
            except Exception as e:
                logging.debug('Removed streaming client: {}', repr(e))
                raise

        return response
