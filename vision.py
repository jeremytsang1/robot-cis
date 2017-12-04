import servos
from config import config_camera_servo


class Cam(servos.ServoMotor):
    def __init__(self, config):
        servos.ServoMotor.__init__(self, config)
        self.min = self.config['min_pl']
        self.max = self.config['max_pl']
        
    def lookup(self):
        self.sweep(self.config['min_pl'])

    def lookdown(self):
        self.sweep(self.config['max_pl'])

    def tilt(self, dist_pl):
        """Safe tilting. Camera servo tilts up or down but only if the sum of
        dist_pl and the current pulse level doesn't go beyond min/max
        pulse levels set in config.

        Args:
        dist_pl (int): positive or negative integer

        Returns:
        None

        """
        if (self.config['min_pl'] <= (self.current_pl + dist_pl) <=
            self.config['max_pl']):
            self.sweep(self.current_pl + dist_pl)

if __name__ == "__main__":

    cam = Cam(config_camera_servo)

