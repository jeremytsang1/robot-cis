import time
import Adafruit_PCA9685
import config_log
import logging


class ServoMotor():
    """Class for Servo Motors driven by PCA9685"""
    number_of_motors = 0  # motors created in session (including destroyed)
    instances = list()  # list of all the ServoMotor objects created

    def __init__(self, cals):
        """
        Args:
        name (str): Name of servo motor.
        cals (dct): dct containing calibration info for motor.

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.pwm = Adafruit_PCA9685.PCA9685()  # Pwm module for PCA9685
        self.pwm.set_pwm_freq(60)  # Set servo period to 1/(60 s^-1)
        self.cals = cals  # Pulse lengths determined in physical calibration
        self.name = cals['name']  # For convenience
        self.channel = self.cals['channel']  # On PCA9685 board
        self.num = ServoMotor.number_of_motors  # Identifier for servo

        ServoMotor.number_of_motors += 1
        ServoMotor.instances.append(self)

        self.current_pl = self.cals['pow_pl']
        self.power_on()

    def sweep(self, end_pl, pause_time=0.005):
        """Sweeps servo motor from the current position (with respect to pulse
        length) to specified pulse length in unit
        increments. Specified pauses are made between each increment.

        Args:
        end_pl (int): Pulse length to end at (between self.cals['min_pl']
        and self.cals['max_pl'])
        pause_time (float): Time in seconds to wait between each jump.

        Returns:
        None

        """
        step = -1 if (end_pl - self.current_pl) < 0 else 1
        while self.current_pl != end_pl:
            self.current_pl += step
            self.pwm.set_pwm(self.channel, 0, self.current_pl)
            time.sleep(pause_time)

    def power_on(self):
        """Moves servo to the power on position. Make sure to always run
        ServoMotor.power_off() before shutting off servos.

        """
        self.pwm.set_pwm(self.channel, 0, self.cals['pow_pl'])

    def power_off(self):
        """Sweeps servo to power on position to avoid violent startup."""
        self.sweep(self.cals['pow_pl'])


if __name__ == "__main__":
    pass
