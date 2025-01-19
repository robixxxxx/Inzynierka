import pygame
import cv2
import numpy as np
import requests
import threading
import queue

from models.telemetry_data_model import TelemetryDataModel
from models.control_data_model import ControlDataModel

class VideoController:
    def __init__(self, screen, font, stream_url, telemetry_data:TelemetryDataModel, control_data:ControlDataModel):
        self.screen = screen
        self.font = font
        self.stream_url = stream_url
        self.capture = cv2.VideoCapture(self.stream_url)
        self.running = False
        self.frame_queue = queue.Queue(maxsize=5)
        self.speed = 0  # Initialize speed to 0
        self.voltage = 0.0
        self.current = 0.0
        self.wifi_signal_strength = 0
        self.gear = 0
        self.lights = 0
        self.horn = 0
        self.telemetry_data = telemetry_data
        self.control_data = control_data
        self.telemetry_lock = threading.Lock()

    def fetch_frames(self):
        bytes_buffer = b''
        stream = requests.get(self.stream_url, stream=True)
        while self.running:
            bytes_buffer += stream.raw.read(2048)
            start = bytes_buffer.find(b'\xff\xd8')
            end = bytes_buffer.find(b'\xff\xd9')
            if start != -1 and end != -1:
                jpg = bytes_buffer[start:end + 2]
                bytes_buffer = bytes_buffer[end + 2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    if self.frame_queue.full():
                        self.frame_queue.get()
                    self.frame_queue.put(frame)

    def start_video_stream(self):
        self.running = True
        fetch_thread = threading.Thread(target=self.fetch_frames, daemon=True)
        fetch_thread.start()

    def update_telemetry(self):
        with self.telemetry_lock:
            self.speed = self.telemetry_data.speed
            self.voltage = self.telemetry_data.voltage
            self.current = self.telemetry_data.current
            self.wifi_signal_strength = self.telemetry_data.wifi_signal_strength
            self.gear = self.control_data.gear
            self.lights = self.control_data.functions[0]
            self.horn = self.control_data.functions[1]

    def run(self):
        self.start_video_stream()
        clock = pygame.time.Clock()
    
        while self.running:
            # Odbieranie i wyświetlanie ramki wideo
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                if isinstance(frame, np.ndarray):
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, self.screen.get_size())
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.screen.blit(frame_surface, (0, 0))
    
            # Rysowanie telemetryki
            self.update_telemetry()
            self._draw_telemetry()
            pygame.display.flip()
    
            # Obsługa zdarzeń
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
    
            clock.tick(30)
    
        self.stop()

    def _draw_telemetry(self):
        gear_txt = "R" if self.gear == -1 else "N" if self.gear == 0 else self.gear
        with self.telemetry_lock:
            telemetry_text = [
                f"Speed: {self.speed} km/h",
                f"Voltage: {self.voltage:.2f} V",
                f"Current: {self.current:.2f} A",
                f"WiFi Signal Strength: {self.wifi_signal_strength} dBm",
                f"Gear: {gear_txt}",
                f"Lights: {self.lights}",
                f"Horn: {self.horn}",
            ]
        y_offset = 10
        for line in telemetry_text:
            telemetry_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(telemetry_surface, (10, y_offset))
            y_offset += telemetry_surface.get_height() + 5

    def stop(self):
        self.running = False
        self.capture.release()

    def start_video_stream(self):
        self.running = True
        fetch_thread = threading.Thread(target=self.fetch_frames, daemon=True)
        fetch_thread.start()
