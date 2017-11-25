import config_log
import logging
import arm
import car
import vision

class Carm():
    def __init__(self, config):
        """
        Args:
        config (dict): configuration dictionary containing string keys
        for the following values:
            'car' (dict): configuration dict for Car object.
            'arm' (dict): configuration dict for Arm object.

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.car = car.Car(config['car'])
        self.arm = arm.Arm(config['arm'])
        self.cam = vision.Cam(config['cam'])
        # self.eye = vision.Eye(config['eye'])


if __name__ == "__main__":
    # Example configuration for Carm Object
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

    car_config = {
        'left_motor': config_left_dc_motor,
        'right_motor': config_right_dc_motor
    }

    gripper_servo_config = {
        'name': 'gripper',
        'channel': 12,
        'pow_pl': 300,
        'min_pl': 135,
        'max_pl': 300
    }
    right_servo_config = {  # use for forward and backward motion
        'name': 'right',
        'channel': 14,
        'pow_pl': 300,
        'min_pl': 300,  # provided l.current_pl = 450
        'max_pl': 550
    }
    left_servo_config = {  # use for up and down motion
        'name': 'left',
        'channel': 13,
        'pow_pl': 450,
        'min_pl': 150,
        'max_pl': 450
    }
    base_servo_config = {
        'name': 'base',
        'channel': 15,
        'pow_pl': 400,
        'min_pl': None,
        'max_pl': None
    }

    arm_config = {
        'gripper': gripper_servo_config,
        'right': right_servo_config,
        'left': left_servo_config,
        'base': base_servo_config,
        }

config_camera_servo = {
    'name': 'right',
    'channel': 15,
    'pow_pl': 400,
    'min_pl': 325,
    'max_pl': 475}

    config = {
        'car': car_config,
        'arm': arm_config
        }

    carm = Carm(config)
