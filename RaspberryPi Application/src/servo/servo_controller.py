import RPi.GPIO as GPIO
import time

SERVO_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

class ServoController:
    def __init__(self, pin=SERVO_PIN):
        self.pin = pin
        self.pwm = GPIO.PWM(self.pin, 50)  # 50Hz PWM frequency
        self.pwm.start(0)

    def set_angle(self, angle):
        duty = 2.5 + (angle / 180.0) * 10
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)  # Allow time for the servo to move

    def stop(self):
        self.pwm.ChangeDutyCycle(0)
    
    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()

# import pigpio

# SERVO_PIN = 27
# pi = pigpio.pi()
# pi.set_mode(SERVO_PIN, pigpio.OUTPUT)

# class ServoController:
#     def __init__(self, pin=SERVO_PIN):
#         self.pin = pin

#     def set_angle(self, angle):
#         pulse = 1500 + (angle / 180.0) * 600
#         pi.set_PWM_frequency(self.pin, 50)
#         pi.set_servo_pulsewidth(self.pin, pulse)

#     def stop(self):
#         pi.set_servo_pulsewidth(self.pin, 0)
    
#     def cleanup(self):
#         pi.stop()