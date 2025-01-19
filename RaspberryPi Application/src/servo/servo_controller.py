import pigpio
import os

SERVO_PIN = 27
pi = pigpio.pi()
pi.set_mode(SERVO_PIN, pigpio.OUTPUT)

class ServoController:
    def __init__(self, pin=SERVO_PIN):
        self.pin = pin
        os.system("sudo pigpiod")

    def set_angle(self, angle):
        pulse = 1500 + (angle / 180.0) * 600
        pi.set_PWM_frequency(self.pin, 50)
        pi.set_servo_pulsewidth(self.pin, pulse)

    def stop(self):
        pi.set_servo_pulsewidth(self.pin, 0)
    
    def cleanup(self):
        pi.stop()