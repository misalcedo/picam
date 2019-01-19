import argparse
import asyncio
import logging
import ssl

import aiohttp_jinja2
import aioredis
import jinja2
import uvloop
import yaml
from os.path import isfile
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
from asyncio import get_event_loop

DEFAULT_PARAMETERS = "resources/configuration.yaml"


def load_configuration(name):
    if not isfile(name):
        return {}

    with open(name) as f:
        return yaml.load(f)


def load_ssl_context(arguments):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(arguments['chain'], arguments['key'])

    return context


def create_redis(arguments):
    redis_arguments = arguments['redis']
    connections_arguments = redis_arguments['connections']

    return get_event_loop().run_until_complete(aioredis.create_redis_pool(
        'redis://' + redis_arguments['host'],
        minsize=connections_arguments['min'],
        maxsize=connections_arguments['max']))


async def close_redis(app):
    pool = app['redis']
    pool.close()
    await pool.wait_closed()


def serve():
    configuration = parse_arguments()
    print(configuration)
    camera_arguments = configuration['camera']
    server_arguments = configuration['server']

    context = load_ssl_context(server_arguments)
    web_cam = Camera(**camera_arguments)

    middleware = session_middleware(SessionStorage(create_redis(configuration)))

    app = web.Application(middlewares=[middleware])

    add_configuration(app, configuration, web_cam)
    setup_plugins(app)
    add_signals(app, web_cam)
    add_routes(app, configuration)

    web.run_app(app, port=server_arguments['port'], host=server_arguments['host'], ssl_context=context)


def add_configuration(app, arguments, web_cam):
    app['camera'] = web_cam
    app['users'] = arguments['users']


def setup_plugins(app):
    get_event_loop().run_until_complete(setup_remotes(app, Secure()))
    setup_toolbar(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    setup_jobs(app)
    setup_security(app, SessionIdentityPolicy(), AuthorizationPolicy())


def add_signals(app, web_cam):
    app.on_startup.append(web_cam.record)
    app.on_cleanup.append(web_cam.stop)
    app.on_cleanup.append(close_redis)


def add_routes(app):
    app.add_routes([
        web.view('/', HomeView, name="home"),
        web.view('/sign_in', SignInView, name='sign_in'),
        web.view('/sign_out', SignOutView, name='sign_out'),
        web.view('/oauth', AuthView, name='auth'),
        web.view('/camera', CameraView, name='camera')
    ])
    app.router.add_static('/', path='static', name='static')


def main():
    """Runs the camera server."""
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logging.basicConfig(level=logging.INFO)
    serve()


def parse_arguments():
    """
    Sample usage:
        python3 main.py --parameters config.yaml
    """
    parser = argparse.ArgumentParser(description="A home security camera server.")

    parser.add_argument("--config", help="The path to the YAML file with the runtime configuration.",
                        default="/etc/picam/config.yaml")

    namespace = parser.parse_args()

    configuration = load_configuration(DEFAULT_PARAMETERS)
    configuration.update(load_configuration(namespace.config))

    return configuration


if __name__ == '__main__':
    main()
