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

    enter_menu(robot)


def enter_menu(robot):

    sensor_readings = {
        'irl': list(),
        'irr': list(),
        'uls': list()
    }
    menu_str = generate_menu_str(robot)
    user_cmd = str()
    
    # make a class for command history later
    # cmd_history will list of dicts with each dict having:
    #  -     key (str): keybinding for command (e.g. 'w', '[]', 'line', etc)
    #  - value (float): time indicating how long to execute cmd
    cmd_history = [{user_cmd: float()}]  # key = command, value = how long to run command
    
    user_cmd_count = int()
    start_time = time.time()
    end_time = float()

    try:
        print(menu_str)
        previous_user_cmd = ''
        while user_cmd != 'j':
            user_cmd = input('> ')

            if user_cmd in robot.cmd_dct.keys():
                user_cmd_count += 1

                # record end time of PREVIOUS command
                end_time = time.time()

                # add the previous command's execution time to the history
                cmd_history[user_cmd_count -
                                1][previous_user_cmd] = round(end_time - start_time, 3)

                # make a new command dict for the next commmand
                cmd_history.append({user_cmd: float()})

                # make sure the number of commmands entered is the same as
                # the number of commands stored
                assert len(cmd_history) == user_cmd_count + 1

                # record start time of CURRENT command
                start_time = time.time()

                execute_single_cmd(robot, user_cmd)

                previous_user_cmd = user_cmd
            else:
                print('Please choose VALID a menu command\n')
            print(menu_str)

        # Shutdown
        print("\n\nYour commands this session were: ")
        pprint.pprint(cmd_history)  # find how to save a log of this later
        print('\n')
        robot.power_off()
        print("Goodbye!")
    except:
        robot.power_off()
        time.sleep(10)
        cleanup()


def generate_menu_str(robot):
    # aligning all colons in the menu
    width = max([len(key) for key in robot.cmd_dct.keys()])
    menu_str = '\n'.join([ok.rjust(width) + ": " +
                          robot.cmd_dct[ok][0] for ok in [cmd[0] for cmd in robot.cmd_list]])
    return menu_str


def execute_single_cmd(robot, user_cmd):
    """Executes a single command (user_cmd). Assumes user_cmd is
    a key in robot.cmd_dct.
    """
    # get information for the next command
    tup = robot.cmd_dct[user_cmd]

    if tup[-1] == 'sensor':
        robot.car.brake()
        print(tup[1]())
        # sensor_readings['uls'].append()
    elif len(tup) == 2:  # method has 0 arguments
        tup[1]()
    elif len(tup) == 3:  # method has 1 argument
        tup[1](tup[2])
    elif len(tup) == 4:  # method has 2 arguments
        tup[1](tup[2], tup[3])


def exectute_cmds(robot, cmd_dict):
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
    robot = carm.Carm(config.config_carm)

    robot.car.rm.logger.setLevel(logging.INFO)
    robot.car.lm.logger.setLevel(logging.INFO)

    manual_mode(robot)
    cleanup()
