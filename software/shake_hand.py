import time
import math
from Adafruit_PCA9685 import PCA9685
import RPi.GPIO as GPIO
import subprocess
import numpy as np

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
enable = 7
GPIO.setup(enable, GPIO.OUT)
GPIO.output(enable, GPIO.LOW)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = PCA9685(address=0x42, busnum=1)
pwm.set_pwm_freq(50)

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
    P = np.array([0, 0, 0])  # 3D position (X, Y, Z)
    
    for i in range(len(joint_angles)):
        theta_x = joint_angles[i][0]
        theta_y = joint_angles[i][1]
        L = segment_lengths[i]
        
        R_x = rotation_matrix_x(theta_x)
        R_y = rotation_matrix_y(theta_y)
        
        # Apply the rotations and translation
        if i == 4:
            D = np.array([0, L, 0])  # translation along X-axis for each segment
        else:
            D = np.array([L, 0, 0])
        
        # Apply the rotation matrix (rotation first, then translation)
        P = P + R_y.dot(R_x).dot(D)
    
    return P

joint_angles = {
    0: [0, 80],
    1: [0, 40],
    2: [0, 80],
    3: [0, 50],
    4: [0, 100]
}

segment_lengths = [25, 90, 105, 120, 30]

final_position = forward_kinematics(joint_angles, segment_lengths)

final_position = np.round(final_position, 2)

print(f"Pozi?ia finala a capatului bra?ului: {final_position[0]:.2f}, {final_position[1]:.2f}, {final_position[2]:.2f}")

try:
    initial_angles = {
        3: 20,
        2: 80,
        1: 80,
        0: 150,
        5: 10,
        6: 40,
        7: 40,
        8: 40,
        9: 40
    }

    move_servos(initial_angles)
    print("Servos moved to initial positions.")

    specific_angles = {
        5: 70,
        8: 120,
        7: 120,
        6: 110,
        9: 120
    }

    print("Waiting for pin 17 to go high...")
    while GPIO.input(17) == GPIO.LOW:
        time.sleep(0.1)

    print("Pin 17 is high. Moving specific servos.")
    move_servos(specific_angles)
    print("Specific servos moved to the specified positions.")

    while True:
        if GPIO.input(17) == GPIO.HIGH:
            move_servos(specific_angles)
        else:
            print("Pin 17 is low. Running reset_handshake_right.py script.")
            subprocess.call(['python', 'reset_handshake_right.py'])
            break
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Servo movement stopped.")
    neutral_angles = {channel: neutral_position for channel in initial_angles.keys()}
    move_servos(neutral_angles)
finally:
    GPIO.cleanup()
