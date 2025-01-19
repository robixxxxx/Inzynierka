import cv2
import pygame
import numpy as np
import socket
import threading
import queue
import math
import os
from consts import *

from models.telemetry_data_model import TelemetryDataModel
from models.control_data_model import ControlDataModel
from controllers.video.video_receiver import VideoReceiver

class VideoController:
    def __init__(self, screen, font, port, telemetry_data: TelemetryDataModel, control_data: ControlDataModel):
        self.screen = screen
        self.font = font
        self.running = False
        self.video_receiver = VideoReceiver(port)
        self.telemetry_data = telemetry_data
        self.control_data = control_data
        self.telemetry_lock = threading.Lock()
        self.speed = 0
        self.voltage = 0.0
        self.current = 0.0
        self.wifi_signal_strength = 0
        self.gear = 0
        self.lights = 0
        self.horn = 0
        self.smoothed_voltage = None
        self.smoothed_wifi_signal_strength = None
        self.load_wifi_icons()
        self.load_battery_icons()

    def load_wifi_icons(self):
        self.wifi_icons = []
        for i in range(4):
            icon_path = os.path.join("icons", "wifi", f"wifi_{i}.png")
            self.wifi_icons.append(pygame.image.load(icon_path))

    def load_battery_icons(self):
        self.battery_icons = []
        for i in range(7):
            icon_path = os.path.join("icons", "battery", f"battery_{i}.png")
            self.battery_icons.append(pygame.image.load(icon_path))

    def update_telemetry(self):
        with self.telemetry_lock:
            self.speed = self.telemetry_data.speed
            self.voltage = self.telemetry_data.voltage
            self.current = self.telemetry_data.current
            self.wifi_signal_strength = self.telemetry_data.wifi_signal_strength
            self.gear = self.control_data.gear
            self.lights = self.control_data.functions[0]
            self.horn = self.control_data.functions[1]
            self.smoothed_voltage = self.smooth_value(self.smoothed_voltage, self.voltage)
            self.smoothed_wifi_signal_strength = self.smooth_value(self.smoothed_wifi_signal_strength, self.wifi_signal_strength)

    def smooth_value(self, smoothed_value, new_value, alpha=0.1):
        if smoothed_value is None:
            return new_value
        return alpha * new_value + (1 - alpha) * smoothed_value

    def run(self):
        self.running = True
        self.video_receiver.start_receiving()
        clock = pygame.time.Clock()

        while self.running:
            # Odbieranie i wyświetlanie ramki wideo
            frame = self.video_receiver.get_frame()
            if frame is not None:
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
        telemetry_text = [f"Bieg: {gear_txt}"]
        y_offset = 10
        for line in telemetry_text:
            telemetry_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(telemetry_surface, (10, y_offset))
            y_offset += telemetry_surface.get_height() + 5

    def stop(self):
        self.running = False
        self.video_receiver.stop()