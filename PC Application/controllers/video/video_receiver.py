# import cv2
# import pygame
import numpy as np
import socket
import threading
import queue
# import math
# import os
from consts import *

# from models.telemetry_data_model import TelemetryDataModel
# from models.control_data_model import ControlDataModel

class VideoReceiver:
    def __init__(self, port, resolution=(640, 360)):
        self.port = port
        self.resolution = resolution
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', port))
        self.running = False
        self.frame_queue = queue.Queue(maxsize=5)

    def start_receiving(self):
        self.running = True
        threading.Thread(target=self._receive_frames, daemon=True).start()

    def _receive_frames(self):
        import ffmpeg
        process = (
            ffmpeg
            .input('pipe:', format='h265')
            .output('pipe:', format='rawvideo', pix_fmt='bgr24', s=f'{self.resolution[0]}x{self.resolution[1]}')
            .run_async(pipe_stdin=True, pipe_stdout=True, quiet=True)
        )
        while self.running:
            data, _ = self.sock.recvfrom(65536)
            if data:
                process.stdin.write(data)
                raw_frame = process.stdout.read(self.resolution[0] * self.resolution[1] * 3)
                if raw_frame:
                    frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((self.resolution[1], self.resolution[0], 3))
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
        process.stdin.close()
        process.wait()

    def stop(self):
        self.running = False
        self.sock.close()

    def get_frame(self):
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None