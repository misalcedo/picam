import argparse
from camera.frames import FrameSplitter
from server.handler import StreamingHandler
from server.stream import StreamingServer


def main():
    """
    Sample usage:
        python3 main.py --camera picam
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

    namespace = parser.parse_args()

    print("Started webcam server with arguments:", namespace)

    webcam = create_camera(namespace.camera)
    video_output = FrameSplitter()
    webcam.record(video_output)

    try:
        server = StreamingServer(video_output, ('', namespace.port), StreamingHandler)
        server.serve_forever()
    finally:
        webcam.stop()


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
