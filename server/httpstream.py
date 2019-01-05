from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE = """\
<html>
    <head>
    <title>RapBot MJPEG Stream</title>
    </head>
    <body>
        <h1>RapBot MJPEG Stream</h1>
        <img src="stream.mjpg"/>
    </body>
</html>
""".encode('utf-8')


class BaseStreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.redirect_root()
        elif self.path == '/index.html':
            self.index()
        elif self.path == '/stream.mjpg':
            self.stream()
        elif self.path == '/still.jpg':
            self.still()
        else:
            self.not_found()

    def still(self):
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'image/jpeg')
        self.end_headers()
        self.send_frame()

    def stream(self):
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        self.send_frames()

    def not_found(self):
        self.send_error(404)
        self.end_headers()

    def index(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(PAGE))
        self.end_headers()
        self.wfile.write(PAGE)

    def redirect_root(self):
        self.send_response(301)
        self.send_header('Location', '/index.html')
        self.end_headers()


class StreamingServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
