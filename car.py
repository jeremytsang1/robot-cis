import config_log
import logging
import dc_motors as dcm
from dc_motors import GPIO
from time import sleep


class Car():
    """Class for car base of CARM."""

#    def __init__(self, left_motor, right_motor):
    def __init__(self, config):
        """
        Args:
        config (dict): configuration dictionary containing string keys
        for the following values:
            'left_motor' (DCMotor): DCMotor object for left rear wheel
            'right_motor' (DCMotor): DCMotor object for right rear wheel

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.lm = dcm.DCMotor(config['left_motor'])
        self.logger.debug('left_motor:\n{}'.format(self.lm.__str__()))
        self.rm = dcm.DCMotor(config['right_motor'])
        self.motor_lst = [self.lm, self.rm]  # for looping over motors
        self.logger.debug('right_motor:\n{}'.format(self.rm.__str__()))

    def brake(self):
        """Stops both left and right car motors.

        Args:
        None

        Returns: None

        """
        self.lm.stop()
        self.rm.stop()

    def drive(self, direction, drive_time=-1):
        """Sets the car driving in a straight line indefinitely or for some
        specified time.

        Args:
        direction (int): Can take any value in (-1, 0, 1).
          - -1: car drives backwards
          -  0: car brakes
          -  1: car drives forward

        drive_time (float or int): determines how long the car drives
          - values specify how long the car drives in seconds
          - negative values cause the car to drive indefinitely

        Returns:
        None

        """
        if drive_time >= 0:
            self.lm.set_direction(direction)
            self.rm.set_direction(direction)
            sleep(drive_time)
            self.brake()
        elif drive_time < 0:
            self.lm.set_direction(direction)
            self.rm.set_direction(direction)
        else:
            self.logger.error('Entered invalid value for drive_time')
            self.brake()

    def swing_turn(self, horizontal_direction, vertical_direction,
                   turn_time=-1, num_turns=1, wait_interval=.25):
        """Causes the car to perform a series of swing turns (operating only a
single motor to turn the car) or do an indefinite swing turn.

        Args:
        horizontal_direction (int): Specfies side-to-side turning.
          - -1: Turn left.
          -  1: Turn right.
        vertical_direction (int): Specfies forward-reverse travel.
          - -1: Travel backwards.
          -  0: Stop.
          -  1: Travel forwards.
        turn_time (float): Duration of each turn.
          - nonnegative values: Duration of each turn.
          - negative values: Turn indefinitely.
        num_turns (int): Non negative int. Specifies how many turns to perform.
        wait_interval (float): Delay between each turn.

        Returns:
        None

        """
        self.brake()  # make sure no unnecessary motors running
        if turn_time < 0:  # indefinite turning
            # run the left motor (motor_lst[0]) for turning right and
            # the right motor (motor_list[1]) for turning left
            self.motor_lst[::horizontal_direction][0].set_direction(
                vertical_direction)
        else:  # turning for specific time
            for i in range(num_turns):
                self.motor_lst[::horizontal_direction][0].set_time(
                    vertical_direction, turn_time)
                sleep(wait_interval)

    def point_turn(self, horizontal_direction,
                   turn_time=-1, num_turns=1, wait_interval=.25):
        """Causes the car to perform a series of point turns (operating both
motors in opposite directions) or do an indefinite point turn.

        Args:
        horizontal_direction (int): Specfies side-to-side turning.
          - -1: Turn left.
          -  1: Turn right.
        turn_time (float): Duration of each turn.
          - nonnegative values: Duration of each turn.
          - negative values: Turn indefinitely.
        num_turns (int): Non negative int. Specifies how many turns to perform.
        wait_interval (float): Delay between each turn.

        Returns:
        None

        """
        self.brake()  # make sure no unnecessary motors running
        if turn_time < 0:  # indefinite turning
            self.motor_lst[::horizontal_direction][0].set_direction(1)
            self.motor_lst[::horizontal_direction][1].set_direction(-1)
        else:  # specified turn time
            for i in range(num_turns):
                self.motor_lst[::horizontal_direction][0].set_direction(1)
                self.motor_lst[::horizontal_direction][1].set_direction(-1)
                sleep(turn_time)
                self.brake()
                sleep(wait_interval)
            self.brake()


if __name__ == "__main__":
    print()

    config_left_dc_motor = {
        'name': 'left',
        'pin_forward': 6,
        'pin_backward': 5
    }
    config_right_dc_motor = {
        'name': 'right',
        'pin_forward': 16,
        'pin_backward': 12
    }

    config = {'left_motor': config_left_dc_motor,
              'right_motor': config_right_dc_motor}

    car = Car(config)

    dcm.GPIO.cleanup()
