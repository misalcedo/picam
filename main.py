import argparse
import asyncio
import json
import logging
import ssl

import aiohttp_jinja2
import jinja2
import uvloop
from aiohttp import web
from aiohttp_debugtoolbar import setup as setup_toolbar
from aiohttp_security import SessionIdentityPolicy, setup as setup_security
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiojobs.aiohttp import setup as setup_jobs

from auth.policy import AuthorizationPolicy
from server.handler import StreamingHandler
from server.stream import StreamingServer
from views.auth import AuthView
from views.camera import CameraView
from views.home import HomeView
from views.login import LoginView


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
                        default="resources/client_secret.json")
    parser.add_argument("--users", help="The list of email addresses allowed to access the web-cam.",
                        nargs='*',
                        default=[])
    parser.add_argument("--favicon", help="The file path to the favicon.ico file.",
                        default="favicon.ico")

    return parser.parse_args()


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


def load_client_secret(namespace):
    """Loads the client id from the client secret JSON file."""
    with open(namespace.secrets) as secret:
        return json.load(secret)["web"]


def create_camera(name):
    """Chooses the Camera implementation based on the given camera name."""
    if name == "pi":
        from camera.pi import PiCamera as Camera
    elif name == "stub":
        from camera.stub import StubCamera as Camera
    elif name == "usb":
        from camera.usb import UsbCameraAsync as Camera
    else:
        return None

    return Camera()


def server_async():
    namespace = parse_arguments()
    context = load_ssl_context(namespace)
    web_cam = create_camera(namespace.camera)

    middleware = session_middleware(SimpleCookieStorage())

    app = web.Application(middlewares=[middleware])

    add_configuration(app, namespace, web_cam)
    setup_plugins(app)
    add_signals(app, web_cam)
    add_routes(app)

    web.run_app(app, port=namespace.port, host=namespace.host, ssl_context=context)


def add_configuration(app, namespace, web_cam):
    client_secret = load_client_secret(namespace)

    app['client_id'] = client_secret['client_id']
    app['client_secret'] = client_secret['client_secret']
    app['camera'] = web_cam
    app['users'] = namespace.users


def setup_plugins(app):
    setup_toolbar(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    setup_jobs(app)
    setup_security(app, SessionIdentityPolicy(), AuthorizationPolicy())


def add_signals(app, web_cam):
    app.on_startup.append(web_cam.record)
    app.on_cleanup.append(web_cam.stop)


def add_routes(app):
    app.add_routes([
        web.view('/login', LoginView),
        web.view('/oauth', AuthView, name='auth'),
        web.view('/', HomeView),
        web.view('/camera', CameraView)
    ])
    app.router.add_static('/', path='static', name='static')


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logging.basicConfig(level=logging.DEBUG)
    server_async()
