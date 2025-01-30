import struct
import threading

class TelemetryDataModel:
    def __init__(self):
        self.speed = 0
        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        self.acceleration_z = 0.0
        self.voltage = 0.0
        self.current = 0.0
        self.wifi_signal_strength = 0
        self.lock = threading.Lock()

    def update(self, data):
        with self.lock:
            speed, acceleration_x, acceleration_y, acceleration_z, voltage, current, wifi_signal_strength = struct.unpack("ffffffi", data)
            self.speed = speed
            self.acceleration_x = acceleration_x
            self.acceleration_y = acceleration_y
            self.acceleration_z = acceleration_z
            self.voltage = voltage
            self.current = current
            self.wifi_signal_strength = wifi_signal_strength

    def get_acceleration_x(self):
        with self.lock:
            return self.acceleration_x
    
    def get_acceleration_y(self):
        with self.lock:
            return self.acceleration_y
    
    def get_acceleration_z(self):
        with self.lock:
            return self.acceleration_z