config_left_dc_motor = {
    'name': 'left',
    'pin_forward': 6,
    'pin_backward': 5
}
config_right_dc_motor = {
    'name': 'right',
    'pin_forward': 16,
    'pin_backward': 12
}

config_car = {
    'left_motor': config_left_dc_motor,
    'right_motor': config_right_dc_motor
}

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
# Disable left and base servos till finish the rest of the Carm.
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

carm_config = {
    'car': config_car,
    'arm': config_arm
    }


