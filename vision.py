import servos


class Cam(servos.ServoMotor):
    def __init__(self, config):
        servos.ServoMotor.__init__(self, config)
        
    def lookup(self):
        self.sweep(self.config['min_pl'])

    def lookdown(self):
        self.sweep(self.config['max_pl'])


if __name__ == "__main__":
    config_camera_servo = {
        'name': 'right',
        'channel': 15,
        'pow_pl': 400,
        'min_pl': 325,
        'max_pl': 475}

    cam = Cam(config_camera_servo)

