import time
import math
from Adafruit_PCA9685 import PCA9685
import RPi.GPIO as GPIO
import numpy as np

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
enable = 7
pwm = PCA9685(address=0x42, busnum=1)
pwm.set_pwm_freq(50)
GPIO.setup(enable, GPIO.OUT)
GPIO.output(enable, GPIO.LOW)

servo_min = 150
servo_max = 600
neutral_position = 90

def set_servo_angle(channel, angle):
    pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
    pwm.set_pwm(channel, 0, pulse_length)

def move_servos(angles):
    for channel, angle in angles.items():
        set_servo_angle(channel, angle)
        time.sleep(0.1)
    time.sleep(0.5)

def rotation_matrix_x(theta_x):
    theta_x = math.radians(theta_x)
    return np.array([[1, 0, 0],
                     [0, math.cos(theta_x), -math.sin(theta_x)],
                     [0, math.sin(theta_x), math.cos(theta_x)]])

def rotation_matrix_y(theta_y):
    theta_y = math.radians(theta_y)
    return np.array([[math.cos(theta_y), 0, math.sin(theta_y)],
                     [0, 1, 0],
                     [-math.sin(theta_y), 0, math.cos(theta_y)]])

def forward_kinematics(joint_angles, segment_lengths):
    P = np.array([0, 0, 0])
    
    for i in range(len(joint_angles)):
        theta_x = joint_angles[i][0]
        theta_y = joint_angles[i][1]
        L = segment_lengths[i]
        
        R_x = rotation_matrix_x(theta_x)
        R_y = rotation_matrix_y(theta_y)
        
        if i == 4:
            D = np.array([0, L, 0])
        else:
            D = np.array([L, 0, 0])
        
        P = P + R_y.dot(R_x).dot(D)
    
    return P

joint_angles = {
    0: [0, 30],
    1: [0, 10],
    2: [0, 40],
    3: [0, 100],
    4: [0, 100]
}

segment_lengths = [25, 90, 105, 120, 30]

final_position = forward_kinematics(joint_angles, segment_lengths)

final_position = np.round(final_position, 2)

print(f"Pozi?ia finala a capatului bra?ului: {final_position[0]:.2f}, {final_position[1]:.2f}")

try:
    angles = {
        3: 100,
        2: 30,
        1: 40,
        0: 100,
        4: 10
    }

    move_servos(angles)
    print("Servomotoarele au fost mutate la pozi?iile specificate.")

except KeyboardInterrupt:
    print("Mi?carea servomotoarelor a fost oprita.")
    neutral_angles = {channel: neutral_position for channel in angles.keys()}
    move_servos(neutral_angles)
