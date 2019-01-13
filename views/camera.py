import logging

from aiohttp.web import StreamResponse
from aiohttp_security import check_permission

from auth.permissions import STREAM
from views.base import BaseView

RESPONSE_HEADERS = {
    'Age': '0',
    'Cache-Control': 'no-cache, private',
    'Pragma': 'no-cache',
    'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME'
}


class CameraView(BaseView):
    """The handler for the streaming web-cam server."""

    async def get(self):
        await check_permission(self.request, STREAM, self.request.app)

        response = StreamResponse(status=200, reason='OK', headers=RESPONSE_HEADERS)

        await response.prepare(self.request)

        web_cam = self.request.app['camera']

        try:
            while await web_cam.is_recording():
                async with web_cam as frame:
                    await response.write(b'--FRAME\r\n')
                    await response.write(b'Content-Type: image/jpeg\r\n')
                    await response.write(b'Content-Length: ')
                    await response.write(str(len(frame)).encode('utf-8'))
                    await response.write(b'\r\n\r\n')

                    await response.write(frame)
                    await response.write(b'\r\n')
        except Exception:
            logging.info('Removed streaming client.')
            raise

        return response
