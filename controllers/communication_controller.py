import socket
import time
import threading
import pygame
import cv2
import numpy as np
from models.settings_manager import SettingsManager
from models.device_model import DeviceModel
from models.telemetry_data_model import TelemetryDataModel
from models.control_data_model import ControlDataModel
from controllers.force_feedback_controller import ForceFeedbackController
from controllers.input_handler import InputHandler

class CommunicationController:
    def __init__(self, screen, font, device: DeviceModel, settings_manager: SettingsManager, control_data, telemetry_data):
        self.screen = screen
        self.font = font
        self.device = device
        self.settings_manager = settings_manager
        self.control_connection = None
        self.telemetry_connection = None
        self.running = False
        self.control_data = control_data
        self.telemetry_data = telemetry_data
        self.input_handler = InputHandler(settings_manager, self.control_data)
        self.telemetry_lock = threading.Lock()

    def run(self):
        self.start_communication()
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.stop_communication()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        self.stop_communication()
                        return

            self.update_video_stream()
            self.render_telemetry_data()
            clock.tick(30)

    def start_communication(self):
        self.running = True
        self.send_thread = threading.Thread(target=self.send_loop, daemon=True)
        self.receive_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.send_thread.start()
        self.receive_thread.start()

    def send_loop(self):
        try:
            self.control_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_connection.connect((self.device.ip, self.device.control_port))
            print(f"Connected to control server at {self.device.ip}:{self.device.control_port}")

            while self.running:
                self.update_control_data()
                packed_data = self.control_data.pack_data()
                if packed_data:
                    self.control_connection.send(packed_data)
                time.sleep(0.1)  # Small delay between sends
        except Exception as e:
            print(f"Error in control loop: {e}")
            self.running = False
            raise ConnectionError("Error in control loop")
        finally:
            if self.control_connection:
                self.control_connection.close()

    def receive_loop(self):
        try:
            self.telemetry_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.telemetry_connection.connect((self.device.ip, self.device.telemetry_port))
            print(f"Connected to telemetry server at {self.device.ip}:{self.device.telemetry_port}")
            self.force_feedback_controller = ForceFeedbackController(self.settings_manager)    
            while self.running:
                telemetry_data = self.telemetry_connection.recv(28)
                if not telemetry_data or len(telemetry_data) != 28:
                    print(f"Received data length: {len(telemetry_data)}")
                    print("Incomplete telemetry data received, disconnecting.")
                    self.running = False
                    break

                with self.telemetry_lock:
                    self.telemetry_data.update(telemetry_data)
                self.force_feedback_controller.update_force_feedback(
                    self.telemetry_data.acceleration_x,
                    self.telemetry_data.acceleration_y,
                    self.telemetry_data.acceleration_z
                )

        except Exception as e:
            print(f"Error in telemetry loop: {e}")
            self.running = False
            raise ConnectionError("Error in telemetry loop")
        finally:
            if self.telemetry_connection:
                self.telemetry_connection.close()

    def update_control_data(self):
        self.input_handler.update_control_data()

    def get_control_data(self):
        control_data = self.input_handler.get_control_data()
        if control_data:
            return control_data.pack_data()
        return None

    def stop_communication(self):
        self.running = False
        if self.send_thread:
            self.send_thread.join()
        if self.receive_thread:
            self.receive_thread.join()
        