from PIL import ImageGrab
import numpy as np
import time
from functools import partial
from datetime import datetime, timedelta
import cv2 as cv
from matplotlib import pyplot as plt
import PySimpleGUI as sg # pip install pysimplegui
import os
import glob
import click # pip install click
import csv

def cv_rescale(frame, scale=0.5):
    width = int(frame.shape[1]*scale)
    height = int(frame.shape[0]*scale)
    dimensions = (width, height)
    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)

def clear_images():
    if click.confirm('Are you sure you want to delete all your screenshots?:', default=False):
        files = glob.glob(pathname= '**/*.png', recursive=True)
        for f in files:
            print(f"Now deleting: {f}")
            os.remove(f)
    return

def convert_to_int(string):

    if string.isdigit():
        return int(string)
    else: 
        sg.popup_error(f'"{string}" is not a valid integer.',  keep_on_top=True,)
        return None

def startup_gui():

    layout = [
        [sg.Text(text='😁📚StudyShame.ai📚😁', font=('Arial Bold', 48),
        size=20, expand_x=True, justification='center', background_color = '#21535b')],
        [sg.Text(text='The app that uses guilt & passive aggression to keep you on task :)', font=('Arial', 18), expand_x=True, background_color = '#21535b')],
        [sg.Text("What will you be working on?:", font=('Arial', 18)), 
         sg.Input(key="Task", font=('Arial', 24), size = (15,15))],
        [sg.Text("For how long?:", font=('Arial', 18)), 
         sg.Input(key="Duration hr", font=('Arial', 24), size = (5,5), default_text="0"),
         sg.Text("hours", font=('Arial', 18)), 
         sg.Input(key="Duration min", font=('Arial', 24), size = (5,5), default_text="60"),
         sg.Text("mins", font=('Arial', 18))],
        [sg.Text("How often should we check in?: every", font=('Arial', 18)), 
         sg.Input(key="Interval", font=('Arial', 24), size = (5,5), default_text="5"),
         sg.Text("mins", font=('Arial', 18))],
        [sg.Button("Let's Frocken GO!!!", font=('Arial Bold', 32)),sg.Exit()]
    ]

    layout = add_todays_total(layout, 0)

    window = sg.Window("StudyShame Initiator", layout, 
                       text_justification='center', element_justification='center',
                       keep_on_top=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            abort = True
            return None, None, None, abort
        if event == "Let's Frocken GO!!!":
            abort = False
            task = values["Task"]
            if not task: task = "focused work"
            duration_hr = values["Duration hr"]
            duration_min = values["Duration min"]
            interval = values["Interval"]

            duration_hr = convert_to_int(duration_hr)
            if not isinstance(duration_hr, int): continue
            duration_min = convert_to_int(duration_min)
            if not isinstance(duration_min, int): continue
            interval = convert_to_int(interval)
            if not isinstance(interval, int): continue

            duration = duration_hr*60 + duration_min

            break

    window.close()
    return task, duration, interval, abort

def flash():

    layout = [
        [sg.Text(text='😁Say cheese😁', font=('Arial Bold', 48),
        size=20, expand_x=True, justification='center')],
    ]

    window = sg.Window("StudyShame Initiator", layout, size = (7000,7000),
                       location = (-1000,-1000),
                       keep_on_top=True, background_color='white')
    event, values = window.read(timeout=1)
    return window

def take_screenshot():
    # print('Taking screenshot...')

    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

    image = ImageGrab.grab()
    screenshot_time = str(datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
    filepath = (f'screenshots/{screenshot_time}_ss.png')
    image.save(filepath)

    return filepath, screenshot_time

def take_photo():

    capture = cv.VideoCapture(0)

    for i in range(40):
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame")
            return
        if i == 20:
            window = flash()

        # cv.imshow('Video',frame)
        # if cv.waitKey(1) & 0xFF==ord('d'):
            # break
    window.close()
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
    small_photo = cv_rescale(photo, scale=0.8)
    cv.imwrite(temp_path2, small_photo)

    layout = [
        [sg.Text(text=f'Is this what {task} looks like???', font=('Arial Bold', 24),
        size=20, expand_x=True, justification='center', background_color = '#21535b')],
        [sg.Image('temp_img.png', expand_x=True, expand_y=True, background_color='black'),
         sg.Image('temp_img2.png', expand_x=True, expand_y=True, background_color='black')],
        [sg.Button("Yes🤩", font=('Arial Bold', 48)), 
         sg.Button("No😔", font=('Arial Bold', 48))],
        [sg.Button("Yes, but don't save images", font=('Arial Bold', 8)), 
         sg.Button("No, but don't save images", font=('Arial Bold', 8))],
    ]

    window = sg.Window("StudyShame Check-in", layout, size=(1100,800), keep_on_top=True,
                       disable_minimize=True, disable_close=True,
                       element_justification='center', background_color='black')

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

        if event == "No😔":
            screenshot_path = (f'screenshots/no/{screenshot_time}_ss.png')
            photo_path = (f'photos/no/{screenshot_time}_ss.png')
            is_on_task = False

        if event == "Yes, but don't save images":
            is_on_task = True
            os.remove(screenshot_path)
            os.remove(photo_path)
            break

        if event == "No, but don't save images":
            is_on_task = True
            os.remove(screenshot_path)
            os.remove(photo_path)
            break

        os.rename(old_screenshot_path, screenshot_path)
        os.rename(old_photo_path, photo_path)
        break

    window.close()

    os.remove(temp_path)
    os.remove(temp_path2)

    return is_on_task

def add_noise(values, std_dev=1):
    values = np.array(values)
    noise = np.random.normal(scale=std_dev, size=len(values)).astype(int)
    noisy_values = values + noise
    return noisy_values

def give_up():
    layout = [
        [sg.Text(text="Are you sure you want to lose all your progress?", font=('Arial Bold', 12),
        size=20, expand_x=True, expand_y=True, justification='center', background_color = '#21535b', key="-Remaining-")],
        [sg.Text(text="There really is no going back.", font=('Arial', 10), expand_x=True, expand_y=True, background_color = '#21535b', key="-Completion-")],
        [sg.Button("I'm sure", font=('Arial Bold', 16)), sg.Button("Good point, let's keep going", font=('Arial Bold', 16))]
    ]

    window = sg.Window("StudyShame.ai", layout, size = (500,100),
                        text_justification='center', element_justification='center',
                        disable_minimize=True, disable_close=True, keep_on_top=True,
                        no_titlebar=True, grab_anywhere=True)
    
    event, values = window.read(timeout=15000)
    abort = False
    if event == "I'm sure":
        abort = True
    # if event == "Good point, let's keep going":
    #     abort = False
    window.close()
    return abort

def countdown_and_checkins(task, duration, interval): #change timer speed here

    num_millisecs = 1000 #change to speed up

    added_time = 0
    elapsed_time = 0
    time_completed = 0
    time_remaining = duration
    total_duration = duration

    completion_time, time_remaining_string = update_timer_times(time_remaining)

    timer_layout = [
        [sg.Text(text=time_remaining_string, font=('Arial Bold', 22),
        size=20, expand_x=True, expand_y=True, justification='center', background_color = '#21535b', key="-Remaining-")],
        [sg.Text(text=completion_time, font=('Arial', 12), expand_x=True, expand_y=True, background_color = '#21535b', key="-Completion-")],
        [sg.Button("Give up", font=('Arial Bold', 8))]
    ]

    timer_window = sg.Window("StudyShame.ai", timer_layout, size = (100,100),
                       text_justification='center', element_justification='center',
                       disable_minimize=True, disable_close=True, keep_on_top=True,
                       no_titlebar=True, grab_anywhere=True)


    checkin_times = [*range(interval,duration+1,interval)] # first check-in at time "interval", last at duration+1 (exclusive)
    std_dev = interval/2
    noisy_checkin_times = add_noise(checkin_times, std_dev)
    # print(noisy_checkin_times)

    while elapsed_time < total_duration:
        event, values = timer_window.read(timeout=60*num_millisecs)

        if event == "Give up":
            if give_up():
                success = False
                timer_window.close()
                return duration, success, time_completed
            else: continue

        elapsed_time += 1
        print(elapsed_time)

        if elapsed_time in noisy_checkin_times:
            is_on_task = capture_and_checkin(task)
            if not is_on_task:
                added_time += interval
                checkin_times.append(duration+added_time)
                noisy_checkin_times = add_noise(checkin_times, std_dev)
                # print(noisy_checkin_times) 
            else: time_completed = elapsed_time - added_time

        total_duration = duration + added_time  
        time_remaining = total_duration - elapsed_time

        completion_time, time_remaining_string = update_timer_times(time_remaining)
        timer_window["-Remaining-"].update(time_remaining_string)
        timer_window["-Completion-"].update(completion_time)

        timer_window.refresh()

    timer_window.close()
    success = True
    time_completed = duration
    return duration, success, time_completed

def update_timer_times(time_remaining):
        current_time = datetime.now()
        time_to_add = timedelta(minutes=time_remaining)
        completion_time = current_time + time_to_add
        completion_time = str(completion_time.strftime("%I:%M %p"))
        time_remaining_string = str(time_to_add)[:-3]
        return completion_time, time_remaining_string 

def write_to_csv(list):
    with open('logbook.csv', 'a') as f_object:
        writer_object = csv.writer(f_object, lineterminator='\n')
        writer_object.writerow(list)
        f_object.close()
    return

def keep_going(duration, success, task, time_completed):

    if success:
        layout = [
            [sg.Text(text="You did it!🥳", font=('Arial Bold', 24),
            size=20, expand_x=True, expand_y=True, justification='center', background_color = '#21535b', key="-Remaining-")],
            [sg.Text(text= f"You completed {duration} minutes of {task}!", 
                    font=('Arial', 10), expand_x=True, expand_y=True, background_color = '#21535b', key="-Completion-")],
            [sg.Button("Go again", font=('Arial Bold', 16)), sg.Button("Quit", font=('Arial Bold', 16))]
        ]
    else: 
        layout = [
            [sg.Text(text="You failed:(", font=('Arial Bold', 24),
            size=20, expand_x=True, expand_y=True, justification='center', background_color = '#21535b', key="-Remaining-")],
            [sg.Text(text= f"We believed in you but you only did {time_completed} out of the {duration}",
                    font=('Arial', 10), expand_x=True, expand_y=True, background_color = '#21535b', key="-Completion-")],
            [sg.Text(text= f"minutes of {task} that you promised.",
                    font=('Arial', 10), expand_x=True, expand_y=True, background_color = '#21535b', key="-Completion-")],
            [sg.Button("I'm sorry, lemme try again", font=('Arial Bold', 16)), sg.Button("Quit", font=('Arial Bold', 16))]
        ]

    layout = add_todays_total(layout, 0)

    window = sg.Window("StudyShame.ai", layout,
                        text_justification='center', element_justification='center', 
                        grab_anywhere=True, keep_on_top=True)
    
    event, values = window.read()
    if event == "Go again" or "I'm sorry, lemme try again":
        keep_going = True
    if event == "Quit":
        keep_going = False
    window.close()
    return keep_going

def add_todays_total(layout, unlogged_time):
    '''adds a total number of completed minutes for
     the day under give_up, keep_going and startup'''

    # read only the last 20 lines to save RAM
    with open("logbook.csv") as file:
        last_lines = [line for i, line in enumerate(file)][-20:]

    rows = csv.reader(last_lines)

    # get today's date in the same format as the CSV
    today = datetime.now().strftime("%y-%m-%d")

    total_time_completed = 0

    # iterate over the CSV rows
    for row in rows:

        if row[0][0].isdigit() and len(row)==4: #excluding header and any invalid rows
            date_time, success, duration, time_completed = row
            
            # check if the date matches today's date
            if date_time.split("_")[0] == today:
                total_time_completed += int(time_completed)

    total_time_completed += int(unlogged_time)

    todays_total_string=f"Today's total: {total_time_completed} min"
    todays_total = [sg.Text(text=todays_total_string, font=('Arial', 10),
        size=20, expand_x=True, expand_y=True, justification='center', key="-Todays Total-")]
    layout.append(todays_total)
    return layout
    
def main():

    while True:
        task, duration, interval, abort = startup_gui()
        if abort: return

        # duration = 3
        # interval = 12

        duration, success, time_completed = countdown_and_checkins(task, duration, interval)
        now = str(datetime.now().strftime("%y-%m-%d_%H-%M"))
        log_data = [now,success,duration, time_completed]
        write_to_csv(log_data)

        if not keep_going(duration, success, task, time_completed): break

if __name__ == '__main__':
    # take_photo()
    # capture_and_checkin("f")
    # keep_going(1,True,"fuckshit",10)
    # write_to_csv(['lol',1,100,])
    main()
    # clear_images()