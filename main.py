import argparse
import ssl
from camera.frames import FrameSplitter
from server.handler import StreamingHandler
from server.stream import StreamingServer


def main():
    """
    Sample usage:
        python3 main.py --camera pi --port 1629 --domain localhost --host localhost
    """
    parser = argparse.ArgumentParser(description="A home security camera server.")
    parser.add_argument("--camera", help="The type of camera to use.",
                        choices=["pi", "stub", "usb"],
                        default="pi")
    parser.add_argument("--port", help="The TCP port to listen on.",
                        type=int,
                        default=1629)
    parser.add_argument("--host", help="The host interface to listen on.",
                        default="0.0.0.0")
    parser.add_argument("--domain", help="The host interface to listen on.",
                        default="puppy-cam.salcedo.cc")
    parser.add_argument("--cert", help="The file path to the TLS certificate.",
                        default="fullchain.pem")
    parser.add_argument("--key", help="The file path to the TLS certificate key.",
                        default="privkey.pem")
    parser.add_argument("--secrets", help="The file path to the Google API's client-secrets JSON file.",
                        default="client_secret.json")
    parser.add_argument("--redirect", help="The URL path for the OATH server to redirect an authentication response to.",
                        default="/oauth2/callback")

    namespace = parser.parse_args()

    print("Started web-cam server with arguments:", namespace)

    web_cam = create_camera(namespace.camera)
    video_output = FrameSplitter()
    web_cam.record(video_output)

    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(namespace.cert, namespace.key)

        server = StreamingServer(video_output, (namespace.host, namespace.port), StreamingHandler)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        server.serve_forever()
    finally:
        web_cam.stop()


def create_camera(name):
    """Chooses the Camera implementation based on the given camera name."""
    if name == "pi":
        from camera.pi import PiCamera as Camera
    elif name == "stub":
        from camera.stub import StubCamera as Camera
    else:
        return None

    return Camera()


if __name__ == '__main__':
    main()
