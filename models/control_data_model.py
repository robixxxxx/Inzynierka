import struct
import threading
from functools import reduce

class ControlDataModel:
    def __init__(self):
        self.gear = 0
        self.steering = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.functions = [0] * 8 # 0: ligts, 1:horn, 2-7: not used
        self.lock = threading.Lock()

    def update(self, gear, steering, throttle, brake, functions):
        with self.lock:
            self.gear = gear
            self.steering = steering
            self.throttle = throttle
            self.brake = brake
            self.functions = functions

    def pack_data(self):
        gear = self.gear
        print(self.steering)
        steering = max(-128, min(127, int(self.steering * 127)))
        gas = int(self.throttle * 100) if self.throttle > 0 else 0
        brake = int(self.brake * 100) if self.brake > 0 else 0
        functions = reduce(lambda x, y: (x << 1) | y, reversed(self.functions))

        try:
            with self.lock:
                packed_data = struct.pack("bbBBB", gear, steering, gas, brake, functions)
                return packed_data
        except struct.error as e:
            with self.lock:
                print(f"Error packing control data: {e}")
                return None