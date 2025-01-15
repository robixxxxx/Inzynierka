import json
import pygame
import threading
import socket
from models.device_model import DeviceModel
from views.device_list_view import DeviceListView
from controllers.communication_controller import CommunicationController
from controllers.video.video_controller import VideoController

from models.control_data_model import ControlDataModel
from models.telemetry_data_model import TelemetryDataModel

class DeviceController:
    DISCOVERY_PORT = 50000

    def __init__(self, screen, font, settings_manager):
        self.screen = screen
        self.font = font
        self.settings_manager = settings_manager
        self.devices = []
        self.running = False
        self.lock = threading.Lock()
        self.view = DeviceListView(self.screen, self.font)
        self.communication_controller = None

    def discover_devices(self):
        """Skanuje sieć w poszukiwaniu urządzeń."""
        print("Skanowanie sieci w poszukiwaniu urządzeń")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(2)
            sock.bind(('', self.DISCOVERY_PORT))

            try:
                while self.running:
                    try:
                        data, addr = sock.recvfrom(1024)
                        print(f"Received data from: {addr}, {data}")

                        # Parse JSON safely
                        try:
                            device_info = json.loads(data.decode('utf-8'))
                        except json.JSONDecodeError as e:
                            print(f"Invalid JSON received: {data}, Error: {e}")
                            continue
                        
                        # Extract device details
                        name = device_info.get("name")
                        control_port = device_info.get("control_port")
                        telemetry_port = device_info.get("telemetry_port")

                        # Create a Device object
                        device = DeviceModel(
                            name=name,
                            ip=addr[0],
                            control_port=int(control_port),
                            telemetry_port=int(telemetry_port)
                        )
                        with self.lock:
                            if device not in self.devices:
                                self.devices.append(device)

                    except socket.timeout:
                        if not self.running:  # Check if discovery is still running
                            break

            except Exception as e:
                print(f"Błąd podczas wyszukiwania: {e}")

    def run(self):
        """Main loop for device discovery."""
        self.devices = []
        self.running = True

        # Start discovery in a thread
        discovery_thread = threading.Thread(target=self.discover_devices, daemon=True)
        discovery_thread.start()

        clock = pygame.time.Clock()
        selected_index = 0

        while self.running:
            # Render discovered devices
            with self.lock:
                self.view.render(self.devices, selected_index)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        with self.lock:
                            if self.devices:
                                selected_index = (selected_index + 1) % len(self.devices)
                    elif event.key == pygame.K_UP:
                        with self.lock:
                            if self.devices:
                                selected_index = (selected_index - 1) % len(self.devices)
                    elif event.key == pygame.K_RETURN:
                        with self.lock:
                            if self.devices:
                                selected_device = self.devices[selected_index]
                                print(f"Selected device: {selected_device.name} at {selected_device.ip}")
                                self.running = False  # Stop discovery
                                self._start_vehicle_control(selected_device)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            clock.tick(60)

        # Stop discovery thread
        self.running = False
        discovery_thread.join()

    def _start_vehicle_control(self, device):
        """Start vehicle control after selecting a device."""
        try:
            self.control_data = ControlDataModel()
            self.telemetry_data = TelemetryDataModel()
            self.communication_controller = CommunicationController(self.screen, self.font, device, self.settings_manager, self.control_data, self.telemetry_data)
            self.video_controller = VideoController(self.screen, self.font, f"http://{device.ip}:8000/video", self.telemetry_data, self.control_data)
            self.communication_controller.start_communication()
            self.video_controller.run()
        except ConnectionError as e:
            print(f"Connection error: {e}")
            print("Restarting device discovery...")
            self.run()  # Restart discovery after failure
        except Exception as e:
            print(f"Unexpected error during communication: {e}")
            print("Returning to device discovery...")
            self.run()
        finally:
            if self.communication_controller:
                self.communication_controller.stop_communication()

    def stop(self):
        self.running = False