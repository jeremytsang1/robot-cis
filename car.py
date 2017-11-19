import config_log
import logging
import dc_motors as dcm
from dc_motors import GPIO


class Car():
    """Class for car base of CARM."""

    def __init__(self, left_motor, right_motor):
        """
        Args:
            left_motor (DCMotor): DCMotor object for left rear wheel
            right_motor (DCMotor): DCMotor object for right rear wheel
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.lm = left_motor
        self.logger.debug("left_motor:\n{}".format(self.lm.__str__()))
        self.rm = right_motor
        self.logger.debug("right_motor:\n{}".format(self.rm.__str__()))

    def brake(self):
        """
        Stops both left and right car motors.

        Args:
        None

        Returns:
        None

        """
        self.lm.stop()
        self.rm.stop()

    def __str__(self):
        self.lm.str + '\n' + self.rm.str


if __name__ == "__main__":
    print()
    right = dcm.DCMotor("left", 6, 5)    # motor 0
    left = dcm.DCMotor("right", 16, 12)  # motor 1

    car = Car(left, right)
    dcm.GPIO.cleanup()
