import servos
from config import config_camera_servo


class Cam(servos.ServoMotor):
    def __init__(self, config):
        servos.ServoMotor.__init__(self, config)
        
    def lookup(self):
        self.sweep(self.config['min_pl'])

    def lookdown(self):
        self.sweep(self.config['max_pl'])


if __name__ == "__main__":

    cam = Cam(config_camera_servo)

