import threading
import numpy as np
import cv2
import time
from Adafruit_PCA9685 import PCA9685
import socket
import subprocess
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from googletrans import Translator


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
whatDoYouSee = False


detected_objects = []
prototxt_path = 'deploy.prototxt'
model_path = 'MobileNetSSD_deploy.caffemodel'
min_confidence = 0.2
classes = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle',
    'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog',
    'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa',
    'train', 'tvmonitor'
]
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

translator = Translator()

np.random.seed(34732)
colors = np.random.uniform(0, 255, size=(len(classes), 3))
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_lock = threading.Lock()
frame = None

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
set_servo_angle(servo_y_channel, 0)
set_servo_angle(servo_x_channel, 25)
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            with frame_lock:
                frame = new_frame

frame_thread = threading.Thread(target=capture_frames, daemon=True)
frame_thread.start()

def process_frame():
    global detected_objects, whatDoYouSee

    while True:
        with frame_lock:
            if frame is None:
                continue
            local_frame = frame.copy()

        height, width = local_frame.shape[:2]
        gray = cv2.cvtColor(local_frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        blob = cv2.dnn.blobFromImage(cv2.resize(local_frame, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        detected_objects.clear()
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            class_index = int(detections[0, 0, i, 1])
            class_name = classes[class_index]

            if confidence > min_confidence:
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (startX, startY, endX, endY) = box.astype("int")
                detected_objects.append({"class": class_name, "coordinates": (startX, startY, endX, endY)})

                color = colors[class_index]
                cv2.rectangle(local_frame, (startX, startY), (endX, endY), color, 2)
                cv2.putText(local_frame, f"{class_name}: {confidence:.2f}", (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        for (x, y, w, h) in faces:
            cv2.rectangle(local_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            detected_objects.append({"class": "face", "coordinates": (x, y, x + w, y + h)})

        if whatDoYouSee:
            description = generate_scene_description(detected_objects)
            send_data(description)
            whatDoYouSee = False  

        cv2.namedWindow("Detected Objects", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Detected Objects", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Detected Objects", local_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
process_thread = threading.Thread(target=process_frame, daemon=True)
process_thread.start()

def send_data(data, host='192.168.100.23', port=53030):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode())
            print("Data sent:", data)
    except Exception as e:
        print(f"Error sending data: {e}")

def receive_data():
    global hand, whatDoYouSee
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
    elif data == "photo" and hand:
        image_path = "captured_image.jpg"
        capture_image(image_path)
        print("Se analizeaza imaginea...")
        description = describe_image(image_path)
        translated_description = translate_text(description, "ro")
        print(translated_description)
        send_data(translated_description)
    descriptions = []
    for obj in detected_objects:
        descriptions.append(f"A {obj['class']} is in the frame.")
    return " ".join(descriptions)

def capture_image(image_path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Eroare: Nu se poate accesa camera.")
        return
    
    ret, frame = cap.read()
    if ret:
        frame_resized = cv2.resize(frame, (640, 480))  # Redimensionează imaginea
        cv2.imwrite(image_path, frame_resized)
        print(f"Imagine salvată: {image_path}")
    else:
        print("Eroare la capturarea imaginii.")
    
    cap.release()

def describe_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((640, 480))  # Redimensionează imaginea la o dimensiune mai mică
    inputs = processor(image, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model.generate(**inputs)
    
    description = processor.decode(output[0], skip_special_tokens=True)
    return description

def translate_text(text, target_language="ro"):
    translated = translator.translate(text, dest=target_language)
    return translated.text


def cleanup():
    cap.release()
    cv2.destroyAllWindows()

import atexit
atexit.register(cleanup)

def main_loop():
    global current_x_angle, current_y_angle, locked_x_angle, locked_y_angle
    
    try:
        while True:

            if hand:
                print("Handshake mode active.")  
            
            if whatDoYouSee:
                print("Processing 'whatDoYouSee' request...")  
            
            if locked_x_angle is not None:
                current_x_angle = locked_x_angle
            if locked_y_angle is not None:
                current_y_angle = locked_y_angle            

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")
        cleanup()

if __name__ == "__main__":
    main_loop()
