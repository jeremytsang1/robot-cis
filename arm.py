import config_log
import logging
import time
import servos


class Arm():
    """Class for arm of CARM."""
    def __init__(self, cals):
        """Args: cals (dict): Dict with configuration for each of the four
        servos that make up the arm.

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.gripper = servos.ServoMotor(cals['gripper'])
        self.left = servos.ServoMotor(cals['left'])
        self.right = servos.ServoMotor(cals['right'])
        # Disable base until finished with rest of arm.
        # self.base = servos.ServoMotor(cals['base'])
        # self.servo_list = (self.gripper, self.left, self.right, self.base)
        self.servo_list = (self.gripper, self.left, self.right)

    def grab(self):
        """Moves the robotic arm forwards to grab (close an open gripper) an
        object and then rectracts the arm for a subsequent dropoff
        (open a closed gripper).

        """
        dropoff = self.right.cals['min_pl']
        pickup = self.right.cals['max_pl']
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

    def poweroff(self):
        """Quick power way to run power_off for each of the 4 servos.
        """
        for servo in self.servo_list:
            servo.power_off()


if __name__ == "__main__":
    print()
    cals = {
        'gripper': {
            "name": "gripper",
            "channel": 12,
            "pow_pl": 300,
            "min_pl": 135,
            "max_pl": 300},
        # Left and right servo are in opposition to each other. Until work
        # out details keep left servo at 450 at all times.
        'left': {  # use for up and down motion
            "name": "left",
            "channel": 13,
            "pow_pl": 450,
            "min_pl": 150,
            "max_pl": 450},
        'right': {  # use for forward and backward motion
            "name": "right",
            "channel": 14,
            "pow_pl": 275,
            "min_pl": 275,  # provided l.current_pl = 450
            "max_pl": 550}
        # 'base': {
        #     "name": "base",
        #     "channel": 15,
        #     "pow_pl": 400,
        #     "min_pl": None,
        #     "max_pl": None},
    }
    arm = Arm(cals)

    # A few grabs to make sure everything is working
    for i in range(3):
        arm.grab()

    arm.poweroff()
