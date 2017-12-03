import config_log
import logging
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


class IRSensor():
    """Class for OSOYOO IR Infrared Obstacle Avoidance Sensor Module"""
    def __init__(self, config):
        """
        Args:
        config (dict): configuration dictionary containing string keys
        for the following values:
            'name' (str): name of IR sensor
            'pin' (int): BCM number for input (sensor --> pi)  GPIO pin

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.pin = config['pin']
        self.name = config['name']
        self.setup(self.pin)  # 1: no interrupt, 0: interrupt
        self.signal = self.check()

    def setup(self, pin):
        GPIO.setup(pin, GPIO.IN)

    def check(self):
        """Gives a value based on if there is an object blocking or reflecting
        back to the sensor. Gives 1 if there is no
        obstruction/interruption and 0 if there is.

        Args:
        None.

        Returns:
        int: Returns 1 if there is no obstruction, 0 if there is an
        obstruction.
        """
        self.signal = GPIO.input(self.pin)
        interrupt = str()
        if self.signal == 0:
            pass
        elif self.signal == 1:
            interrupt = "no "
        else:
            print("Check sensor")
        return self.signal

    def run_sensor(self, timeout=0, interval=1):
        """Continuously checks if there is an obstruction blocking the sensor
        for user specified time or indefinitely in user specified
        intervals.

        Args:
        timeout (float): Number of seconds to run the sensor. If set to 0,
        runs indefinitely.
        interval (float): How often to check sensors (in seconds).

        Returns:
        None.

        """
        if timeout > 0:
            t0, t1 = time.time(), time.time()
            while t1 - t0 < timeout:
                self.check()
                t1 = time.time()
                time.sleep(interval)
        else:  # check indefinitely
            try:
                while True:
                    self.check()
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.logger.debug("{} sensor stopped by user".format(
                    self.name))


if __name__ == "__main__":
    print()
    config_ir_left = {'name': 'left',
                      'pin': 14}
    config_ir_right = {'name': 'right',
                       'pin': 15}

    ir_left = IRSensor(config_ir_left)
    ir_right = IRSensor(config_ir_right)
