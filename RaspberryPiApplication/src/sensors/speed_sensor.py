import RPi.GPIO as GPIO
import time
import math

SENSOR_PIN = 22  # Pin connected to the sensor's signal output
WHEEL_DIAMETER_MM = 45
PULSES_PER_REVOLUTION = 18  # Number of signal changes per full wheel revolution
UPDATE_INTERVAL = 1.0  # Time interval in seconds for speed calculation

class SpeedSensor:
    def __init__(self):
        """
        Inicjalizuje czujnik prędkości.
        
        :param pin_sensor: Numer pinu GPIO podłączonego do transoptora.
        :param wheel_diameter: Średnica koła w mm.
        :param pulses_per_revolution: Liczba impulsów na jeden obrót koła.
        """
        self.pin_sensor = SENSOR_PIN
        self.wheel_diameter = WHEEL_DIAMETER_MM
        self.pulses_per_revolution = PULSES_PER_REVOLUTION

        # Obwód koła w metrach
        self.wheel_circumference_m = (self.wheel_diameter * math.pi) / 1000
        
        # Zmienne pomocnicze
        self.pulse_count = 0
        self.last_time = None

        # Konfiguracja GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Rejestracja przerwania
        GPIO.add_event_detect(self.pin_sensor, GPIO.RISING, callback=self._pulse_callback)

    def _pulse_callback(self, channel):
        """
        Prywatna metoda wywoływana przy każdym impulsie.
        """
        self.pulse_count += 1

    def calculate_speed(self):
        """
        Oblicza prędkość na podstawie zarejestrowanych impulsów.
        
        :return: Prędkość w m/s.
        """
        if self.last_time is None:
            self.last_time = time.time()
            return 0

        current_time = time.time()
        elapsed_time_s = current_time - self.last_time
        self.last_time = current_time
        elapsed_time_h = elapsed_time_s / 3600

        # Obliczanie liczby obrotów
        revolutions = self.pulse_count / self.pulses_per_revolution
        self.pulse_count = 0

        # Obliczanie prędkości w m/s
        wheel_circumference_km = self.wheel_circumference_m / 1000
        speed = (revolutions * wheel_circumference_km) / elapsed_time_h
        return speed

    def cleanup(self):
        """
        Czyści konfigurację GPIO. Do wywołania przy zakończeniu aplikacji.
        """
        GPIO.cleanup()

# Przykład użycia klasy w większej aplikacji
if __name__ == "__main__":
    try:
        # Tworzymy instancję czujnika prędkości
        sensor = SpeedSensor(pin_sensor=17, wheel_diameter=45, pulses_per_revolution=20)
        print("Czujnik prędkości uruchomiony. Naciśnij Ctrl+C, aby zakończyć.")

        while True:
            time.sleep(1)  # Aktualizacja co 1 sekundę
            speed = sensor.calculate_speed()
            print(f"Prędkość: {speed:.2f} m/s")

    except KeyboardInterrupt:
        print("\nZatrzymywanie programu.")
    finally:
        sensor.cleanup()
