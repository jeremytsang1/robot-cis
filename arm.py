import config_log
import logging
import time
import servos


class Arm():
    """Class for arm of CARM."""
    def __init__(self, config):
        """Args: config (dict): Dict with configuration for each of the four
        servos that make up the arm.

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.gripper = servos.ServoMotor(config['gripper'])
        self.right = servos.ServoMotor(config['right'])
        # Disable base and left servos until finished with rest of arm.
        # self.left = servos.ServoMotor(config['left'])
        # self.base = servos.ServoMotor(config['base'])
        # self.servo_list = (self.gripper, self.left, self.right, self.base)
        self.servo_list = (self.gripper, self.right)

    def grab(self):
        """Moves the robotic arm forwards to grab (close an open gripper) an
        object and then rectracts the arm for a subsequent dropoff
        (open a closed gripper).

        """
        dropoff = self.right.config['min_pl']
        pickup = self.right.config['max_pl']
        speed = 0.00005
        try:
            self.gripper.sweep(300, speed)
            time.sleep(1)
            self.right.sweep(dropoff, speed)
            time.sleep(1)
            self.gripper.sweep(300, speed)
            time.sleep(1)
            self.right.sweep(pickup, speed)
            time.sleep(1)
            self.gripper.sweep(135, speed)
            time.sleep(1)
            self.right.sweep(dropoff, speed)
            time.sleep(1)
            self.gripper.sweep(300, speed)
            time.sleep(1)
        except KeyboardInterrupt:
            self.right.sweep(dropoff)

    def power_off(self):
        """Quick power way to run power_off for each of the 4 servos.
        """
        for servo in self.servo_list:
            servo.power_off()

    def open_gripper(self):
        self.gripper.sweep(self.gripper.config['max_pl'])

    def close_gripper(self):
        self.gripper.sweep(self.gripper.config['min_pl'])

    def extend(self, dist_pl):
        if (self.right.config['min_pl'] <= (self.right.current_pl + dist_pl) <=
            self.right.config['max_pl']):
            self.right.sweep(self.right.current_pl + dist_pl)


if __name__ == "__main__":
    print()
    # Example configuration for Arm Object
    config_gripper_servo = {
        'name': 'gripper',
        'channel': 12,
        'pow_pl': 300,
        'min_pl': 135,
        'max_pl': 300}
    config_right_servo = {  # use for forward and backward motion
        'name': 'right',
        'channel': 14,
        'pow_pl': 300,
        'min_pl': 300,  # provided l.current_pl = 450
        'max_pl': 550}
    # config_left_servo = {  # use for up and down motion
    #     'name': 'left',
    #     'channel': 13,
    #     'pow_pl': 450,
    #     'min_pl': 150,
    #     'max_pl': 450
    # }
    # config_base_servo = {
    #     'name': 'base',
    #     'channel': 15,
    #     'pow_pl': 400,
    #     'min_pl': None,
    #     'max_pl': None
    # }

    config_arm = {
        'gripper': config_gripper_servo,
        'right': config_right_servo,
        # 'left': config_left_servo,
        # 'base': config_base_servo,
        }

    arm = Arm(config_arm)

    # A few grabs to make sure everything is working
    for i in range(3):
        arm.grab()

    arm.power_off()
