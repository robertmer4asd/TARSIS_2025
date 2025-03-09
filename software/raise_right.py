import time
from Adafruit_PCA9685 import PCA9685
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pwm = PCA9685(address=0x42, busnum=1)
pwm.set_pwm_freq(50)
servo_min = 150
servo_max = 600

def set_servo_angle(channel, angle):
    pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
    pwm.set_pwm(channel, 0, pulse_length)

def move_servos(angles):
    for channel, angle in angles.items():
        set_servo_angle(channel, angle)
        time.sleep(0.1)
try:
    angles = {
        3: 50,
        2: 10,
        1: 20,
        0: 100,
        4: 10
        }

    move_servos(angles)

    print("Servos moved to the specified positions.")
except KeyboardInterrupt:
    print("Servo movement stopped.")
    neutral_angles = {channel: neutral_position for channel in angles.keys()}
    move_servos(neutral_angles)
