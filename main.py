import argparse
import asyncio
import json
import ssl

import uvloop
from aiohttp import web

from server.handler import StreamingHandler
from server.stream import StreamingServer


def main():
    namespace = parse_arguments()
    client_id = load_client_id(namespace)
    favicon = load_favicon(namespace)
    web_cam = create_camera(namespace.camera)

    web_cam.record()

    try:
        serve(client_id, favicon, web_cam, namespace)
    finally:
        web_cam.stop()


def parse_arguments():
    """
    Sample usage:
        python3 main.py --camera pi --port 1629 --domain localhost --host localhost
    """
    parser = argparse.ArgumentParser(description="A home security camera server.")
    parser.add_argument("--camera", help="The type of camera to use.",
                        choices=["pi", "stub", "usb"],
                        default="usb")
    parser.add_argument("--port", help="The TCP port to listen on.",
                        type=int,
                        default=1629)
    parser.add_argument("--host", help="The host interface to listen on.",
                        default="0.0.0.0")
    parser.add_argument("--domain", help="The host interface to listen on.",
                        default="puppy-cam.salcedo.cc")
    parser.add_argument("--cert", help="The file path to the TLS certificate.",
                        default="resources/fullchain.pem")
    parser.add_argument("--key", help="The file path to the TLS certificate key.",
                        default="resources/privkey.pem")
    parser.add_argument("--secrets", help="The file path to the Google API's client-secrets JSON file.",
                        default="client_secret.json")
    parser.add_argument("--users", help="The list of email addresses allowed to access the web-cam.",
                        nargs='*',
                        default=[])
    parser.add_argument("--favicon", help="The file path to the favicon.ico file.",
                        default="favicon.ico")
    namespace = parser.parse_args()
    return namespace


def serve(client_id, favicon, web_cam, namespace):
    context = load_ssl_context(namespace)

    server = StreamingServer(server_address=(namespace.host, namespace.port), handler_class=StreamingHandler,
                             frames=web_cam.frames(), client_id=client_id,
                             users=namespace.users, favicon=favicon)

    server.socket = context.wrap_socket(server.socket, server_side=True)

    print("Started web-cam server with arguments:", namespace)

    server.serve_forever()


def load_ssl_context(namespace):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(namespace.cert, namespace.key)
    return context


def load_favicon(namespace):
    with open(namespace.favicon, 'rb') as file:
        return file.read()


def load_client_id(namespace):
    """Loads the client id from the client secret JSON file."""
    with open(namespace.secrets) as secret:
        return json.load(secret)["web"]["client_id"]


def create_camera(name):
    """Chooses the Camera implementation based on the given camera name."""
    if name == "pi":
        from camera.pi import PiCamera as Camera
    elif name == "stub":
        from camera.stub import StubCamera as Camera
    elif name == "usb":
        from camera.usb import UsbCamera as Camera
    else:
        return None

    return Camera()


def server_async():
    from views.login import LoginView
    from views.home import HomeView
    from views.camera import CameraView

    import aiohttp_jinja2
    import jinja2

    namespace = parse_arguments()
    context = load_ssl_context(namespace)

    app = web.Application()
    app.add_routes([
        web.view('/login', LoginView),
        web.view('/', HomeView),
        web.view('/camera', CameraView)
    ])
    app.router.add_static('/static', path='static', name='static')
    app['client_id'] = load_client_id(namespace)

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))

    web.run_app(app, ssl_context=context)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    server_async()
