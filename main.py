import carm
import config
import RPi.GPIO as GPIO


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
    option = str()
    menu_str = '\n'.join((
        '',
        '    w: forward',
        '    s: backwards',
        '    a: point left',
        '    d: point left',
        '    q: swing left FWD',
        '    e: swing right FWD',
        '    q: swing left BACK',
        '    e: swing right BACK',
        'space: brake',
        '    g: grab',
        '    o: opens',
        '    n: full extend',
        '    p: full retract',
        '    [: increment extend',
        '    ]: increment retract',        
        '    1: look down',
        '    2: look straight',
        '    3: look up',
        '    j: quit',
        '\n> '))

    while option != 'j':
        option = input(menu_str)
        if option == 'w':
            robot.car.drive(1)
        elif option == 's':
            robot.car.drive(-1)
        elif option == 'a':
            robot.car.point_turn(-1)
        elif option == 'd':
            robot.car.point_turn(1)
        elif option == 'q':
            robot.car.swing_turn(-1, 1)
        elif option == 'e':
            robot.car.swing_turn(1, 1)
        elif option == 'z':
            robot.car.swing_turn(-1, -1)
        elif option == 'c':
            robot.car.swing_turn(1, -1)
        elif option == ' ':
            robot.car.brake()
        elif option == 'g':
            robot.arm.gripper.sweep(135)
        elif option == 'o':
            robot.arm.gripper.sweep(300)
        elif option == 'n':
            robot.arm.right.sweep(550)
        elif option == 'p':
            robot.arm.right.sweep(300)
        elif option == '[':
            if robot.arm.right.current_pl < 500:
                robot.arm.right.sweep(robot.arm.right.current_pl - 5)
        elif option == ']':
            if robot.arm.right.current_pl < 500:
                robot.arm.right.sweep(robot.arm.right.current_pl + 5)
        elif option == '1':
            robot.cam.lookdown()
        elif option == '2':
            robot.cam.power_off()
        elif option == '3':
            robot.cam.lookup()
        elif option == 'j':
            robot.car.brake()
            robot.arm.poweroff()
            robot.cam.power_off()
            print("Goodbye!")
        else:
            print('Please choose a menu option\n')


if __name__ == "__main__":
    robot = carm.Carm(config.carm_config)

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
