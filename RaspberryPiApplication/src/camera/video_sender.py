import cv2
import socket
import ffmpeg
import numpy as np
from picamera2 import Picamera2

class VideoSender:
    def __init__(self):
        # self.ip = ip
        self.port = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.camera = Picamera2()
        camera_config = self.camera.create_video_configuration(
            main={"size": (640, 360)},
            controls={"FrameRate": 24}
        )
        self.camera.configure(camera_config)
        self.camera.start()

        # FFmpeg proces do kodowania w H.265
        self.process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='640x360')
            .output('pipe:', format='h265', vcodec='libx265', preset='ultrafast')
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, quiet=True)
        )

    def send_video(self):
        while True:
            frame = self.camera.capture_array("main")
            self.process.stdin.write(frame.tobytes())  # Przekazujemy klatkę do FFmpeg
            h265_data = self.process.stdout.read(1024)  # Odbieramy zakodowaną klatkę (fragmenty)
            if h265_data:
                self.sock.sendto(h265_data, (self.ip, self.port))

    def stop(self):
        self.camera.stop()
        self.sock.close()
        self.process.stdin.close()
        self.process.wait()