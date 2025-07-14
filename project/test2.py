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
import sqlite3
import tkinter as tk
root = tk.Tk()
root.geometry("300x200")
name_var=tk.StringVar()
price_var=tk.StringVar()
start = 1
submitted = 0
sub_name = ""
sub_price = ""
def submit():
    global submitted
    global sub_name
    global sub_price
    sub_name = str(name_var.get())
    sub_price = str(price_var.get())
    print(sub_name)
    print(sub_price)
    submitted = 100
    name_var.set("")
    price_var.set("")

name_label = tk.Label(root, text = 'Item Name', font=('calibre',10, 'bold'))

# creating a entry for input
# name using widget Entry
name_entry = tk.Entry(root,textvariable = name_var, font=('calibre',10,'normal'))

# creating a label for password
passw_label = tk.Label(root, text = 'Price', font = ('calibre',10,'bold'))

# creating a entry for password
passw_entry=tk.Entry(root, textvariable = price_var, font = ('calibre',10,'normal'))

# creating a button using the widget
# Button that will call the submit function
sub_btn=tk.Button(root,text = 'Submit', command = submit)

# placing the label and entry in
# the required position using grid
# method
name_label.grid(row=0,column=0)
name_entry.grid(row=0,column=1)
passw_label.grid(row=1,column=0)
passw_entry.grid(row=1,column=1)
sub_btn.grid(row=2,column=1)

# connecting to the database
connection = sqlite3.connect("inventory.db")

# cursor
crsr = connection.cursor()
'''
sql_command = """CREATE TABLE inv (
id_number INTEGER,
category VARCHAR(20),
product_name VARCHAR(255),
status CHAR(1),
price_paid INTEGER,
price_sold INTEGER
);"""

crsr.execute(sql_command)
'''
# close the connection
# connection.close()
latest_key = ""
ischar = False
def on_press(key):
    global latest_key
    global ischar
    ischar = True
    try:
        latest_key = key.char # Alphanumeric keys

    except AttributeError:
        latest_key = str(key)  # Special keys
        ischar = False
    print(f"Key pressed: {latest_key}")

def on_release(key):
    global latest_key
    latest_key = ""
    ischar = False
    print("Key released")

# Start the listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def capture(state, userdata):
    global confirm
    confirm = 67

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
name = ""
#cv2.namedWindow("Picamera2 - TFLite Classification")

def main():
    global submitted
    global active
    global confirm
    global currentObj
    global actualObj
    global hasObj
    global width
    global height
    global interpreter
    global crsr
    global sub_name
    global sub_price

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
        #print(latest_key)

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
        '''
        print(name)
        cv2.putText(frame, f"{name}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        if ischar:
            print(latest_key + "bruh")
            print(ischar)
            name += latest_key

        if latest_key == 'Key.backspace':
            name = name[:-1]
        '''
        #print(str(submitted) + "submitted value")
        #print(sub_name)
        #print (sub_price)
        if submitted == 100:
            print("hello world")
            sql_command = """INSERT INTO inv
            VALUES ( 1, '""" + labels[currentObj] + """','""" + sub_name + """', 'a',""" + sub_price + """,""" + """-1);"""

            print(sql_command)
            crsr.execute(sql_command)
            connection.commit()

            sql_command = """SELECT * FROM inv;"""
            crsr.execute(sql_command)
            ans = crsr.fetchall()
            print("y is this so annoying")
            for i in ans:
                print(i)
                print ("this is the db")
            submitted = 0
        if latest_key == 'Key.enter':
            active = True







    #cv2.createButton("Click Me", capture, None, cv2.QT_PUSH_BUTTON, 1)
    cv2.imshow("Picamera2 - TFLite Classification", frame)



    if cv2.waitKey(25) & 0xFF == ord('q'):
        cheese = 1
        cv2.destroyAllWindows()
        picam2.stop()
        connection.close()

    else:
        root.after(1, main)

root.after(1000, main)
root.mainloop()
connection.close()