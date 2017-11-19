import config_log
import logging
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)


class DCMotor():
    """Class for DC motors driven by L298N Dual H-Bridge."""
    number_of_motors = 0  # how many motors have been instantiated so far
    instances = list()

    def __init__(self, name, pin_forward, pin_backward):
        """
        Args:
            name (str): name of motor
            pin_forward (int): BCM number for forward GPIO pin
            pin_forward (int): BCM number for backward GPIO pin
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.state = 0  # 0 if motor off, 1 if motor on
        self.direction = 0  # (-1, 0, 1) = (backward, off, forward)
        self.name = name
        self.pins = {'forward': pin_forward,
                     'backward': pin_backward}
        self.num = DCMotor.number_of_motors
        DCMotor.number_of_motors += 1
        DCMotor.instances.append(self)
        self.setup(self.pins)

    def setup(self, pins):
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def set(self, direction):
        """
        Sets the motor on or off and in the desired direction.

        Args:
            direction (int): Must be an in (-1, 0, 1).
            -1 sets the motor running backwards.
             1 sets the motor running forwards.
             0 turns the motor off.

        Returns:
            None

        """
        if direction in (-1, 0, 1):
            self.direction = direction
            self.logger.debug("(pin, output): "
                              "({}, {})"
                              ", "
                              "({}, {})".format(
                                  self.pins['forward'],
                                  GPIO.input(self.pins['forward']),
                                  self.pins['backward'],
                                  GPIO.input(self.pins['backward'])))
            if direction == -1:
                self.state = 1
                GPIO.output(self.pins['forward'], GPIO.LOW)
                GPIO.output(self.pins['backward'], GPIO.HIGH)
            elif direction == 0:
                self.state = 0
                GPIO.output(self.pins['forward'], GPIO.LOW)
                GPIO.output(self.pins['backward'], GPIO.LOW)
            else:
                self.state = 1
                GPIO.output(self.pins['forward'], GPIO.HIGH)
                GPIO.output(self.pins['backward'], GPIO.LOW)
        else:
            self.logger.debug("Attempted to set direction to: {}".format(
                direction))
            raise ValueError("Direction must be set to -1, 0, or 1")

    def set_time(self, direction, time=0):
        """
        Sets the motor on or off in the desired direction for a
        specified amount of time.

        Args:
            direction (int): Must be an in (-1, 0, 1).
            -1 sets the motor running backwards.
             1 sets the motor running forwards.
             0 turns the motor off.
            time: Length of time the motor runs in seconds.

        Returns:
            None
        """
        self.set(direction)
        sleep(time)
        self.stop()

    def stop(self):
        """Turns the motor off.
        """
        self.set(0)

    def __str__(self):
        motor_str = "motor_num: {}".format(self.num)
        for direction in self.pins.keys():
            motor_str += '\n{} pin: (pin number: {}, pin output: {})'.format(
                direction,
                self.pins[direction],
                GPIO.input(self.pins[direction]))
        return motor_str


if __name__ == "__main__":
    # Testing
    print()
    right = DCMotor("left", 6, 5)    # motor 0
    left = DCMotor("right", 16, 12)  # motor 1

    left.set_time(1, .25)
    right.set_time(1, .25)
    GPIO.cleanup()
