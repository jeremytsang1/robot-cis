import logging
import carm
import config
import RPi.GPIO as GPIO
import time
import pprint
import datetime
import os


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

    menu_str = generate_menu_str(robot)
    user_cmd = str()
    
    # make a class for command history later
    # cmd_history will list of dicts with each dict having:
    #  -     key (str): keybinding for command (e.g. 'w', '[]', 'line', etc)
    #  - value (float): time indicating how long to execute command
    cmd_history = [{'str': user_cmd,
                    'time': float()}]
    
    user_cmd_count = int()
    start_time = time.time()
    end_time = float()

    try:
        print(menu_str)
        while user_cmd != 'j':
            print(cmd_history)
            user_cmd = input('> ')

            if user_cmd in robot.cmd_dct.keys():
                user_cmd_count += 1

                # record end time of PREVIOUS command
                end_time = time.time()

                # add the previous command's execution time to the history
                cmd_history[user_cmd_count -
                            1]['time'] = round(end_time - start_time, 3)

                # make a new command dict for the next commmand
                cmd_history.append({'str': user_cmd, 'time': float()})

                # make sure the number of commmands entered is the same as
                # the number of commands stored
                assert len(cmd_history) == user_cmd_count + 1

                # record start time of CURRENT command
                start_time = time.time()

                execute_single_cmd(robot, user_cmd)

            else:
                print('Please choose VALID a menu command\n')
            print(menu_str)

        # Shutdown
        cmd_history = cmd_history[1:]  # Omits the '' cmd
        print("\n\nYour commands this session were: ")
        write_cmds_to_txt(cmd_history)
        pprint.pprint(cmd_history)
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
    try:
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
    except KeyboardInterrupt:
        stop()


def execute_cmds(robot, cmds):
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
    def ex(cmd_str, robot=robot):
        execute_single_cmd(robot, cmd_str)

    if type(cmds) == str:
        try:
            cmds = read_cmds_from_txt(cmds)
        except FileNotFoundError:
            print("File not found")

    for cmd in cmds:
        ex(cmd['str'])
        time.sleep(cmd['time'])
    ex(' ')


def read_cmds_from_txt(filename):
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


def write_cmds_to_txt(cmds, filename='cmds.txt'):
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

    # Example Commands
    cmds = [
        {'str': 'n', 'time': 2},
        {'str': 'p', 'time': 2},
        {'str': 'g', 'time': 1},
        {'str': 'o', 'time': 1},
        {'str': '3', 'time': 1},
        {'str': '1', 'time': 1},
        {'str': '2', 'time': 1},
    ]

    right_90 = [{'str': 'd', 'time': 0.523},
                {'str': 's', 'time': 0.641},
                {'str': 'd', 'time': 0.912},
                {'str': 's', 'time': 0.736},
                {'str': 'd', 'time': 1.129},
                {'str': 's', 'time': 0.734},
                {'str': 'd', 'time': 1.288},
                {'str': 'd', 'time': 0.444},
                {'str': 's', 'time': 0.763},
                {'str': 'd', 'time': 1.108},
                {'str': 's', 'time': 0.664},
                {'str': 'd', 'time': 1.076},
                {'str': 's', 'time': 0.777},
                {'str': 'd', 'time': 1.163},
                {'str': 's', 'time': 0.758},
                {'str': 'd', 'time': 1.107},
                {'str': 's', 'time': 0.668},
                {'str': 'd', 'time': 1.303},
                {'str': 's', 'time': 0.648},
                {'str': 'd', 'time': 1.46},
                {'str': 's', 'time': 0.689},
                {'str': 'd', 'time': 1.43},
                {'str': 's', 'time': 0.805},
                {'str': 'd', 'time': 2.049},
                {'str': 's', 'time': 1.041},
                {'str': ' ', 'time': 14.953}]

    left_90 = [{'str': 'a', 'time': 1.046},
               {'str': 's', 'time': 0.896},
               {'str': 'a', 'time': 1.022},
               {'str': 'a', 'time': 0.853},
               {'str': 's', 'time': 1.035},
               {'str': 'a', 'time': 1.28},
               {'str': 's', 'time': 1.088},
               {'str': 'a', 'time': 1.367},
               {'str': 's', 'time': 1.055},
               {'str': 'a', 'time': 1.327},
               {'str': 's', 'time': 0.918},
               {'str': 'a', 'time': 1.152},
               {'str': 's', 'time': 1.286},
               {'str': 'a', 'time': 1.196},
               {'str': 's', 'time': 1.067},
               {'str': 'a', 'time': 1.185},
               {'str': 's', 'time': 1.534},
               {'str': 'a', 'time': 2.046},
               {'str': 's', 'time': 0.773},
               {'str': 'd', 'time': 0.515},
               {'str': ' ', 'time': 9.85},
               {'str': 'j', 'time': 0.0}]

