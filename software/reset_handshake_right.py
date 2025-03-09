import time
from Adafruit_PCA9685 import PCA9685

pwm = PCA9685(address=0x42, busnum=1)
pwm.set_pwm_freq(50)

servo_min = 150
servo_max = 600
neutral_position = 90
step_delay = 0.01
step_size = 1

def set_servo_angle(channel, angle):
    pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
    pwm.set_pwm(channel, 0, pulse_length)

def move_servo_smoothly(channel, start_angle, end_angle, step_size, step_delay):
    step = step_size if start_angle < end_angle else -step_size
    for angle in range(start_angle, end_angle + step, step):
        set_servo_angle(channel, angle)
        time.sleep(step_delay)

def move_servos(angles):
    current_angles = {channel: neutral_position for channel in angles.keys()}
    for channel, end_angle in angles.items():
        if channel == 3:
            start_angle = current_angles[channel]
            move_servo_smoothly(channel, start_angle, end_angle, step_size, step_delay)
            current_angles[channel] = end_angle
        else:
            set_servo_angle(channel, end_angle)
            time.sleep(0.1)
    time.sleep(0.5)

try:
    angles = {
        3: 1,
        2: 10,
        4: 10,
        1: 80,
        0: 100,
        5: 10,
        6: 40,
        7: 40,
        8: 40,
        9: 40
    }
    move_servos(angles)
    print("Servos moved to the specified positions.")
except KeyboardInterrupt:
    print("Servo movement stopped.")
    neutral_angles = {channel: neutral_position for channel in angles.keys()}
    move_servos(neutral_angles)
