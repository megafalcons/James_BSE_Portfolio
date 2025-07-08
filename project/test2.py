from picamera2 import Picamera2
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
import tensorflow as tf
from PIL import Image
import time
import os
import shutil
import requests
from pynput import keyboard

latest_key = None

def on_press(key):
    global latest_key
    try:
        latest_key = key.char  # Alphanumeric keys
    except AttributeError:
        latest_key = str(key)  # Special keys
    print(f"Key pressed: {latest_key}")

def on_release(key):
    global latest_key
    latest_key = None
    print("Key released")

# Start the listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# --- Load labels from file ---
def load_labels(label_path):
    with open(label_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

# --- Set the input tensor for the interpreter ---
def set_input_tensor(interpreter, image):
    input_details = interpreter.get_input_details()[0]
    interpreter.set_tensor(input_details['index'], image)

# --- Run inference and return top result ---
def classify_image(interpreter, image):
    set_input_tensor(interpreter, image)
    interpreter.invoke()

    output_details = interpreter.get_output_details()[0]
    output = interpreter.get_tensor(output_details['index'])[0]

    top_result = np.argmax(output)
    return top_result, output[top_result]

# --- Setup paths ---
LABEL_PATH = "pc1Stuff/labels.txt"
TFLITE_MODEL_PATH = "pc1Stuff/skibPC.tflite"

# --- Load model and allocate tensors ---

interpreter = Interpreter(TFLITE_MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
_, height, width, _ = input_details[0]['shape']

# --- Load labels ---
labels = load_labels(LABEL_PATH)

# --- Initialize Picamera2 ---
picam2 = Picamera2()
picam2.preview_configuration.main.size = (800, 800)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

active = True
confirm = 0
currentObj = -1
actualObj = -1
hasObj = False
time.sleep(4)
while True:
    if active:
        frame = picam2.capture_array()
        # frame2 = frame
        # Preprocess frame for model
        image = cv2.resize(frame, (width, height))
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image = image.astype(np.float32) / 255.0
        image = np.expand_dims(image, axis=0)


        label_id, prob = classify_image(interpreter, image)
        label_text = f"{labels[label_id]} ({prob:.2f})"

        # Display result on image
        if prob > 0.5:

            if currentObj == label_id:
                confirm += 1
                print(str(confirm))
                if confirm >= 67:
                    confirm = 0
                    active = False
                    hasObj = True
                    actualObj = currentObj
                    #currentObj = -1
                    print('wtf')
                    output_folder = 'temp/'
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)
                        print(f"Created folder: {output_folder}")
                    full_path = os.path.join(output_folder, 'temp.png')
                    cv2.imwrite(full_path, frame)
                    print(f"Image saved to: {full_path}")

            else:
                currentObj = label_id
                confirm = 0

            cv2.putText(frame, f"{label_text}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame, f"{confirm}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    elif hasObj:
        frame = cv2.imread('temp/temp.png')
        print(latest_key)

        if latest_key == '.' and currentObj < len(labels)-1:
            currentObj += 1
            time.sleep(0.2)
            print('this worked right')

        elif latest_key == ',' and currentObj >= 1:

            currentObj -= 1
            time.sleep(0.2)
            print('this worked left')


        elif latest_key == 'Key.enter' :
            hasObj = False
            output_folder = 'savedImages/' + labels[currentObj]
            full_file_path = os.path.join(output_folder, 'data.txt')
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                print(f"Created folder: {output_folder}")

                with open(full_file_path, "w") as file:
                    file.write("0")

            num = 0
            with open(full_file_path, "r") as file:
                content = file.read()
                try:
                    num = int(content.strip())
                except ValueError:
                    num = 0
            num += 1
            with open(full_file_path, "w") as file:
                file.write(str(num))
            output_filename = 'temp'+str(num)+'.png'
            full_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(full_path, frame)
            print(f"Image saved to: {full_path}")

            num = 0
            path_to_count = 'savedImages/count.txt'
            with open(path_to_count, "r") as file:
                content = file.read()
                try:
                    num = int(content.strip())
                except ValueError:
                    num = 0
            num += 1
            if num == 200:
                folder_to_zip = 'savedImages'  # e.g., "./data"
                zip_filename = 'savedImages.zip'

                shutil.make_archive(base_name='savedImages', format='zip', root_dir=folder_to_zip)

                url = 'http://172.16.6.137:3000/upload-folder'

                with open(zip_filename, 'rb') as f:
                    files = {'folderZip': f}
                    response = requests.post(url, files=files)

                print("Status:", response.status_code)
                print("Response:", response.text)
                num = 0

                url = 'http://172.16.6.137:3000/get-folder'
                response = requests.get(url)
                with open("pc1Stuff/skibPC.tflite", "wb") as f:
                    f.write(response.content)

                interpreter = Interpreter(TFLITE_MODEL_PATH)
                interpreter.allocate_tensors()
                input_details = interpreter.get_input_details()
                _, height, width, _ = input_details[0]['shape']
            with open(path_to_count, "w") as file:
                file.write(str(num))


        cv2.putText(frame, f"{labels[currentObj]}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)


    else:
        frame = cv2.imread('skibidi.png')
        if latest_key == 'Key.space':
            active = True






    cv2.imshow("Picamera2 - TFLite Classification", frame)


    if cv2.waitKey(25) & 0xFF == ord('q'):
        cheese = 1
        cv2.destroyAllWindows()
        picam2.stop()
        break