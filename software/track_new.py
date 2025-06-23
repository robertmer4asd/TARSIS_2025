import threading
import cv2
import time
from Adafruit_PCA9685 import PCA9685
import socket
import subprocess
import atexit
import argparse
import os

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.edgetpu import run_inference

try:
    pwm = PCA9685(address=0x41, busnum=1)
    pwm.set_pwm_freq(50)
except Exception as e:
    print(f"Error initializing PCA9685: {e}")

servo_x_channel = 0
servo_y_channel = 1
servo_min = 150
servo_max = 600
current_x_angle = 375
current_y_angle = 375
locked_x_angle = None
locked_y_angle = None
hand = False

def set_servo_angle(channel, angle):
    pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
    pwm.set_pwm(channel, 0, pulse_length)

set_servo_angle(servo_y_channel, 0)
set_servo_angle(servo_x_channel, 25)

def send_data(data, host='192.168.100.23', port=53030):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode())
            print("Data sent:", data)
    except Exception as e:
        print(f"Error sending data: {e}")

def receive_data():
    global hand
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 53030))
            s.listen(5)
            print("Listening on port 53030...")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        handle_received_data(data.decode())
    except Exception as e:
        print(f"Error in receive_data: {e}")

listener_thread = threading.Thread(target=receive_data, daemon=True)
listener_thread.start()

def handle_received_data(data):
    global hand
    print(f"Handling received message: {data}")
    if data and not hand:
        subprocess.call(['python', 'salut_mana.py'])
        subprocess.call(['python', 'reset_handshake_right.py'])
        subprocess.call(['python', 'rest_left.py'])
        hand = True
    elif data == "shake hand" and hand:
        subprocess.call(['python', 'shake_hand.py'])
    elif data == "stanga" and hand:
        subprocess.call(['python', 'raise_left.py'])
    elif data == "explain" and hand:
        subprocess.call(['python', 'run_emote.py'])
    elif data == "dreapta" and hand:
        subprocess.call(['python', 'raise_right.py'])
        time.sleep(3)
        subprocess.call(['python', 'reset_handshake_right.py'])

def set_servo_angle(channel, angle):
    global current_x_angle, current_y_angle, locked_x_angle, locked_y_angle
    if channel == servo_x_channel and angle != current_x_angle:
        try:
            pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
            pwm.set_pwm(channel, 0, pulse_length)
            current_x_angle = angle
            print(f"Servo X angle set to: {angle}")
        except Exception as e:
            print(f"Error setting X servo angle: {e}")
    elif channel == servo_y_channel and angle != current_y_angle:
        try:
            pulse_length = int((angle / 180.0) * (servo_max - servo_min) + servo_min)
            pwm.set_pwm(channel, 0, pulse_length)
            current_y_angle = angle
            locked_y_angle = angle
            print(f"Servo Y angle set to: {angle}")
        except Exception as e:
            print(f"Error setting Y servo angle: {e}")
def coral_detect():
    default_model_dir = '../all_models'
    default_model = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
    default_labels = 'coco_labels.txt'

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default=os.path.join(default_model_dir, default_model))
    parser.add_argument('--labels', default=os.path.join(default_model_dir, default_labels))
    parser.add_argument('--top_k', type=int, default=3)
    parser.add_argument('--camera_idx', type=int, default=0)
    parser.add_argument('--threshold', type=float, default=0.1)
    args = parser.parse_args([])

    print(f'Loading model: {args.model} with labels: {args.labels}')
    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()
    labels = read_label_file(args.labels)
    inference_size = input_size(interpreter)

    cap = cv2.VideoCapture(args.camera_idx)
    cv2.namedWindow('Object Detection', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Object Detection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2_im_rgb = cv2.resize(cv2_im_rgb, inference_size)
        run_inference(interpreter, cv2_im_rgb.tobytes())
        objs = get_objects(interpreter, args.threshold)[:args.top_k]
        frame = append_objs_to_img(frame, inference_size, objs, labels)

        cv2.imshow('Object Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, _ = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]
    for obj in objs:
        bbox = obj.bbox.scale(scale_x, scale_y)
        x0, y0, x1, y1 = int(bbox.xmin), int(bbox.ymin), int(bbox.xmax), int(bbox.ymax)
        label = f"{int(100 * obj.score)}% {labels.get(obj.id, obj.id)}"
        cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(cv2_im, label, (x0, y0 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
    return cv2_im

def main_loop():
    try:
        print("Starting Coral object detection...")
        coral_detect()
    except KeyboardInterrupt:
        print("Exiting...")
        cleanup()

if __name__ == "__main__":
    main_loop()
