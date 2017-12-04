import config_log
import logging
import arm
import car
import vision
import ir
import ultrasonic
import RPi.GPIO as GPIO

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
        self.irl = ir.IRSensor(config['irl'])
        self.irr = ir.IRSensor(config['irr'])
        self.uls = ultrasonic.UltrasonicSensor(config['uls'])
        self.cmd_list = [
            ('w', ('forwards', self.car.drive, 1)),
            ('s', ('backwards', self.car.drive, -1)),
            ('a', ('swing left FWD', self.car.swing_turn, -1, 1)),  # 2 args
            ('d', ('swing right FWD', self.car.swing_turn, 1, 1)),  # 2 args
            ('q', ('point left', self.car.point_turn, -1)),
            ('e', ('point right', self.car.point_turn, 1)),
            ('z', ('swing left BACK', self.car.swing_turn, -1, -1)),  # 2 args
            ('c', ('swing right BACK', self.car.swing_turn, 1, -1)),  # 2 args
            (' ', ('brake', self.car.brake)),  # 0 args
            ('[', ('increment extend', self.arm.extend, -5)),
            (']', ('increment retract', self.arm.extend, 5)),
            ('g', ('grab', self.arm.close_gripper)),  # 0 args
            ('o', ('opens', self.arm.open_gripper)),  # 0 args
            ('n', ('full extend', self.arm.right.sweep, self.arm.right.config['max_pl'])),
            ('p', ('full retract', self.arm.right.sweep, self.arm.right.config['min_pl'])),
            ('1', ('look down', self.cam.lookdown)),  # 0 args
            ('2', ('look straight', self.cam.power_off)),  # 0 args
            ('3', ('look up', self.cam.lookup)),  # 0 args
            ('u', ('check ultrasonic', self.uls.get_distance, 'uls', 'sensor')),
            # ('line', ('enter line following mode', line_following_mode, self)),
            ('j', ('quit',)),
        ]
        self.cmd_dct = {cmd[0]: cmd[1] for cmd in self.cmd_list}

    def power_off(self):
        """Brings the robot to a safe halt. Turns off DC motors and returns
        servo motors to starting positions to prevent violent startup. """
        self.car.brake()
        self.arm.power_off()
        self.cam.power_off()


if __name__ == "__main__":
    # Example configuration for Carm Object
    config_left_dc_motor = {
        'name': 'left',
        'pin_forward': 16,
        'pin_backward': 12
    }

    config_right_dc_motor = {
        'name': 'right',
        'pin_forward': 6,
        'pin_backward': 5
    }


    config_car = {
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

    config_arm = {
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
    
    config_ir_left = {'name': 'left',
                      'pin': 14}
    config_ir_right = {'name': 'right',
                       'pin': 15}

    config_ultrasonic = {'trig': 23,
                         'echo': 24}

    config = {
        'car': config_car,
        'arm': config_arm,
        'cam': config_camera_servo,
        'irl': config_ir_left,
        'irr': config_ir_right,
        'uls': config_ultrasonic,
        }

    carm = Carm(config)
