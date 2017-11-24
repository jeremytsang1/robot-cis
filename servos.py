import time
import Adafruit_PCA9685
import config_log
import logging


class ServoMotor():
    """Class for Servo Motors driven by PCA9685"""
    number_of_motors = 0  # motors created in session (including destroyed)
    instances = list()  # list of all the ServoMotor objects created

    def __init__(self, config):
        """
        Args:
        config (dict): configuration dictionary containing string keys
        for the following values:
            'name' (str): Name of servo motor
            'channel' (int): Channel on PCA9685 board.
            'pow_pl' (int): Pulse level to set at power on.
            'min_pl' (int): minimum safe pulse level (determine in calibration)
            'max_pl' (int): minimum safe pulse level (determine in calibration)

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.pwm = Adafruit_PCA9685.PCA9685()  # Pwm module for PCA9685
        self.pwm.set_pwm_freq(60)  # Set servo period to 1/(60 s^-1)
        self.num = ServoMotor.number_of_motors  # Identifier for servo
        ServoMotor.number_of_motors += 1
        ServoMotor.instances.append(self)

        self.config = config
        self.name = config['name']
        self.channel = self.config['channel']
        self.current_pl = self.config['pow_pl']
        self.power_on()

    def sweep(self, end_pl, pause_time=0.005):
        """Sweeps servo motor from the current position (with respect to pulse
        length) to specified pulse length in unit
        increments. Specified pauses are made between each increment.

        Args:
        end_pl (int): Pulse length to end at (between self.config['min_pl']
        and self.config['max_pl'])
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
        self.pwm.set_pwm(self.channel, 0, self.config['pow_pl'])

    def power_off(self):
        """Sweeps servo to power on position to avoid violent startup."""
        self.sweep(self.config['pow_pl'])


if __name__ == "__main__":
    print()
    # Example configuration for ServoMotor Object
    config_gripper_servo = {
        'name': 'gripper',
        'channel': 12,
        'pow_pl': 300,
        'min_pl': 135,
        'max_pl': 300}
    config_right_servo = {  # use for forward and backward motion
        'name': 'right',
        'channel': 14,
        'pow_pl': 300,
        'min_pl': 300,  # provided l.current_pl = 450
        'max_pl': 550}
    # config_left_servo = {  # use for up and down motion
    #     'name': 'left',
    #     'channel': 13,
    #     'pow_pl': 450,
    #     'min_pl': 150,
    #     'max_pl': 450
    # }
    # config_base_servo = {
    #     'name': 'base',
    #     'channel': 15,
    #     'pow_pl': 400,
    #     'min_pl': None,
    #     'max_pl': None
    # }

    gripper = ServoMotor(config_gripper_servo)
    right = ServoMotor(config_right_servo)
    # left = ServoMotor(config_left_servo)
