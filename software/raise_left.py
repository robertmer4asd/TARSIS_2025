import time
from Adafruit_PCA9685 import PCA9685

pwm = PCA9685(address=0x41, busnum=1)
pwm.set_pwm_freq(50)

servo_min = 150
servo_max = 600

def set_servo_angle(channel, angle):
    pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
    pwm.set_pwm(channel, 0, pulse_length)

def set_multiple_servos(servo_dict):
    for channel, angle in servo_dict.items():
        set_servo_angle(channel, angle)

servo_positions_raise = {
    2: 80,
    3: 30,
    4: 140,
    5: 50,
    6: 50
}

servo_positions_rest = {
    0: 25,
    1: 0,
    2: 100,
    3: 50,
    4: 120,
    5: 30,
    6: 20
}

try:
    set_multiple_servos(servo_positions_raise)
    time.sleep(3)
    set_multiple_servos(servo_positions_rest)


except KeyboardInterrupt:
    print("Servo control interrupted.")
    for channel in servo_positions.keys():
        set_servo_angle(channel, 90)
        pwm.set_pwm(channel, 0, 0)
