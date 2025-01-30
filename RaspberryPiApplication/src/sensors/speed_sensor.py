import RPi.GPIO as GPIO
import time
import math

SENSOR_PIN = 22  # Pin connected to the sensor's signal output
WHEEL_DIAMETER_MM = 45
PULSES_PER_REVOLUTION = 18  # Number of signal changes per full wheel revolution
UPDATE_INTERVAL = 1.0  # Time interval in seconds for speed calculation

class SpeedSensor:
    def __init__(self):
        self.pin_sensor = SENSOR_PIN
        self.wheel_diameter = WHEEL_DIAMETER_MM
        self.pulses_per_revolution = PULSES_PER_REVOLUTION

        self.wheel_circumference_m = (self.wheel_diameter * math.pi) / 1000
        
        self.pulse_count = 0
        self.last_time = None

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.pin_sensor, GPIO.RISING, callback=self._pulse_callback)

    
    def _pulse_callback(self, channel):
        self.pulse_count += 1

    def calculate_speed(self):
        if self.last_time is None:
            self.last_time = time.time()
            return 0

        current_time = time.time()
        elapsed_time_s = current_time - self.last_time
        self.last_time = current_time
        elapsed_time_h = elapsed_time_s / 3600

        # Calculating the number of revolutions
        revolutions = self.pulse_count / self.pulses_per_revolution
        self.pulse_count = 0

        # calculation of the speed in km/h
        wheel_circumference_km = self.wheel_circumference_m / 1000
        speed = (revolutions * wheel_circumference_km) / elapsed_time_h
        return speed

    def cleanup(self):
        GPIO.cleanup()
