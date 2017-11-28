# Libraries
import config_log
import logging
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


class UltrasonicSensor():
    """Class for Elegoo HC-SR04 Ultrasonic Module Distance Sensor"""

    speed_of_sound = 34300  # cm/s

    def __init__(self, config):
        """
        Args:
        config (dict): configuration dictionary containing string keys
        for the following values:
            'trig' (int): BCM number for tigger (output pi --> sensor) GPIO pin
            'echo' (int): BCM number for echo (input sensor --> pi) GPIO pin

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.config = config
        self.trig = self.config['trig']
        self.echo = self.config['echo']
        self.setup()

    def setup(self):
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def get_distance(self):
        """Gets distance in straight line emanating from sensor by computing
        the time it takes for sound to travel from the sensor to the
        nearest object and back again.

        Args:
        None

        Returns:
        float: Distance from sensor in centimeters.
        """
        t0, t1 = float(), float()

        # Send 0.01 ms pulse to Trigger
        GPIO.output(self.trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig, GPIO.LOW)

        # set starting time before receiving signal
        while GPIO.input(self.echo) == 0:
            t0 = time.time()

        # set ending time once signal received
        while GPIO.input(self.echo) == 1:
            t1 = time.time()

        return ((t1 - t0) * self.speed_of_sound) / 2  # in cm


if __name__ == "__main__":

    config_ultrasonic = {'trig': 23,
                         'echo': 24}
    u_sensor = UltrasonicSensor(config_ultrasonic)
    while True:
        print(round(u_sensor.get_distance(), 1))
        time.sleep(.25)
