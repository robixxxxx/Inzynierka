import threading
import time
import struct
import socket
import json
import subprocess
import RPi.GPIO as GPIO
import os
from flask import Flask, Response, request, jsonify, render_template_string, send_from_directory
from src.sensors.ina3221 import INA3221Sensor
from src.sensors.as5600 import AS5600Sensor
from src.sensors.speed_sensor import SpeedSensor
from src.sensors.mpu6500 import MPU6500Sensor
from src.sensors.pcf8574 import PCF8574IOExpander
from src.motor.l9110s import L9110SMotorDriver
from src.servo.servo_controller import ServoController
from src.camera.camera import Camera


BROADCAST_PORT = 50000
CONTROL_PORT = 12345
TELEMETRY_PORT = 12346

BROADCAST_MSG = json.dumps({
    "name": "RaspberryPiControlServer",
    "control_port": CONTROL_PORT,
    "telemetry_port": TELEMETRY_PORT
}).encode('utf-8')


class RCServer:
    def __init__(self):
        self.app = Flask(__name__)
        try:
            self.ina = INA3221Sensor()
            self.mpu6500 = MPU6500Sensor()
            self.io_expander = PCF8574IOExpander()
            self.motor = L9110SMotorDriver()
            self.servo = ServoController()
            self.camera = Camera()
            self.speed_sensor = SpeedSensor()
            
        except Exception as e:
            print(f"Error initializing sensors or controllers: {e}")

        self.control_socket = None
        self.telemetry_socket = None
        self.broadcast_socket = None
        self.client_connected = False

        self.telemetry_data = {
            "speed": 0,
            "accX": 0.0,
            "accY": 0.0,
            "accZ": 0.0,
            "voltage": 0.0,
            "current": 0.0,
            "wifi_signal_strength": 0
        }

        self.control_data = {
            "gas_pedal": 0,
            "brake_pedal": 0,
            "lights_on": False,
            "horn_on": False,
            "gear": 0
        }

        self.lights_on = False

        self.lock = threading.Lock()
        self.running = True

        self.telemetry_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
        self.telemetry_thread.start()
        self.html_dir = os.path.join(os.path.dirname(__file__), 'src/html/')
        print(self.html_dir)
        
        self.app.add_url_rule('/', 'index_page', self.index, methods=['GET'])
        self.app.add_url_rule('/video', 'video', self.video)
        self.app.add_url_rule('/wifi', 'wifi_page', self.wifi_page, methods=['GET'])
        self.app.add_url_rule('/wifi/scan', 'wifi_scan', self.wifi_scan, methods=['GET'])
        self.app.add_url_rule('/wifi/connect', 'wifi_connect', self.wifi_connect, methods=['POST'])

    def _telemetry_loop(self):
        while self.running:
            try:
                ina_data = self.ina.read()
                accel = self.mpu6500.read_acceleration()

                with self.lock:
                    self.telemetry_data["speed"] = self.speed_sensor.calculate_speed()
                    self.telemetry_data["accX"] = accel["accX"]
                    self.telemetry_data["accY"] = accel["accY"]
                    self.telemetry_data["accZ"] = accel["accZ"]
                    self.telemetry_data["voltage"] = ina_data["voltage"]
                    self.telemetry_data["current"] = ina_data["current"]
                    self.telemetry_data["wifi_signal_strength"] = self.get_wifi_signal_strength()

            except Exception as e:
                print(f"Błąd w pętli telemetrycznej: {e}")
            time.sleep(0.1)

    def get_wifi_signal_strength(self):
        try:
            # Uruchomienie iwconfig
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)

            for line in result.stdout.split('\n'):
                if 'Signal level' in line:  # Znajdź linię z "Signal level"
                    # Podziel linię na fragmenty i szukaj kluczowych wartości
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'level=' in part:  # Znajdź segment z "level="
                            try:
                                # Wyciągnij wartość po "level="
                                signal_level = int(part.split('=')[1].replace('dBm', '').strip())
                                return signal_level
                            except ValueError as ve:
                                print(f"Error parsing signal level value: {ve}")

                    # Dodatkowe sprawdzenie, jeśli "level=" jest oddzielne
                    if 'Signal' in parts and 'level=' in parts[i + 1]:
                        try:
                            signal_level = int(parts[i + 1].split('=')[1].replace('dBm', '').strip())
                            return signal_level
                        except ValueError as ve:
                            print(f"Error parsing signal level value: {ve}")

        except Exception as e:
            print(f"Error getting WiFi signal strength: {e}")
        return 0  # Wartość domyślna w przypadku błędu



    def start_broadcasting(self):
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while not self.client_connected and self.running:
            self.broadcast_socket.sendto(BROADCAST_MSG, ("<broadcast>", BROADCAST_PORT))
            print("Broadcasting server presence...")
            time.sleep(5)
        self.broadcast_socket.close()

    def handle_control_connection(self):
        while self.running:
            try:
                self.control_socket = self._create_server_socket(CONTROL_PORT)
                print(f"Control server listening on port {CONTROL_PORT}...")
                client_socket, addr = self.control_socket.accept()
                print(f"Connected to client for control at {addr}")
                self.client_connected = True
                self.process_control_data(client_socket)
            except Exception as e:
                print(f"Control connection failed: {e}")
            finally:
                if self.control_socket:
                    self.control_socket.close()
                    self.reset_to_broadcast()

    def handle_telemetry_connection(self):
        while self.running:
            try:
                self.telemetry_socket = self._create_server_socket(TELEMETRY_PORT)
                print(f"Telemetry server listening on port {TELEMETRY_PORT}...")
                client_socket, addr = self.telemetry_socket.accept()
                print(f"Connected to client for telemetry at {addr}")
                self.client_connected = True
                self.send_telemetry_data(client_socket)
            except Exception as e:
                print(f"Telemetry connection failed: {e}")
            finally:
                if self.telemetry_socket:
                    self.telemetry_socket.close()
                    self.reset_to_broadcast()

    def process_control_data(self, client_socket):
        try:
            while self.running:
                data = client_socket.recv(5)
                if not data or len(data) != 5:
                    print("Invalid control data or connection lost.")
                    self.client_connected = False
                    break

                gear, steering, gas, brake, functions = struct.unpack("bbBBB", data)
                self.update_control_data(gear, steering, gas, brake, functions)
                # print(f"Control data updated: {self.control_data}, functions: {functions}")

                self.apply_controls_to_hardware()

        except socket.error as e:
            print(f"Control socket error: {e}")
        finally:
            client_socket.close()

    def send_telemetry_data(self, client_socket):
        try:
            while self.client_connected and self.running:
                with self.lock:
                    speed = float(self.telemetry_data["speed"])
                    accX = float(self.telemetry_data["accX"])
                    accY = float(self.telemetry_data["accY"])
                    accZ = float(self.telemetry_data["accZ"])
                    voltage = float(self.telemetry_data["voltage"])
                    current = float(self.telemetry_data["current"])
                    wifi_signal_strength = int(self.telemetry_data["wifi_signal_strength"])

                # print(f"Data sent: speed:{speed}, accX:{accX}, accY:{accY}, accZ:{accZ}, voltage:{voltage}, current:{current}, wifi_signal_strength:{wifi_signal_strength}")
                packed_data = struct.pack("ffffffi", speed, accX, accY, accZ, voltage, current, wifi_signal_strength)
                client_socket.sendall(packed_data)
                time.sleep(0.1)
        except socket.error as e:
            print(f"Telemetry socket error: {e}")
        finally:
            client_socket.close()

    def update_control_data(self, gear, steering, gas, brake, functions):
        with self.lock:
            self.control_data["steering_angle"] = steering
            self.control_data["gas_pedal"] = gas
            self.control_data["brake_pedal"] = brake
            self.control_data["lights_on"] = ((functions & (1 << 0)) != 0)
            self.control_data["horn_on"] = ((functions & (1 << 1)) != 0)
            self.control_data["gear"] = gear

    def apply_controls_to_hardware(self):
        try:
            steering = self.control_data["steering_angle"]
            gear = self.control_data["gear"]
            gas = self.control_data["gas_pedal"] 
            brake = self.control_data["brake_pedal"]
            
            self.motor.set_power(gas, brake, gear)

            self.io_expander.set_bit(0, self.control_data["lights_on"])
            self.io_expander.set_bit(1, self.control_data["lights_on"])
            self.io_expander.set_bit(2, self.control_data["lights_on"])
            self.io_expander.set_bit(3, self.control_data["lights_on"])
            self.io_expander.set_bit(4, brake > 5)
            self.io_expander.set_bit(5, brake > 5)
            self.io_expander.set_bit(6, self.control_data["horn_on"])

            servo_angle = 0 + steering
            self.servo.set_angle(servo_angle)
        except Exception as e:
            print(f"Error applying controls to hardware: {e}")

    def reset_to_broadcast(self):
        with self.lock:
            self.client_connected = False
        if self.control_socket:
            self.control_socket.close()
        if self.telemetry_socket:
            self.telemetry_socket.close()
        self.motor.stop()
        self.servo.stop()
        
        
        print("Connection lost. Returning to broadcast mode...")
        threading.Thread(target=self.start_broadcasting, daemon=True).start()

    def stop(self):
        self.running = False
        self.client_connected = False
        if self.control_socket:
            self.control_socket.close()
        if self.telemetry_socket:
            self.telemetry_socket.close()
        self.motor.cleanup()
        self.servo.cleanup()
        GPIO.cleanup()
        print("Server stopped.")

    @staticmethod
    def _create_server_socket(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(1)
        return sock
    def index(self):
        index_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Raspberry Pi Camera</title>
            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    padding-top: 50px;
                }
                .camera-stream {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .camera-stream img {
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center mb-4">Raspberry Pi Camera Stream</h1>
                <div class="camera-stream">
                    <img src="/video" width="1280" height="720">
                </div>
                <div class="text-center">
                    <a href="/wifi" class="btn btn-primary">Manage WiFi</a>
                </div>
            </div>
            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
        return render_template_string(index_html)
    
    def video(self):
        return Response(self.camera.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def favicon(self):
        return Response(status=204)
    
    def wifi_page(self):
        wifi_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WiFi Management</title>
            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    padding-top: 50px;
                }
                .network-item {
                    margin-bottom: 1rem;
                    padding: 1rem;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .network-item:hover {
                    background-color: #f8f9fa;
                    border-color: #007bff;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center mb-4">WiFi Management</h1>
                <div class="d-flex justify-content-between mb-4">
                    <h2>Available Networks</h2>
                    <button class="btn btn-primary" onclick="scanWiFi()">Scan Networks</button>
                </div>
                <div id="wifi-list" class="row"></div>
                <hr>
                <h2>Connect to a Network</h2>
                <form id="connect-form" class="mt-3">
                    <div class="mb-3">
                        <label for="ssid" class="form-label">SSID:</label>
                        <input type="text" class="form-control" id="ssid" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password:</label>
                        <input type="password" class="form-control" id="password">
                    </div>
                    <button type="button" class="btn btn-success" onclick="connectWiFi()">Connect</button>
                </form>
            </div>
        
            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                function scanWiFi() {
                    fetch('/wifi/scan')
                        .then(response => response.json())
                        .then(data => {
                            const wifiList = document.getElementById('wifi-list');
                            wifiList.innerHTML = '';
                            
                            if (data.networks && data.networks.length > 0) {
                                data.networks.forEach(network => {
                                    const networkHTML = `
                                        <div class="col-md-4">
                                            <div class="network-item" onclick="selectNetwork('${network.SSID}')">
                                                <h5>${network.SSID || "Hidden"}</h5>
                                                <p><strong>Signal:</strong> ${network.Signal}%</p>
                                                <p><strong>Bars:</strong> ${network.Bars}</p>
                                            </div>
                                        </div>
                                    `;
                                    wifiList.innerHTML += networkHTML;
                                });
                            } else {
                                wifiList.innerHTML = '<p class="text-muted">No networks found.</p>';
                            }
                        })
                        .catch(error => {
                            console.error('Error scanning WiFi:', error);
                            alert('Error scanning WiFi. Check the console for more details.');
                        });
                }
        
                function selectNetwork(ssid) {
                    document.getElementById('ssid').value = ssid;
                }
        
                function connectWiFi() {
                    const ssid = document.getElementById('ssid').value;
                    const password = document.getElementById('password').value;
                    fetch('/wifi/connect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ ssid, password })
                    }).then(response => response.json())
                      .then(data => {
                          alert(data.message || data.error);
                      })
                      .catch(error => {
                          console.error('Error connecting to WiFi:', error);
                          alert('Error connecting to WiFi. Check the console for more details.');
                      });
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(wifi_html)
    
    def _wifi_scan(self):
        """Skanuje dostępne sieci Wi-Fi."""
        try:
            
            subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], check=True)

            # Pobranie listy sieci
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,BARS', 'dev', 'wifi'], capture_output=True, text=True)

            # Podział wyniku na linie
            networks = []
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 3:  # Upewnij się, że wszystkie pola istnieją
                    ssid, signal, bars = parts[0], parts[1], parts[2]
                    networks.append({
                        "SSID": ssid if ssid else "Hidden",
                        "Signal": signal,
                        "Bars": bars
                    })

            # Jeśli brak sieci, zwróć informację
            if not networks:
                return jsonify({"message": "No networks found."})

            return jsonify({"networks": networks})
        except Exception as e:
            return jsonify({"error": f"Error scanning networks: {str(e)}"})

    def _wifi_connect(self):
        """Łączy się z wybraną siecią Wi-Fi."""
        try:
            os.system('raspi-config nonint disable_overlayfs')
            data = request.get_json()
            ssid = data.get('ssid')
            password = data.get('password')

            if not ssid:
                return jsonify({"error": "SSID is required"}), 400

            if password:
                result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], capture_output=True, text=True)
            else:
                result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], capture_output=True, text=True)

            if result.returncode == 0:
                return jsonify({"message": f"Connected to {ssid}"})
            else:
                return jsonify({"error": f"Failed to connect to network: {result.stderr}"}), 500

        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Failed to connect to network: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
        
    def wifi_scan(self):
        """Skanuje dostępne sieci Wi-Fi."""
        try:
            # Wymuszanie pełnego skanowania
            subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], check=True)

            # Pobranie listy sieci
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,BARS', 'dev', 'wifi'], capture_output=True, text=True)

            # Debugowanie wyniku
            print(f"nmcli output:\n{result.stdout}")

            # Podział wyniku na linie
            networks = []
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 3:  # Upewnij się, że wszystkie pola istnieją
                    ssid, signal, bars = parts[0], parts[1], parts[2]
                    networks.append({
                        "SSID": ssid if ssid else "Hidden",
                        "Signal": signal,
                        "Bars": bars
                    })

            # Jeśli brak sieci, zwróć informację
            if not networks:
                return jsonify({"message": "No networks found."})

            return jsonify({"networks": networks})
        except Exception as e:
            return jsonify({"error": f"Error scanning networks: {str(e)}"})

    def wifi_connect(self):
        """Łączy się z wybraną siecią Wi-Fi."""
        try:
            os.system('raspi-config nonint disable_overlayfs')
            data = request.get_json()
            ssid = data.get('ssid')
            password = data.get('password')

            if not ssid:
                return jsonify({"error": "SSID is required"}), 400

            if password:
                result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], capture_output=True, text=True)
            else:
                result = subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], capture_output=True, text=True)

            if result.returncode == 0:
                return jsonify({"message": f"Connected to {ssid}"})
            else:
                return jsonify({"error": f"Failed to connect to network: {result.stderr}"}), 500

        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Failed to connect to network: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
