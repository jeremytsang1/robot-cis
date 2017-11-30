import logging
import carm
import config
import RPi.GPIO as GPIO
import time


def stop():  # emergency stop
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
    option_key = str()

    option_dct = {
        'w': ('forwards', robot.car.drive, 1),
        'a': ('point left', robot.car.drive, -1),
        's': ('backwards', robot.car.point_turn, -1),
        'd': ('point left', robot.car.point_turn, 1),
        'e': ('swing right FWD', robot.car.swing_turn, -1, 1),  # 2 args
        'q': ('swing left FWD', robot.car.swing_turn, 1, 1),  # 2 args
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
        'line',
        'j']

    # aligning all colons in the menu
    width = max([len(key) for key in option_dct.keys()])
    menu_str = '\n'.join([ok.rjust(width) + ": " +
                          option_dct[ok][0] for ok in option_key_order]) + '\n> '

    while option_key != 'j':
        print()
        option_key = input(menu_str)
        if option_key in option_dct.keys():
            tup = option_dct[option_key]
            if len(tup) == 2:
                tup[1]()
            elif len(tup) == 3:
                tup[1](tup[2])
            elif len(tup) == 4:
                tup[1](tup[2], tup[3])
        else:
            print('Please choose a menu option\n')

    # Shutdown
    robot.car.brake()
    robot.arm.poweroff()
    robot.cam.power_off()
    print("Goodbye!")


def line_following_mode(robot):
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
        turning_left = False
        turning_right = False
        while not movement['brake']:
            if interrupt_right(robot.irl.check(),
                               robot.irr.check()) and not turning_left:
                turning_left = True
                robot.car.point_turn(-1)
                time.sleep(2)
            elif interrupt_right(robot.irl.check(),
                                 robot.irr.check()) and turning_left:
                turning_left = False
                robot.car.swing_turn(1, 1)
            elif interrupt_left(robot.irl.check(),
                                robot.irr.check()) and not turning_right:
                turning_right = True
                robot.car.point_turn(1)
                time.sleep(2)
            elif interrupt_left(robot.irl.check(),
                                robot.irr.check()) and turning_right:
                turning_right = False
                robot.car.swing_turn(-1, 1)
            time.sleep(.1)  # delay to check sensors
            movement['brake'] = interrupt_both(robot.irl.check(),
                                               robot.irr.check())
        robot.car.brake()
    except:
        robot.car.brake()


if __name__ == "__main__":
    robot = carm.Carm(config.carm_config)

    robot.car.rm.logger.setLevel(logging.INFO)
    robot.car.lm.logger.setLevel(logging.INFO)
    robot.irr.logger.setLevel(logging.INFO)
    robot.irl.logger.setLevel(logging.INFO)

#    line_following_mode(robot)
    manual_mode(robot)

    cleanup()

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
