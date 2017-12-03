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

    option_dct = {
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
    option_key_order = [
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

    enter_menu(option_dct, option_key_order)


def enter_menu(option_dct, option_key_order):

    sensor_readings = {
        'irl': list(),
        'irr': list(),
        'uls': list()
    }
    menu_str = generate_menu_str(option_dct, option_key_order)
    user_option = str()
    option_history = [{user_option: float()}]  # key = command, value = how long to run command
    user_option_count = int()
    start_time = time.time()
    end_time = float()

    try:
        print(menu_str)
        while user_option != 'j':
            previous_user_option = user_option
            user_option = input('> ')
            end_time = time.time()
            user_option_count += 1
            option_history[user_option_count -
                           1][previous_user_option] = round(end_time - start_time, 3)
            option_history.append({user_option: float()})

            # make sure the number of commmands entered is the same as
            # the number of commands stored
            assert len(option_history) == user_option_count + 1
            start_time = time.time()
            print('hello')
            if user_option in option_dct.keys():
                tup = option_dct[user_option]
                if tup[-1] == 'sensor':
                    print(tup[1]())
                    # sensor_readings['uls'].append()
                    continue
                elif len(tup) == 2:
                    tup[1]()
                elif len(tup) == 3:
                    tup[1](tup[2])
                elif len(tup) == 4:
                    tup[1](tup[2], tup[3])
            else:
                print('Please choose a menu option\n')
            print(menu_str)

        # Shutdown
        pprint.pprint(option_history)  # find how to save a log of this later
        robot.power_off()
        print("Goodbye!")
    except:
        robot.power_off()
        time.sleep(10)
        cleanup()


def generate_menu_str(option_dct, option_key_order):
    # aligning all colons in the menu
    width = max([len(key) for key in option_dct.keys()])
    menu_str = '\n'.join([ok.rjust(width) + ": " +
                          option_dct[ok][0] for ok in option_key_order])
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
    robot.irr.logger.setLevel(logging.INFO)
    robot.irl.logger.setLevel(logging.INFO)

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
