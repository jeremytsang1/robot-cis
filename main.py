import logging
import carm
import config
import RPi.GPIO as GPIO
import time
import pprint


def stop():
    """Emergency stop for convenience"""
    robot.car.brake()


def cleanup():
    print("Cleaning up the GPIO!")
    GPIO.cleanup()


def manual_mode(robot):
    """
    Provides a menu for manual control of a Carm object for the user.

    Args:
    robot (Carm): Instance of a Carm object.

    Returns:
    None

    """

    command_dct, command_key_order = generate_command_info(robot)

    enter_menu(command_dct, command_key_order)


def generate_command_info(robot):
    command_dct = {
        # dictionary containing the keybindings and associated
        # commands for the user. The tuple will contain the:
        #  - name of the command
        #  - method to call
        #  - arguments to pass to the method
        #  - (optionally) if command references a sensor the name of the sensor
        #  - (optionally) a marker in the last element to denote it is a sensor
        'w': ('forwards', robot.car.drive, 1),
        's': ('backwards', robot.car.drive, -1),
        'a': ('swing left FWD', robot.car.swing_turn, -1, 1),  # 2 args
        'd': ('swing right FWD', robot.car.swing_turn, 1, 1),  # 2 args
        'q': ('point left', robot.car.point_turn, -1),
        'e': ('point right', robot.car.point_turn, 1),
        'z': ('swing left BACK', robot.car.swing_turn, -1, -1),  # 2 args
        'c': ('swing right BACK', robot.car.swing_turn, 1, -1),  # 2 args
        ' ': ('brake', robot.car.brake),  # 0 args
        '[': ('increment extend', robot.arm.extend, -5),
        ']': ('increment retract', robot.arm.extend, 5),
        'g': ('grab', robot.arm.close_gripper),  # 0 args
        'o': ('opens', robot.arm.open_gripper),  # 0 args
        'n': ('full extend', robot.arm.right.sweep, robot.arm.right.config['max_pl']),
        'p': ('full retract', robot.arm.right.sweep, robot.arm.right.config['min_pl']),
        '1': ('look down', robot.cam.lookdown),  # 0 args
        '2': ('look straight', robot.cam.power_off),  # 0 args
        '3': ('look up', robot.cam.lookup),  # 0 args
        'u': ('check ultrasonic', robot.uls.get_distance, 'uls', 'sensor'),
        'line': ('enter line following mode', line_following_mode, robot),
        'j': ('quit',),
    }

    command_key_order = [
        'w',
        'a',
        's',
        'd',
        'e',
        'q',
        'z',
        'c',
        ' ',
        '[',
        ']',
        'g',
        'o',
        'n',
        'p',
        '1',
        '2',
        '3',
        'u',
        'line',
        'j']

    return command_dct, command_key_order


def enter_menu(command_dct, command_key_order):

    sensor_readings = {
        'irl': list(),
        'irr': list(),
        'uls': list()
    }
    menu_str = generate_menu_str(command_dct, command_key_order)
    user_command = str()
    
    # make a class for command history later
    # command_history will list of dicts with each dict having:
    #  -     key (str): keybinding for command (e.g. 'w', '[]', 'line', etc)
    #  - value (float): time indicating how long to execute command
    command_history = [{user_command: float()}]  # key = command, value = how long to run command
    
    user_command_count = int()
    start_time = time.time()
    end_time = float()

    try:
        print(menu_str)
        previous_user_command = ''
        while user_command != 'j':
            user_command = input('> ')

            if user_command in command_dct.keys():
                end_time = time.time()
                user_command_count += 1

                # add the previous command's execution time to the history
                command_history[user_command_count -
                                1][previous_user_command] = round(end_time - start_time, 3)

                # make a new command dict for the next commmand
                command_history.append({user_command: float()})

                # make sure the number of commmands entered is the same as
                # the number of commands stored
                assert len(command_history) == user_command_count + 1

                start_time = time.time()

                # get information for the next command
                tup = command_dct[user_command]

                if tup[-1] == 'sensor':
                    robot.car.brake()
                    print(tup[1]())
                    # sensor_readings['uls'].append()
                    continue
                elif len(tup) == 2:  # method has 0 arguments
                    tup[1]()
                elif len(tup) == 3:  # method has 1 argument
                    tup[1](tup[2])
                elif len(tup) == 4:  # method has 2 arguments
                    tup[1](tup[2], tup[3])
                previous_user_command = user_command
            else:
                print('Please choose VALID a menu command\n')
            print(menu_str)

        # Shutdown
        print("\n\nYour commands this session were: ")
        pprint.pprint(command_history)  # find how to save a log of this later
        print('\n')
        robot.power_off()
        print("Goodbye!")
    except:
        robot.power_off()
        time.sleep(10)
        cleanup()


def generate_menu_str(command_dct, command_key_order):
    # aligning all colons in the menu
    width = max([len(key) for key in command_dct.keys()])
    menu_str = '\n'.join([ok.rjust(width) + ": " +
                          command_dct[ok][0] for ok in command_key_order])
    return menu_str


def exectute_commands(robot, command_dict):
    pass


def line_following_mode(robot):
    """Makes the robot enter line following mode. Drives in in a straight
    line till reaches the end of the masking tape (i.e. both sensors
    interrupted).

    Args:
    robot (Carm): instance of Carm class

    Returns:
    None

    """
    def interrupt_neither(left, right):
        return left and right

    def interrupt_both(left, right):
        return (not left) and (not right)

    def interrupt_left(left, right):
        return left and not right

    def interrupt_right(left, right):
        return right and not left

    try:
        robot.car.drive(1)
        position = {'left_of_line': False,
                    'right_of_line': False}
        movement = {'brake': False,
                    'turning_left': False,
                    'turning_right': False,
                    'driving_forward': False}

        movement['brake'] = False

        while not movement['brake']:
            time.sleep(.1)  # delay to check sensors

            movement['brake'] = interrupt_both(robot.irl.check(),
                                               robot.irr.check())
        robot.car.brake()
    except:
        robot.power_off()
        cleanup()


if __name__ == "__main__":
    robot = carm.Carm(config.carm_config)

    robot.car.rm.logger.setLevel(logging.INFO)
    robot.car.lm.logger.setLevel(logging.INFO)

    manual_mode(robot)

# direction_dct = {
#     'w': robot.car.drive(1),
#     's': robot.car.drive(-1),
#     'a': robot.car.point_turn(-1),
#     'd': robot.car.point_turn(1),
#     'q': robot.car.swing_turn(-1, 1),
#     'e': robot.car.swing_turn(1, 1),
#     'z': robot.car.swing_turn(-1, -1),
#     'c': robot.car.swing_turn(1, -1),
#     ' ': robot.car.brake()}
