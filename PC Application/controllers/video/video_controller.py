import pygame
import cv2
import numpy as np
# import requests
import threading
import queue
import os
import math
from consts import *

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
        self.speed = 0.0
        self.voltage = 0.0
        self.current = 0.0
        self.wifi_signal_strength = 0
        self.gear = 0
        self.lights = 0
        self.horn = 0
        self.telemetry_data = telemetry_data
        self.control_data = control_data
        self.telemetry_lock = threading.Lock()
        self.load_wifi_icons()
        self.load_battery_icons()
        self.smoothed_voltage = None
        self.smoothed_wifi_signal_strength = None

    def load_wifi_icons(self):
        self.wifi_icons = []
        for i in range(4):
            icon_path = os.path.join("icons", "wifi", f"wifi_{i}.png")
            icon = pygame.image.load(icon_path)
            self.wifi_icons.append(icon)
    
    def load_battery_icons(self):
        self.battery_icons = []
        for i in range(7):
            icon_path = os.path.join("icons", "battery", f"battery_{i}.png")
            icon = pygame.image.load(icon_path)
            self.battery_icons.append(icon)

    def fetch_frames(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
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
            self.smoothed_voltage = self.smooth_value(self.smoothed_voltage, self.voltage)
            self.smoothed_wifi_signal_strength = self.smooth_value(self.smoothed_wifi_signal_strength, self.wifi_signal_strength)
    
    def smooth_value(self, smoothed_value, new_value, alpha=0.1):
        if smoothed_value is None:
            return new_value
        return alpha * new_value + (1 - alpha) * smoothed_value

    def run(self):
        self.start_video_stream()
        clock = pygame.time.Clock()
    
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                if isinstance(frame, np.ndarray):
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, self.screen.get_size())
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    self.screen.blit(frame_surface, (0, 0))
    
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
                f"Bieg: {gear_txt}",
            ]
        y_offset = 10
        for line in telemetry_text:
            telemetry_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(telemetry_surface, (10, y_offset))
            y_offset += telemetry_surface.get_height() + 5

        icon_bg_width = 50
        icon_bg_height = 50
        icon_bg_surface = pygame.Surface((icon_bg_width, icon_bg_height))
        icon_bg_surface.set_alpha(128)  # Set transparency level (0-255)
        icon_bg_surface.fill((255, 255, 255))  # Fill with white color

        wifi_icon = self.get_wifi_icon(self.smoothed_wifi_signal_strength)
        if wifi_icon:
            self.screen.blit(icon_bg_surface, (10, y_offset))
            self.screen.blit(wifi_icon, (10, y_offset))
            y_offset += wifi_icon.get_height() + 5

        battery_icon = self.get_battery_icon(self.smoothed_voltage)
        if battery_icon:
            self.screen.blit(icon_bg_surface, (10, y_offset))
            self.screen.blit(battery_icon, (10, y_offset))

        self._draw_meter(center=(self.screen.get_width() - 100, 100), radius=75, max_value=2000, current_value=self.current, unit="mA", color_start=(0, 255, 0), color_end=(255, 0, 0))
        self._draw_meter(center=(self.screen.get_width() - 100, 200), radius=75, max_value=10, current_value=self.speed, unit="km/h", color_start=(255, 255, 255), color_end=(255, 255, 255))

    def _draw_meter(self, center, radius, max_value, current_value, unit, color_start, color_end):
        current_value = min(max(current_value, 0), max_value)
        angle = (current_value / max_value) * 360

        # Determine the color based on the current value
        color = (
            int(color_start[0] + (color_end[0] - color_start[0]) * (current_value / max_value)),
            int(color_start[1] + (color_end[1] - color_start[1]) * (current_value / max_value)),
            int(color_start[2] + (color_end[2] - color_start[2]) * (current_value / max_value)),
        )

        # Draw the background circle
        pygame.draw.circle(self.screen, (75, 75, 75), center, radius, 5)

        # Draw the meter arc
        start_angle = -90
        end_angle = start_angle + angle
        for i in range(start_angle, int(end_angle)):
            rad = math.radians(i)
            x = center[0] + radius * math.cos(rad)
            y = center[1] + radius * math.sin(rad)
            pygame.draw.line(self.screen, color, center, (x, y), 2)

        # Draw the current value text
        current_text = self.font.render(f"{current_value:.2f} {unit}", True, (255, 255, 255))
        text_rect = current_text.get_rect(center=center)
        self.screen.blit(current_text, text_rect)


    def get_wifi_icon(self, signal_strength):
        if signal_strength >= -50:
            return self.wifi_icons[3]
        elif signal_strength >= -60:
            return self.wifi_icons[2]
        elif signal_strength >= -70:
            return self.wifi_icons[1]
        else:
            return self.wifi_icons[0]

    def get_battery_icon(self, voltage):
        if voltage >= 8.4:
            return self.battery_icons[6]
        elif voltage >= 8.0:
            return self.battery_icons[5]
        elif voltage >= 7.6:
            return self.battery_icons[4]
        elif voltage >= 7.2:
            return self.battery_icons[3]
        elif voltage >= 6.8:
            return self.battery_icons[2]
        elif voltage >= 6.4:
            return self.battery_icons[1]
        else:
            return self.battery_icons[0]

    def stop(self):
        self.running = False
        self.capture.release()

    def start_video_stream(self):
        self.running = True
        fetch_thread = threading.Thread(target=self.fetch_frames, daemon=True)
        fetch_thread.start()
