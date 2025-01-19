import RPi.GPIO as GPIO

L9110S_PIN_A = 18
L9110S_PIN_B = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(L9110S_PIN_A, GPIO.OUT)
GPIO.setup(L9110S_PIN_B, GPIO.OUT)
pwmA = GPIO.PWM(L9110S_PIN_A, 1000)
pwmB = GPIO.PWM(L9110S_PIN_B, 1000)
pwmA.start(0)
pwmB.start(0)

class L9110SMotorDriver:
    def __init__(self):
        pass

    def _set_speed_percent(self, speed_percent, brake_percent, gear):
        if brake_percent > speed_percent:
            return brake_percent
        if speed_percent>0:
                return 50 + (gear*10*(speed_percent/100.0))
        else:
            return 0
    
    def set_power(self, speed_percent, brake_percent, gear):
        if gear == -1:
            speed_percent = brake_percent if brake_percent > speed_percent else speed_percent
            pwmA.ChangeDutyCycle(brake_percent)
            pwmB.ChangeDutyCycle(speed_percent)
        elif gear == 0:
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)
        elif gear > 0:
            speed_percent = self._set_speed_percent(speed_percent, brake_percent, gear)
            pwmA.ChangeDutyCycle(speed_percent)
            pwmB.ChangeDutyCycle(brake_percent)
        else:
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)
    
    def stop(self):
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)

    def cleanup(self):
        pwmA.stop()
        pwmB.stop()