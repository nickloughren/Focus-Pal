from PIL import ImageGrab
import time
from functools import partial
from datetime import datetime
import cv2 as cv
from matplotlib import pyplot as plt
import PySimpleGUI as sg # pip install pysimplegui
import os
import glob
import click # pip install click

def cv_rescale(frame, scale=0.5):
    width = int(frame.shape[1]*scale)
    height = int(frame.shape[0]*scale)
    dimensions = (width, height)
    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)

def clear_images():
    if click.confirm('Are you sure you want to delete all your screenshots?:', default=False):
        files = glob.glob(pathname= 'C:/Users/Surface Pro 6/Desktop'
                          '/Focus-Pal/**/*.png', recursive=True)
        for f in files:
            print(f"Now deleting: {f}")
            os.remove(f)
    return

def startup_gui():

    layout = [
        [sg.Text(text='😁📚StudyShame.ai📚😁', font=('Arial Bold', 48),
        size=20, expand_x=True, justification='center', background_color = '#21535b')],
        [sg.Text(text='The app that uses guilt to keep you on task :)', font=('Arial', 18), expand_x=True, background_color = '#21535b')],
        [sg.Text("What task are we working on?:", font=('Arial', 18)), 
         sg.Input(key="Task", font=('Arial', 24), size = (15,15))],
        [sg.Text("How many check-ins do you need?:", font=('Arial', 18)), 
         sg.Input(key="Num Check-ins", font=('Arial', 24), size = (5,5))],
        [sg.Text("Roughly every:", font=('Arial', 18)), 
         sg.Input(key="Interval", font=('Arial', 24), size = (5,5), default_text="20"),
         sg.Text("minutes", font=('Arial', 18))],
        [sg.Button("Let's Frocken GO!!!", font=('Arial Bold', 32))],
        [sg.Exit()]
    ]

    window = sg.Window("StudyShame Initiator", layout, 
                       text_justification='center', element_justification='center')

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            abort = True
            return None, None, abort
        if event == "Let's Frocken GO!!!":
            abort = False
            task = values["Task"]
            num_checkins = values["Num Check-ins"]
            interval = values["Interval"]
            if num_checkins.isdigit():
                num_checkins = int(num_checkins)
                break
            else: 
                sg.popup_error(f'"{num_checkins}" is not a valid integer.',  keep_on_top=True,)  
            if interval.isdigit():
                interval = int(interval)
                break
            else: 
                sg.popup_error(f'"{interval}" is not a valid integer.',  keep_on_top=True,) 
    window.close()
    return task, num_checkins, abort

def take_screenshot():
    print('Taking screenshot...')

    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

    image = ImageGrab.grab()
    screenshot_time = str(datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
    filepath = (f'screenshots/{screenshot_time}_ss.png')
    image.save(filepath)

    global screenshot_count
    screenshot_count += 1

    print(f"#{screenshot_count} saved!")

    return filepath, screenshot_time

def take_photo():
    capture = cv.VideoCapture(0)
    for i in range(60):
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame")
            return

        cv.imshow('Video',frame)
        if cv.waitKey(1) & 0xFF==ord('d'):
            break
    photo_time = str(datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
    photo_path =f'photos/{photo_time}_ss.png'
    cv.imwrite(photo_path,frame)
    capture.release()
    cv.destroyAllWindows()
    return photo_path, photo_time

def capture_and_checkin(task):

    if not task: task = "staying on task"

    #saving original screenshot and scaled-down version for displaying
    screenshot_path, screenshot_time = take_screenshot()
    temp_path = 'temp_img.png'
    screenshot = cv.imread(screenshot_path)
    small_screenshot = cv_rescale(screenshot, scale=0.2)
    cv.imwrite(temp_path, small_screenshot)

    #again for photo
    photo_path, photo_time = take_photo()
    temp_path2 = 'temp_img2.png'
    photo = cv.imread(photo_path)
    small_photo = cv_rescale(photo, scale=0.3)
    cv.imwrite(temp_path2, small_photo)

    layout = [
        [sg.Text(text=f'Is this what {task} looks like???', font=('Arial Bold', 24),
        size=20, expand_x=True, justification='center', background_color = '#21535b')],
        [sg.Image('temp_img.png', expand_x=True, expand_y=True),
         sg.Image('temp_img2.png', expand_x=True, expand_y=True)],
        [sg.Button("Yes🤩", font=('Arial Bold', 48)), 
         sg.Button("No😔", font=('Arial Bold', 48))],
        [sg.Text("If not, what is it?:"), sg.Input(key="-IN-"), sg.FileBrowse()]
    ]

    window = sg.Window("20 min Check-in", layout, size=(900,700), keep_on_top=True,
                       disable_minimize=True, disable_close=True,
                       element_justification='center')

    old_screenshot_path = screenshot_path
    old_photo_path = photo_path
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        if event == "Yes🤩":
            screenshot_path = (f'screenshots/yes/{screenshot_time}_ss.png')
            photo_path = (f'photos/yes/{screenshot_time}_ss.png')
            is_on_task = True
            break
        if event == "No😔":
            screenshot_path = (f'screenshots/no/{screenshot_time}_ss.png')
            photo_path = (f'photos/no/{screenshot_time}_ss.png')
            is_on_task = False
            break

    window.close()

    os.rename(old_screenshot_path, screenshot_path)
    os.rename(old_photo_path, photo_path)

    os.remove(temp_path)
    os.remove(temp_path2)

    return is_on_task

# def countdown(time):

def main():
    num_redos = 0

    task, num_checkins, abort = startup_gui()

    if abort: return

    global screenshot_count 
    screenshot_count = 0 

    while screenshot_count < (num_checkins + num_redos):
        is_on_task = capture_and_checkin(task)
        if not is_on_task:
            num_redos += 1
        time.sleep(1)
        
if __name__ == '__main__':
    main()
    # clear_images()