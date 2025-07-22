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
from tkinter import ttk
root = tk.Tk()
root.geometry("600x400")
name_var=tk.StringVar()
price_var=tk.StringVar()
start = 1
submitted = 0
buildCost = 0
priceSold = tk.StringVar()
# connecting to the database
connection = sqlite3.connect("inventory.db")

# cursor
crsr = connection.cursor()
'''
sql_command = """CREATE TABLE sales(
build_id INTEGER,
price_paid INTEGER,
price_sold INTEGER)"""
crsr.execute(sql_command)

connection.close()
'''
ans1 = []
ans2 = []
ans3 = []
ans4 = []
ans5 = []
ans6 = []
ans7 = []
ans8 = []
builds = []
sub_name = ""
sub_price = ""
def updateChoices():
    global option1
    global option2
    global option3
    global option4
    global option5
    global option6
    global option7
    global option8
    global buildsList
    global ans1
    global ans2
    global ans3
    global ans4
    global ans5
    global ans6
    global ans7
    global ans8
    global builds
    buildsList['values'] = builds
    option1['values'] = [item[0] for item in ans1]
    option2['values'] = [item[0] for item in ans2]
    option3['values'] = [item[0] for item in ans3]
    option4['values'] = [item[0] for item in ans4]
    option5['values'] = [item[0] for item in ans5]
    option6['values'] = [item[0] for item in ans6]
    option7['values'] = [item[0] for item in ans7]
    option8['values'] = [item[0] for item in ans8]



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
def setBuild(name, buildNum):
    global crsr
    global connection
    if name != "":
        sql_command = """SELECT category FROM inv WHERE product_name = '""" + name + """'"""
        crsr.execute(sql_command)
        cat = crsr.fetchall()[0][0]
        sql_command = """UPDATE inv SET build_id = -1 WHERE category = '""" + cat + """' AND build_id = """ + str(buildNum)
        sql_command = """SELECT item_id FROM inv WHERE product_name = '""" + name + """'"""
        crsr.execute(sql_command)
        dupes = crsr.fetchall()
        current = -1
        for x in dupes:
            sql_command = """SELECT build_id FROM inv WHERE item_id =""" + str(x[0])
            crsr.execute(sql_command)
            temp = crsr.fetchall()
            print(str(temp) + "temp")
            if temp[0][0] == -1:
                current = x[0]
                break

        sql_command = """UPDATE inv SET build_id =""" + str(buildNum) + """ WHERE item_id =""" + str(current)
        print(sql_command)
        crsr.execute(sql_command)
        sql_command = """SELECT price_paid FROM inv WHERE item_id =""" +str(current)
        crsr.execute(sql_command)
        temp2= crsr.fetchall()
        global buildCost
        buildCost += temp2[0][0]
        #connection.commit()
def getBuild():
    global crsr
    try:
        buildNum = int(buildsList.get())
    except ValueError:
        return
    sql_command = """SELECT category, product_name, price_paid FROM inv WHERE build_id = """ + str(buildNum) +""" ORDER BY CAST(category AS INTEGER);"""
    crsr.execute(sql_command)
    items = crsr.fetchall()
    print("type name price")
    print(str(items))
    for x in items:
        for y in x:
            print(str(y), end = " ")

        print()
    sql_command = """SELECT price_paid, price_sold FROM sales WHERE build_id = """ + str(buildNum)
    crsr.execute(sql_command)
    prices = crsr.fetchall()
    print(prices)
    print ("price paid: " + str(prices[0][0]))
    print("price sold: " + str(prices[0][1]))
def getInv():
    global crsr
    try:
        buildNum = -1
    except ValueError:
        return
    sql_command = """SELECT category, product_name, price_paid FROM inv WHERE build_id = """ + str(buildNum) +""" ORDER BY CAST(category AS INTEGER);"""
    crsr.execute(sql_command)
    items = crsr.fetchall()
    print("type name price")
    print(str(items))
    for x in items:
        for y in x:
            print(str(y), end = " ")

        print()
def addBuild():
    global crsr
    global buildCost
    buildCost = 0
    try:
        buildNum = int(buildsList.get())
    except ValueError:
        return


    setBuild(option1.get(), buildNum)
    setBuild(option2.get(), buildNum)
    setBuild(option3.get(), buildNum)
    setBuild(option4.get(), buildNum)
    setBuild(option5.get(), buildNum)
    setBuild(option6.get(), buildNum)
    setBuild(option7.get(), buildNum)
    setBuild(option8.get(), buildNum)
    option1.set("")
    option2.set("")
    option3.set("")
    option4.set("")
    option5.set("")
    option6.set("")
    option7.set("")
    option8.set("")
    sql_command = """UPDATE sales
    SET price_paid=""" + str(buildCost) + """ WHERE build_id =""" + str (buildNum)
    crsr.execute(sql_command)
    print(sql_command)
    connection.commit()

def newBuild():
    global crsr
    global buildCost
    buildCost = 0
    buildNum = 0
    with open("bId.txt", "r") as file:
        content = file.read()
        try:
            buildNum = int(content.strip())
        except ValueError:
            buildNum = 0
    buildNum += 1
    with open("bId.txt", "w") as file:
        file.write(str(buildNum))

    setBuild(option1.get(), buildNum)
    setBuild(option2.get(), buildNum)
    setBuild(option3.get(), buildNum)
    setBuild(option4.get(), buildNum)
    setBuild(option5.get(), buildNum)
    setBuild(option6.get(), buildNum)
    setBuild(option7.get(), buildNum)
    setBuild(option8.get(), buildNum)
    option1.set("")
    option2.set("")
    option3.set("")
    option4.set("")
    option5.set("")
    option6.set("")
    option7.set("")
    option8.set("")
    sql_command = """INSERT INTO sales
    VALUES(""" + str(buildNum) + """,""" + str (buildCost) + """, -1)"""
    crsr.execute(sql_command)
    print(sql_command)
    connection.commit()

def sellBuild():
    global priceSold
    try:
        buildNum = int(buildsList.get())
    except ValueError:
        return
    try:
        price = int(priceSold.get())
    except ValueError:
        return

    sql_command = """UPDATE sales SET price_sold =""" + str(price) + """ WHERE build_id =""" + str(buildNum)
    crsr.execute(sql_command)

def updateInv():
    global ans1
    global ans2
    global ans3
    global ans4
    global ans5
    global ans6
    global ans7
    global ans8
    global builds

    buildNum = 0
    with open("bId.txt", "r") as file:
        content = file.read()
        try:
            buildNum = int(content.strip())
        except ValueError:
            buildNum = 0

    if buildNum != 0:
        builds = [0] * (buildNum)
        n = 1
        for x in builds:
            builds[n-1] = n
            n+=1

    else:
        builds = []

    sql_command = """SELECT product_name FROM inv WHERE category= '0 gpu' AND build_id = -1"""
    crsr.execute(sql_command)
    ans1 = crsr.fetchall()

    sql_command = """SELECT product_name FROM inv WHERE category= '1 cpu' AND build_id = -1"""
    crsr.execute(sql_command)
    ans2 = crsr.fetchall()
    sql_command = """SELECT product_name FROM inv WHERE category= '2 ram' AND build_id = -1"""
    crsr.execute(sql_command)
    ans3 = crsr.fetchall()
    sql_command = """SELECT product_name FROM inv WHERE category= '3 motherboard' AND build_id = -1"""
    crsr.execute(sql_command)
    ans4 = crsr.fetchall()
    sql_command = """SELECT product_name FROM inv WHERE category= '4 case' AND build_id = -1"""
    crsr.execute(sql_command)
    ans5 = crsr.fetchall()
    sql_command = """SELECT product_name FROM inv WHERE category= '5 psu' AND build_id = -1"""
    crsr.execute(sql_command)
    ans6 = crsr.fetchall()
    sql_command = """SELECT product_name FROM inv WHERE (category= '6 aio' OR category = '7 air cooler') AND build_id = -1"""
    crsr.execute(sql_command)
    ans7 = crsr.fetchall()
    sql_command = """SELECT product_name FROM inv WHERE (category= '8 ssd (sata)' OR category = '9 ssd (nvme)') AND build_id = -1"""
    crsr.execute(sql_command)
    ans8 = crsr.fetchall()


'''sql_command = """CREATE TABLE inv (
item_id INTEGER,
build_id INTEGER,
count INTEGER,
category VARCHAR(20),
product_name VARCHAR(255),
status CHAR(1),
price_paid INTEGER,
price_sold INTEGER
);"""
'''
'''sql_command = """CREATE TABLE sales(
build_id INTEGER,
price_paid INTEGER,
price_sold INTEGER"""
crsr.execute(sql_command)

connection.close()'''

name_label = tk.Label(root, text = 'Item Name', font=('calibre',10, 'bold'))

# creating a entry for input
# name using widget Entry
name_entry = tk.Entry(root,textvariable = name_var, font=('calibre',10,'normal'))

# creating a label for password
passw_label = tk.Label(root, text = 'Price', font = ('calibre',10,'bold'))

# creating a entry for password
passw_entry=tk.Entry(root, textvariable = price_var, font = ('calibre',10,'normal'))

price_sold = tk.Label(root, text = 'price sold', font=('calibre',10, 'bold'))

# creating a entry for input
# name using widget Entry
enter_price = tk.Entry(root,textvariable = priceSold, font=('calibre',10,'normal'))
# creating a button using the widget
# Button that will call the submit function
sub_btn=tk.Button(root,text = 'Submit', command = submit)

sellBuild = tk.Button(root, text = 'mark as sold', command = sellBuild)
inv_button = tk.Button(root, text = 'new build', command = newBuild)
addToBuild = tk.Button(root, text = 'add to build', command = addBuild)
getBuild = tk.Button(root, text = 'see build', command = getBuild)
updateInv()
buildsList = ttk.Combobox(root, postcommand = updateChoices)
name_label1 = tk.Label(root, text = 'gpu', font=('calibre',10, 'bold'))
option1 = ttk.Combobox(root, postcommand=updateChoices)
name_label2 = tk.Label(root, text = 'cpu', font=('calibre',10, 'bold'))
option2 = ttk.Combobox(root, postcommand=updateChoices)
name_label3 = tk.Label(root, text = 'ram', font=('calibre',10, 'bold'))
option3 = ttk.Combobox(root, postcommand=updateChoices)
name_label4 = tk.Label(root, text = 'motherboard', font=('calibre',10, 'bold'))
option4 = ttk.Combobox(root, postcommand=updateChoices)
name_label5 = tk.Label(root, text = 'case', font=('calibre',10, 'bold'))
option5 = ttk.Combobox(root, postcommand=updateChoices)
name_label6 = tk.Label(root, text = 'psu', font=('calibre',10, 'bold'))
option6 = ttk.Combobox(root, postcommand=updateChoices)
name_label7 = tk.Label(root, text = 'cooler', font=('calibre',10, 'bold'))
option7 = ttk.Combobox(root, postcommand=updateChoices)
name_label8 = tk.Label(root, text = 'ssd', font=('calibre',10, 'bold'))
option8 = ttk.Combobox(root, postcommand=updateChoices)
updateChoices()


# placing the label and entry in
# the required position using grid
# method
name_label.grid(row=0,column=0)
name_entry.grid(row=0,column=1)
passw_label.grid(row=1,column=0)
passw_entry.grid(row=1,column=1)
sub_btn.grid(row=2,column=1)

name_label1.grid(row=4, column = 0)
option1.grid(row = 4, column = 1)
name_label2.grid(row=5, column = 0)
option2.grid(row = 5, column = 1)
name_label3.grid(row=6, column = 0)
option3.grid(row = 6, column = 1)
name_label4.grid(row=7, column = 0)
option4.grid(row = 7, column = 1)
name_label5.grid(row=8, column = 0)
option5.grid(row = 8, column = 1)
name_label6.grid(row=9, column = 0)
option6.grid(row = 9, column = 1)
name_label7.grid(row=10, column = 0)
option7.grid(row = 10, column = 1)
name_label8.grid(row=11, column = 0)
option8.grid(row = 11, column = 1)
inv_button.grid(row=12, column=1)
addToBuild.grid(row=13, column=1)
buildsList.grid(row=13, column=4)
getBuild.grid(row=13, column=2)
sellBuild.grid(row=13, column = 3)
price_sold.grid(row=14, column = 0)
enter_price.grid(row=14, column = 1)
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

active = False
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
        if latest_key == 'Key.space':
            confirm = 67
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
        updateInv()
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
            num = 0
            with open("id.txt", "r") as file:
                content = file.read()
                try:
                    num = int(content.strip())
                except ValueError:
                    num = 0
            num += 1
            with open("id.txt", "w") as file:
                file.write(str(num))
            sql_command = """INSERT INTO inv
            VALUES (""" + str(num) + """, -1, 1,'""" + labels[currentObj] + """','""" + sub_name + """', 'a',""" + sub_price + """,""" + """-1);"""

            print(sql_command)
            crsr.execute(sql_command)
            connection.commit()

            sql_command = """SELECT * FROM inv;"""
            crsr.execute(sql_command)
            updateInv()
            updateChoices()
            root.update()
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