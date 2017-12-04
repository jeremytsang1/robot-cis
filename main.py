import logging
import carm
import config
import RPi.GPIO as GPIO
import time
import pprint
from line_mode import line_following_mode
# import face

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

                robot.execute_single_cmd(user_cmd)

            else:
                print('Please choose VALID a menu command\n')
            if user_cmd not in ('u', 'irl', 'irr'):
                print(menu_str)

        # Shutdown
        cmd_history = cmd_history[1:]  # Omits the '' cmd
        print("\n\nYour commands this session were: ")
        robot.write_cmds_to_txt(cmd_history)
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

