import config_log
import logging
import arm
import car
import vision
import ir
import ultrasonic
import time
import datetime
import os
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
            ('j', ('quit',)),
        ]
        self.cmd_dct = self.update_cmd_dct()

    def update_cmd_dct(self):
        return {cmd[0]: cmd[1] for cmd in self.cmd_list}

    def add_more_cmds(self, cmds_to_add):
        for cmd in cmds_to_add:
            self.cmd_list.insert(-1, cmd)
        self.update_cmd_dct()


    def power_off(self):
        """Brings the robot to a safe halt. Turns off DC motors and returns
        servo motors to starting positions to prevent violent startup. """
        self.car.brake()
        self.arm.power_off()
        self.cam.power_off()

    def execute_single_cmd(self, user_cmd):
        """Executes a single command (user_cmd). Assumes user_cmd is
        a key in robot.cmd_dct.
        """
        # get information for the next command
        try:
            tup = self.cmd_dct[user_cmd]

            if tup[-1] == 'sensor':
                self.car.brake()
                print(tup[1]())
                # sensor_readings['uls'].append()
            elif len(tup) == 2:  # method has 0 arguments
                tup[1]()
            elif len(tup) == 3:  # method has 1 argument
                tup[1](tup[2])
            elif len(tup) == 4:  # method has 2 arguments
                tup[1](tup[2], tup[3])
        except KeyboardInterrupt:
            self.car.brake()

    def execute_cmds(self, cmds):
        """Reads a series of commands from a specially formatted list or text
        file and executes them in order. If using a list, format in the
        following fashion

        cmd_list = [{'str': <command n>, 'time': <time to execute command n>}]

        If using a text file have the first column indicate the commands
        and the second command indincate the time to execute the commands

        w 1.5
        a 7
        s 2
        d 4

        The function ends the series of commands with a brake() to prevent
        robot from rolling away.

        Args:
        robot (Carm): Carm instance
        cmds (list or str): list containing command data or filename of text file
        containing command data

        Returns:
        None

        """
        if type(cmds) == str:
            try:
                cmds = read_cmds_from_txt(cmds)
            except FileNotFoundError:
                print("File not found")

        for cmd in cmds:
            self.execute_single_cmd(cmd['str'])
            time.sleep(cmd['time'])
        self.execute_single_cmd(' ')

    def read_cmds_from_txt(self, filename):
        """Takes in a text file and returns a command list for execution by a
        Carm object. Text must be formatted with the first column as the
        command string and the second column as the duration of execution
        for said command. Example formatting (do not include # signs or
        anything to the right of them):

        w 2.5  # drives forward for 2.5 seconds
        a 3    # swing turns right for 3 seconds
          1    # brakes for 1 second
        1 2    # looksdown for 2 seconds

        Args:
        filename (str): input file containing command strings and times

        Returns:
        list: list of dicts formatted for execution

        """
        cmds = list()
        with open(filename) as f:
            for line in f:
                if line[0] != ' ':
                    line = line.strip('\n').split()
                    cmds.append({'str': line[0],
                                 'time': int(line[1])})
                    print(line)
                else:
                    line = line.strip('\n').split()
                    cmds.append({'str': ' ',
                                 'time': int(line[0])})
                    print(line)
        return (cmds)

    def write_cmds_to_txt(self, cmds, filename='cmds.txt'):
        """Takes in a list of command dicts and writes the values to a text
        file in the ./cmds subdirectory. Cmds must be a list in the form:

        [{'str': '<command str n>', 'time':<time to execute command n>}
            
        Args:
        cmds (list): list of dicts
        filename (str): filename of output text file
    
        Returns:
        None
    
        """
        # TODO make sure the ./cmds dir exists
        sub_dir = './cmds/'
        if os.path.isfile(sub_dir + filename):
            time_stamp = datetime.datetime.now().isoformat()[
                :19].replace(":", '').replace('T', '-')
            filename = filename.split('.')
            filename[0] += '-' + time_stamp
            filename = '.'.join(filename)
    
        with open(sub_dir + filename, 'w') as f:
            for cmd in cmds:
                line = '{} {}\n'.format(cmd['str'], cmd['time'])
                f.write(line)


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
