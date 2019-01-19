import argparse
import asyncio
import logging
import ssl
from asyncio import get_event_loop
from os.path import isfile

import aiohttp_jinja2
import aioredis
import jinja2
import uvloop
import yaml
from aiohttp import web
from aiohttp_debugtoolbar import setup as setup_toolbar
from aiohttp_remotes import Secure, setup as setup_remotes
from aiohttp_security import SessionIdentityPolicy, setup as setup_security
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage as SessionStorage
from aiojobs.aiohttp import setup as setup_jobs

from auth.policy import AuthorizationPolicy
from camera.usb import UsbCameraAsync as Camera
from views.auth import AuthView
from views.camera import CameraView
from views.home import HomeView
from views.sign_in import SignInView
from views.sign_out import SignOutView

DEFAULT_PARAMETERS = "resources/configuration.yaml"


def load_configuration(name):
    if not isfile(name):
        return {}

    with open(name) as f:
        return yaml.load(f)


async def close_redis(app):
    pool = app['redis']
    pool.close()
    await pool.wait_closed()


def serve(configuration):
    sessions = create_sessions(configuration['redis'])
    app = configure(sessions, configuration['users'])

    start_camera(app, configuration['camera'], configuration['motion'], configuration['logging'])

    listen(app, load_ssl_context(configuration['tls']), configuration['server'])


def create_sessions(redis_configuration):
    return session_middleware(SessionStorage(create_redis(redis_configuration)))


def create_redis(arguments):
    connections_arguments = arguments['connections']

    return get_event_loop().run_until_complete(aioredis.create_redis_pool(
        'redis://' + arguments['host'],
        minsize=connections_arguments['min'],
        maxsize=connections_arguments['max']))


def configure(sessions, users):
    app = web.Application(middlewares=[sessions])
    app['users'] = users

    setup_plugins(app)
    app.on_cleanup.append(close_redis)
    add_routes(app)
    return app


def setup_plugins(app):
    get_event_loop().run_until_complete(setup_remotes(app, Secure()))
    setup_toolbar(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    setup_jobs(app)
    setup_security(app, SessionIdentityPolicy(), AuthorizationPolicy())


def add_routes(app):
    app.add_routes([
        web.view('/', HomeView, name="home"),
        web.view('/sign_in', SignInView, name='sign_in'),
        web.view('/sign_out', SignOutView, name='sign_out'),
        web.view('/oauth', AuthView, name='auth'),
        web.view('/camera', CameraView, name='camera')
    ])
    app.router.add_static('/', path='static', name='static')


def start_camera(app, camera_arguments, motion_arguments, logging_arguments):
    video = Camera(**camera_arguments, processor=motion_arguments, clips=logging_arguments['clips'])

    app['camera'] = video
    app.on_startup.append(video.record)
    app.on_cleanup.append(video.stop)


def load_ssl_context(arguments):
    """Create a TLS context with the server's certificate chain and private key."""
    if arguments is None:
        return None

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(arguments['chain'], arguments['key'])

    return context


def listen(app, context, server):
    web.run_app(app, port=server['port'], host=server['host'], ssl_context=context)


def main():
    """Runs the camera server."""
    configuration = parse_arguments()

    setup()
    serve(configuration)


def setup():
    """Configure the runtime environment."""
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logging.basicConfig(level=logging.INFO)


def parse_arguments():
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(description="A home security camera server.")

    parser.add_argument("--config", help="The path to the YAML file with the runtime configuration.",
                        default="/etc/picam/config.yaml")

    namespace = parser.parse_args()

    configuration = load_configuration(DEFAULT_PARAMETERS)
    configuration.update(load_configuration(namespace.config))

    return configuration


if __name__ == '__main__':
    main()
