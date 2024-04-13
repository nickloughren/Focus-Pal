# Description: The accountability partner for those who have no friends to keep them accountable.

# To install:

# cd Documents\GitHub\Focus-Pal

# pyinstaller --onefile --name StudyShame --distpath EXE main.pyw
# or
# auto-py-to-exe
# or
# pyinstaller --noconfirm --onefile --windowed  "C:/Users/Surface Pro 6/Documents/GitHub/Focus-Pal/main.pyw"


import numpy as np
import time
from functools import partial
from datetime import datetime, timedelta
import os
import glob
import json
import shutil
import random

import cv2 as cv  # pip install opencv-python / pip install opencv-contrib-python
import matplotlib.figure as figure  # pip install matplotlib
import matplotlib.ticker as plticker
import matplotlib.patheffects as pe
import PySimpleGUI as sg  # pip install pysimplegui
from PIL import ImageGrab  # pip install PIL
import pandas as pd
import pytz


def cv_rescale(original_path, resized_path, scale=0.5):
    frame = cv.imread(original_path)
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    resized_frame = cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)
    cv.imwrite(resized_path, resized_frame)
    return resized_path


def clear_images():
    confirmation = input(
        "Are you sure you want to delete all your images? (type y/n): "
    )
    if confirmation == "y":
        files = glob.glob(pathname="**/*.png", recursive=True)
        for f in files:
            print(f"Now deleting: {f}")
            os.remove(f)
    else:
        print("Ok, your images will remain.")
    return


def convert_to_int(string):
    if string.isdigit() or string[0] == "-":
        return int(string)
    else:
        sg.popup_error(
            f'"{string}" is not a valid integer.',
            keep_on_top=True,
        )
        return None


def startup_gui():
    text_background_color = "#477320"
    menu_open = False

    today = datetime.now()
    this_morn = today.replace(hour=0, minute=0, second=0, microsecond=0)
    unix_time_this_morn = int(this_morn.timestamp())

    filename = "_SETTINGS.json"
    with open(filename, "r") as file:
        data = json.load(file)
    default_interval = data["Default Check-in Interval (min)"]
    default_goal_hrs = data["Default Goal (hr)"]
    default_goal_mins = data["Default Goal (min)"]
    default_streaks_bool = data["Default to using the streaks feature? (True/False)"]
    secret_button_allowed = (
        data["Should the forbidden button be accessible? (True/False)"] == "True"
    )

    hidden_menu = [
        [
            sg.Text(
                (
                    "                                                        "
                    + 'Would you like to use the "Streaks" feature?:'
                ),
                font=("Arial", 12),
            ),
            sg.Checkbox(
                "",
                default=default_streaks_bool == "True",
                checkbox_color=text_background_color,
                key="-Streaks-",
            ),
        ],
        [
            sg.Text("What will you be working on?:", font=("Arial", 18)),
            sg.Input(
                key="Task",
                font=("Arial", 24),
                size=(20, 20),
                default_text="serious important work",
            ),
        ],
        [
            sg.Text(
                (
                    "                                                        "
                    + "Do you want photo evidence?:"
                ),
                font=("Arial", 12),
            ),
            sg.Checkbox(
                "",
                default=False,
                checkbox_color=text_background_color,
                key="-Pictures Allowed-",
            ),
        ],
        # [
        #     sg.Button(
        #         "Forbidden button that should only be pressed if you know what you're doing! >:(",
        #         font=("Arial", 8),
        #         key="-Add Time-",
        #     )
        # ],
        [
            sg.Text(
                text='Open the file "_SETTINGS.json" for even more options!',
                font=("Arial", 12),
                expand_x=True,
                # text_color="black",
                # background_color=text_background_color,  # "#21535b",
            )
        ],
    ]
    if secret_button_allowed:
        hidden_menu.append(
            [
                sg.Text(
                    text="                                 ",
                ),
                sg.Button(
                    "Forbidden button that should only be pressed if you know what you're doing! >:(",
                    font=("Arial", 8),
                    key="-Add Time-",
                ),
            ],
        )

    layout = [
        [
            sg.Text(
                text="😁📚StudyShame📚😁",
                font=("Arial Bold", 48),
                size=20,
                expand_x=True,
                justification="center",
                # text_color="black",
                background_color=text_background_color,  # "#21535b",
            )
        ],
        [
            sg.Text(
                text="The app that uses guilt & passive aggression to keep you on task :)",
                font=("Arial", 18),
                expand_x=True,
                # text_color="black",
                background_color=text_background_color,  # "#21535b",
            )
        ],
        [
            sg.Text("What's our goal for today?:", font=("Arial", 18)),
            sg.Input(
                key="Duration hr",
                font=("Arial", 24),
                size=(5, 5),
                default_text=default_goal_hrs,
            ),
            sg.Text("hours", font=("Arial", 18)),
            sg.Input(
                key="Duration min",
                font=("Arial", 24),
                size=(5, 5),
                default_text=default_goal_mins,
            ),
            sg.Text("mins", font=("Arial", 18)),
        ],
        [
            sg.Text("How often should I check in?: every", font=("Arial", 18)),
            sg.Input(
                key="Interval",
                font=("Arial", 24),
                size=(5, 5),
                default_text=str(default_interval),
            ),
            sg.Text("mins", font=("Arial", 18)),
        ],
        [
            sg.T(
                "►",
                enable_events=True,
                k="-OPEN MENU-",
                font=("Arial", 16),
            ),
            sg.T(
                "Advanced Settings",
                font=("Arial", 16),
                enable_events=True,
                k="-OPEN MENU-TEXT",
            ),
        ],
        [sg.pin(sg.Column(hidden_menu, key="-MENU-", visible=menu_open))],
        [sg.Button("Let's GO!!!", font=("Arial Bold", 32)), sg.Exit()],
    ]

    layout, _, _, _ = add_todays_total(layout)

    window = sg.Window(
        "StudyShame Initiator",
        layout,
        text_justification="center",
        element_justification="center",
        keep_on_top=True,
    )

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            abort = True
            return None, None, None, None, abort, None, None, None
        if event.startswith("-OPEN MENU-"):
            menu_open = not menu_open
            window["-OPEN MENU-"].update("▼" if menu_open else "►")
            window["-MENU-"].update(visible=menu_open)
        if event == "-Add Time-":
            add_time()
        if event == "Let's GO!!!":
            abort = False
            task = values["Task"]
            if not task:
                task = "focused work"
            duration_hr = values["Duration hr"]
            duration_min = values["Duration min"]
            interval = values["Interval"]
            pictures_allowed = values["-Pictures Allowed-"]
            streaks_bool = values["-Streaks-"]

            duration_hr = convert_to_int(duration_hr)
            if not isinstance(duration_hr, int):
                continue
            duration_min = convert_to_int(duration_min)
            if not isinstance(duration_min, int):
                continue
            interval = convert_to_int(interval)
            if not isinstance(interval, int):
                continue

            duration = duration_hr * 60 + duration_min

            central = pytz.timezone("US/Central")
            today = datetime.now(central)
            this_morn = today.replace(hour=0, minute=0, second=0, microsecond=0)
            unix_time_this_morn = int(this_morn.timestamp())

            break

    window.close()
    return (
        task,
        duration,
        interval,
        pictures_allowed,
        abort,
        streaks_bool,
        secret_button_allowed,
        unix_time_this_morn,
    )


def flash():
    layout = [
        [
            sg.Text(
                text="😁Say cheese😁",
                font=("Arial Bold", 48),
                size=20,
                expand_x=True,
                justification="center",
            )
        ],
    ]

    window = sg.Window(
        "StudyShame Initiator",
        layout,
        size=(7000, 7000),
        location=(-1000, -1000),
        keep_on_top=True,
        background_color="white",
    )
    event, values = window.read(timeout=1)
    return window


def take_screenshot():
    # print('Taking screenshot...')

    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

    image = ImageGrab.grab()
    screenshot_time = str(datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
    filepath = f"screenshots/{screenshot_time}.png"
    image.save(filepath)

    return filepath, screenshot_time


def take_photo():
    capture = cv.VideoCapture(0)

    for i in range(40):
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame.")
            return
        if i == 20:
            window = flash()

        # cv.imshow('Video',frame)
        # if cv.waitKey(1) & 0xFF==ord('d'):
        # break
    window.close()
    photo_time = str(datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
    photo_path = f"photos/{photo_time}.png"
    cv.imwrite(photo_path, frame)
    capture.release()
    cv.destroyAllWindows()
    return photo_path, photo_time


def checkin(task, pictures_allowed):
    text_background_color = "#477320"
    if not task:
        task = "staying on task"

    if pictures_allowed:
        # saving original screenshot and scaled-down version for displaying
        screenshot_path, screenshot_time = take_screenshot()
        screenshot_temp_path = "screenshot_temp_img.png"
        small_screenshot = cv_rescale(screenshot_path, screenshot_temp_path, scale=0.15)

        # again for photo
        photo_path, photo_time = take_photo()
        photo_temp_path = "photo_temp_img.png"
        small_photo = cv_rescale(photo_path, photo_temp_path, scale=0.4)

        layout = [
            [
                sg.Text(
                    text=f'Is this what "{task}" looks like???',
                    font=("Arial Bold", 20),
                    size=20,
                    expand_x=True,
                    justification="center",
                    background_color=text_background_color,
                )
            ],
            [
                sg.Image(
                    small_screenshot,
                    expand_x=True,
                    expand_y=True,
                    # background_color="black",
                ),
                sg.Image(
                    small_photo,
                    expand_x=True,
                    expand_y=True,  # background_color="black"
                ),
            ],
            [
                sg.Button("Yes🤩", font=("Arial Bold", 56)),
                sg.Button("No😔", font=("Arial Bold", 56)),
            ],
            [
                sg.Button("Yes, but don't save images", font=("Arial Bold", 12)),
                sg.Button("No, but don't save images", font=("Arial Bold", 12)),
            ],
        ]

        old_screenshot_path = screenshot_path
        old_photo_path = photo_path
    else:
        layout = [
            [
                sg.Text(
                    text=f"You on task?",
                    font=("Arial Bold", 24),
                    size=20,
                    expand_x=True,
                    justification="center",
                    background_color=text_background_color,
                )
            ],
            [
                sg.Button("Yes", font=("Arial Bold", 48)),
                sg.Button("No", font=("Arial Bold", 48)),
            ],
        ]

    window = sg.Window(
        "StudyShame Check-in",
        layout,
        # size=(750, 750),
        keep_on_top=True,
        disable_minimize=True,
        disable_close=True,
        element_justification="center",
        # background_color="black",
    )

    event, values = window.read()
    if event == "Yes🤩":
        screenshot_path = f"screenshots/yes/{screenshot_time}.png"
        photo_path = f"photos/yes/{photo_time}.png"
        is_on_task = True
        os.rename(
            old_screenshot_path, screenshot_path
        )  # from screenshots/_.png to screenshots/yes/_.png
        os.rename(old_photo_path, photo_path)

    if event == "No😔":
        screenshot_path = f"screenshots/no/{screenshot_time}.png"
        photo_path = f"photos/no/{photo_time}.png"
        is_on_task = False
        os.rename(old_screenshot_path, screenshot_path)
        os.rename(old_photo_path, photo_path)

    if event == "Yes, but don't save images":
        is_on_task = True
        os.remove(screenshot_path)
        os.remove(photo_path)

    if event == "No, but don't save images":
        is_on_task = False
        os.remove(screenshot_path)
        os.remove(photo_path)

    if event == "Yes":
        is_on_task = True

    if event == "No":
        is_on_task = False

    window.close()

    if pictures_allowed:
        os.remove(screenshot_temp_path)
        os.remove(photo_temp_path)

    return is_on_task


def add_noise(values, std_dev=1):
    values = np.array(values)
    noise = np.random.normal(scale=std_dev, size=len(values)).astype(int)
    noisy_values = values + noise
    return noisy_values


def give_up(goal_already_achieved, secret_button_allowed):
    text_background_color = "#477320"

    layout = [
        [
            sg.Text(
                text="Are you sure you want to quit?",
                font=("Arial Bold", 12),
                size=20,
                expand_x=True,
                expand_y=True,
                justification="center",
                background_color=text_background_color,
                key="-Remaining-",
            )
        ],
        [
            sg.Button("I'm sure", font=("Arial Bold", 16)),
            sg.Button("Let's keep going", font=("Arial Bold", 16)),
        ],
        # [
        #     sg.Button(
        #         "Forbidden button that should only be pressed if you know what you're doing! >:(",
        #         font=("Arial", 8),
        #         key="-Add Time-",
        #     )
        # ],
    ]
    if secret_button_allowed:
        layout.append(
            [
                sg.Button(
                    "Forbidden button that should only be pressed if you know what you're doing! >:(",
                    font=("Arial", 8),
                    key="-Add Time-",
                )
            ],
        )

    if not goal_already_achieved:
        encouragement = [
            sg.Text(
                text="You'll lose all you progress since the last checkin.",
                font=("Arial", 10),
                expand_x=True,
                expand_y=True,
                background_color=text_background_color,
                key="-Completion-",
            )
        ]

        layout.insert(1, encouragement)

    window = sg.Window(
        "StudyShame.ai",
        layout,
        # size=(500, 100),
        text_justification="center",
        element_justification="center",
        disable_minimize=True,
        disable_close=True,
        keep_on_top=True,
        no_titlebar=True,
        grab_anywhere=True,
    )

    event, values = window.read(timeout=15 * 1000)
    abort = False
    if event == "I'm sure":
        abort = True
    if event == "-Add Time-":
        window.close()
        return add_time()
    window.close()
    return abort


def add_time():
    text_background_color = "#477320"
    layout = [
        [
            sg.Text(
                text="Add/Subtract time completed",
                font=("Arial", 18),
                expand_x=True,
                # text_color="black",
                background_color=text_background_color,  # "#21535b",
            )
        ],
        [
            sg.Input(key="hr", font=("Arial", 24), size=(5, 5), default_text="0"),
            sg.Text("hours", font=("Arial", 18)),
            sg.Input(key="min", font=("Arial", 24), size=(5, 5), default_text="0"),
            sg.Text("mins", font=("Arial", 18)),
        ],
        # [
        #     sg.Text("Add?:", font=("Arial", 12)),
        #     sg.Checkbox(
        #         "",
        #         default=False,
        #         checkbox_color=text_background_color,
        #         key="-add-",
        #     ),
        # ],
        [
            sg.Button("Submit", font=("Arial Bold", 32)),
            sg.Button("Back", font=("Arial Bold", 32)),
        ],
    ]

    layout, _, _, _ = add_todays_total(layout)

    window = sg.Window(
        "Add/Subtract Time",
        layout,
        text_justification="center",
        element_justification="center",
        keep_on_top=True,
    )

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Back"):
            time_2_add = 0
            break
        elif event == "Submit":
            hours = values["hr"]
            mins = values["min"]

            hours = convert_to_int(hours)
            if not isinstance(hours, int):
                continue
            mins = convert_to_int(mins)
            if not isinstance(mins, int):
                continue

            time_2_add = hours * 60 + mins

            break

    window.close()
    update_log(0, time_2_add)
    return time_2_add


def countdown_window(time_remaining):
    text_background_color = "#234f00"  # "#477320"
    completion_time, time_remaining_string = update_countdown_times(time_remaining)

    timer_layout = [
        [
            sg.Text(
                text=time_remaining_string,
                font=("Arial Bold", 22),
                size=20,
                expand_x=True,
                expand_y=True,
                justification="center",
                background_color=text_background_color,
                key="-Remaining-",
                # text_color="black",
            )
        ],
        [
            sg.Text(
                text=completion_time,
                font=("Arial", 12),
                expand_x=True,
                expand_y=True,
                background_color=text_background_color,
                key="-Completion-",
                # text_color="black",
            )
        ],
        [
            sg.Button(
                "Give up",
                font=("Arial Bold", 8),
                border_width=1,
                key="-Give Up-",
            )
        ],
    ]

    timer_window = sg.Window(
        "StudyShame.ai",
        timer_layout,
        size=(100, 115),
        text_justification="center",
        element_justification="center",
        disable_minimize=True,
        disable_close=True,
        keep_on_top=True,
        no_titlebar=True,
        grab_anywhere=True,
        # alpha_channel=0.8,
    )

    return timer_window


def countup_window():
    text_background_color = "#234f00"

    time_completed_str = f"0:00"

    # I decided to have this func output today's goal
    _, _, goal_today, _ = add_todays_total([])
    goal_str = timedelta(minutes=goal_today)
    goal_str = str(goal_str)[:-3]
    goal_str = f"Goal: {goal_str}"

    timer_layout = [
        [
            sg.Text(
                text=time_completed_str,
                font=("Arial Bold", 22),
                size=20,
                expand_x=True,
                expand_y=True,
                justification="center",
                background_color=text_background_color,
                key="-Completed-",
            )
        ],
        [
            sg.Text(
                text=goal_str,
                font=("Arial", 12),
                expand_x=True,
                expand_y=True,
                background_color=text_background_color,
                key="-Goal-",
            )
        ],
        [sg.Button("Quit", font=("Arial Bold", 8), border_width=0, key="-Give Up-")],
    ]

    timer_window = sg.Window(
        "StudyShame.ai",
        timer_layout,
        size=(100, 115),
        text_justification="center",
        element_justification="center",
        disable_minimize=True,
        disable_close=True,
        keep_on_top=True,
        no_titlebar=True,
        grab_anywhere=True,
    )

    return timer_window


def checkin_times(interval):
    # Generates either random or semi-random numbers.
    max_num_minutes = 60 * 24 * 7

    # # generates a set of times that are semi-random. This is to
    # # ensure that roughly every X minutes there will be a
    # # checkin while maintaining unpredictibility (fully random)
    # checkin_times = [*range(interval, max_num_minutes, interval)]
    # checkin_times = add_noise(checkin_times, std_dev=interval)

    # Generates a list of max_num_minutes/interval numbers from 1 to max_num_minutes (fully random)
    checkin_times = random.sample(
        range(1, max_num_minutes), int(max_num_minutes / interval)
    )

    return checkin_times


def countdown_and_checkins(
    task,
    goal,
    interval,
    pictures_allowed,
    streaks_bool,
    secret_button_allowed,
    time_this_morn,
):
    sec_2_msec = 1000  # decrease to speed up
    time_elapsed = 0
    time_completed = 0
    time_remaining = goal
    time_since_last_checkin = 0
    current_time = time.time()
    streak_minutes = 0
    streak_bonus = 0.9

    timer_window = countdown_window(time_remaining)

    checkins = checkin_times(interval)

    update_log(goal, 0)

    while (time_completed + time_since_last_checkin) < goal:
        if its_bedtime(time_this_morn):
            update_log(goal, time_since_last_checkin)
            timer_window.close()
            return time_completed, streak_minutes

        event, values = timer_window.read(timeout=60 * sec_2_msec)
        if event == "-Give Up-":
            giveUp = give_up(False, secret_button_allowed)
            if giveUp == True:
                timer_window.close()
                return time_completed, streak_minutes
            elif giveUp == False:
                continue
            else:  # if giveup returns time to add (int)
                time_completed += giveUp

        time_since_last_checkin += 1
        time_elapsed += 1

        #### STREAKS (streaks speed up your progress if you're on a roll) ####
        previous_time = current_time
        current_time = time.time()
        diff = current_time - previous_time

        streak_minutes = (
            streak_minutes + 1
            if diff < 90
            else streak_minutes - interval if diff < 120 else 0
        )
        streak_bonus = (
            1.1
            if streak_minutes >= 90
            else 1.0 if streak_minutes >= 30 or not streaks_bool else 0.9
        )
        #################
        if time_elapsed in checkins:
            is_on_task = checkin(task, pictures_allowed)
            if not is_on_task:
                time_since_last_checkin -= interval * 1.0
                streak_minutes, streak_bonus = (0, 0.9)
            update_log(goal, round(time_since_last_checkin * streak_bonus))
            time_completed += round(time_since_last_checkin * streak_bonus)
            time_since_last_checkin = 0

        time_remaining = goal - time_completed - time_since_last_checkin

        completion_time, time_remaining_string = update_countdown_times(time_remaining)
        timer_window["-Remaining-"].update(time_remaining_string)
        timer_window["-Completion-"].update(completion_time)
        if streaks_bool:
            timer_window["-Give Up-"].update(f"Streak: {streak_bonus}")

        timer_window.refresh()

        if time_elapsed in checkins:
            _ = add_progress_plot([], 365)

    timer_window.close()
    time_completed = goal
    update_log(goal, time_since_last_checkin)

    return time_completed, streak_minutes


def countup_and_checkins(
    task,
    goal,
    interval,
    pictures_allowed,
    streak_minutes,
    streaks_bool,
    secret_button_allowed,
    time_this_morn,
):
    sec_2_msec = 1000  # decrease to speed up

    time_completed = goal
    time_elapsed = goal
    time_since_last_checkin = 0
    current_time = time.time()

    checkins = checkin_times(interval)

    timer_window = countup_window()
    event, values = timer_window.read(timeout=0)

    while True:
        if its_bedtime(time_this_morn):
            update_log(goal, time_since_last_checkin)
            timer_window.close()
            return time_completed

        _, _, _, time_completed_today = add_todays_total([])
        time_completed_str = timedelta(
            minutes=time_completed_today + time_since_last_checkin
        )
        time_completed_str = str(time_completed_str)[:-3]
        # goal_str = timedelta(minutes=goal)
        # goal_str = "Goal: " + str(goal_str)[:-3]
        timer_window["-Completed-"].update(time_completed_str)
        # timer_window["-Goal-"].update(goal_str)

        timer_window.refresh()

        event, values = timer_window.read(timeout=60 * sec_2_msec)

        if event == "-Give Up-":
            giveUp = give_up(True, secret_button_allowed)
            if giveUp == True:
                update_log(goal, time_since_last_checkin)
                timer_window.close()
                return time_completed
            elif giveUp == False:
                continue
            else:  # if giveup returns time to add (int)
                time_completed += giveUp

        time_elapsed += 1
        time_since_last_checkin += 1

        #### STREAKS (streaks speed up your progress if you're on a roll)####
        previous_time = current_time
        current_time = time.time()
        diff = current_time - previous_time

        streak_minutes = (
            streak_minutes + 1
            if diff < 120
            else streak_minutes - interval if diff < 300 else 0
        )
        streak_bonus = (
            1.1
            if streak_minutes >= 60
            else 1.0 if streak_minutes >= 30 or not streaks_bool else 0.9
        )
        print(streak_bonus, streak_minutes)
        if streaks_bool:
            timer_window["-Give Up-"].update(f"Streak: {streak_bonus}")
        #################

        if time_elapsed in checkins:
            is_on_task = checkin(task, pictures_allowed)
            if not is_on_task:
                time_since_last_checkin -= interval * 1
                streak_minutes, streak_bonus = (0, 0.9)
            update_log(goal, round(time_since_last_checkin * streak_bonus))
            time_completed += round(time_since_last_checkin * streak_bonus)
            time_since_last_checkin = 0
        if time_elapsed in checkins:
            _ = add_progress_plot([], 365)


def update_countdown_times(time_remaining):
    current_time = datetime.now()
    time_to_add = timedelta(minutes=time_remaining)
    completion_time = current_time + time_to_add
    completion_time = str(completion_time.strftime("%I:%M %p"))
    time_remaining_string = str(time_to_add)[:-3]
    return completion_time, time_remaining_string


def its_bedtime(time_this_morn):
    filename = "_SETTINGS.json"
    with open(filename, "r") as file:
        data = json.load(file)
    bedtime_hr = data["Bedtime (hr)"]
    bedtime_min = data["Bedtime (min)"]
    bedtime_am = data["Bedtime (AM or PM)"] == "AM"
    if bedtime_hr == 12:
        bedtime_hr = 0

    bedtime_secs = (
        int(bedtime_hr * 60) + int(bedtime_min) + 12 * 60 + int(bedtime_am) * 12 * 60
    ) * 60  # 10:00PM
    # floor divide time for seconds since midnight, -5hrs for CS

    central = pytz.timezone("US/Central")
    now = datetime.now(central)
    unix_time_now = int(now.timestamp())

    time_secs = (
        unix_time_now - time_this_morn
    )  # this is how long it's been since the morning.

    # now = datetime.now(central)
    # now_minutes = now.hour * 60 + now.minute
    # if now_minutes < 5 * 60:
    #     now_minutes += (
    #         24 * 60
    #     )  # we want times after midnight to be larger than times before
    # # now = (time.time() / 60 - 5 * 60) % (24 * 60)

    return time_secs >= bedtime_secs


def update_log(goal, completed):
    today = datetime.today()
    today_key = str(today.strftime("%y-%m-%d"))

    # Define a dictionary
    new_entry = {today_key: {"goal": int(goal), "completed": int(completed)}}
    filename = "_PROGRESS_LOG.json"

    # 1. Read the JSON file
    with open(filename, "r") as file:
        data = json.load(file)

    # 2. Add the new entry to the dictionary only if the key does not exist
    if today_key not in data or data[today_key]["goal"] == -1:
        data = fill_empty_days_in_log(data, today)
        data.update(new_entry)
    else:
        data[today_key]["completed"] += int(completed)

    # 3. Write the updated JSON data back to the file
    with open(filename, "w") as file:
        json.dump(data, file)

    return


def fill_empty_days_in_log(data, today):
    # updating previous days with 0 completed if inactive

    if len(data) == 0:  # _PROGRESS_LOG is empty
        new_entry = {str(today.strftime("%y-%m-%d")): {"goal": 0, "completed": 0}}
        data.update(new_entry)
        return data

    day = today
    dates_missed = []
    while True:
        day_before = day - timedelta(days=1)
        day_before_key = day_before.strftime("%y-%m-%d")
        if day_before_key not in data:
            dates_missed.insert(0, day_before_key)
            day = day_before
        else:
            break

    for date in dates_missed:
        new_entry = {date: {"goal": 0, "completed": 0}}
        data.update(new_entry)
    return data


def keep_going_layout(goal, time_completed, task, time_this_morn):
    if its_bedtime(time_this_morn):
        header = "Go to bed."
        subheader_1 = (
            f"It's bed time. You accomplished {time_completed} out of {goal} minutes of {task}. "
            + f"But I'm cutting you off. Sleep is essential for health and wellbeing, and that's NO JOKE!"
        )
        button_1 = "Let's try again tomorrow"
    elif time_completed < goal:
        header = "You failed:("
        subheader_1 = (
            f"Wow. Your really let me down. You only did {time_completed} out "
            + f"of the {goal} minutes of {task} that you promised. I believed in you."
        )
        button_1 = "I'm sorry, lemme try again"
    elif time_completed == goal:
        header = "You did it!🥳"
        subheader_1 = f"Wow! You completed {time_completed} minutes of {task}! I knew you had it in you. I'm very proud."
        button_1 = "Main menu"
        button_2 = "Keep going"
    else:
        header = "Nice job!🥳"
        subheader_1 = (
            f"Wow! You completed {time_completed} minutes of {task}!"
            + f" I'm actually speechless. You're straight up killing the game. Look at this graph. You're a MENACE!!!"
        )
        button_1 = "Main menu"

    text_background_color = "#477320"

    layout = [
        [
            sg.Text(
                text=header,
                font=("Arial Bold", 24),
                size=20,
                expand_x=True,
                expand_y=True,
                justification="center",
                background_color=text_background_color,
                key="-Header-",
            )
        ],
        [
            sg.Text(
                text=subheader_1,
                font=("Arial", 10),
                expand_x=True,
                expand_y=True,
                background_color=text_background_color,
                key="-Subheader 1-",
            )
        ],
    ]
    layout = add_progress_plot(layout, 365)
    buttons = [
        sg.Button(button_1, font=("Arial Bold", 16), key="-Main Menu-"),
        sg.Button("Quit", font=("Arial Bold", 16)),
    ]
    if "button_2" in locals():
        buttons.insert(0, sg.Button(button_2, font=("Arial Bold", 16)))

    layout.append(buttons)
    # layout, _, _, _ = add_todays_total(layout)
    return layout


def keep_going(goal, task, time_completed, time_this_morn):
    layout = keep_going_layout(goal, time_completed, task, time_this_morn)

    window = sg.Window(
        "StudyShame.ai",
        layout,
        text_justification="center",
        element_justification="center",
        grab_anywhere=True,
        keep_on_top=True,
    )
    event, values = window.read()
    if event == "-Main Menu-":
        keep_going = True
    elif event in (sg.WINDOW_CLOSED, "Quit"):
        keep_going = False
    elif event == "Keep going":
        keep_going = "Count Up"

    window.close()
    return keep_going


def add_todays_total(layout):
    """adds a total number of completed minutes for
    the day under give_up, keep_going and startup"""

    filename = "_PROGRESS_LOG.json"

    today = datetime.today()
    today_key = str(today.strftime("%y-%m-%d"))
    keys_since_last_sunday = []
    num_days_since_sunday = (today.weekday() + 1) % 7

    for i in range(num_days_since_sunday + 1):
        date = today - timedelta(days=i)
        keys_since_last_sunday.append(str(date.strftime("%y-%m-%d")))

    with open(filename, "r") as file:
        data = json.load(file)

    time_left_since_sunday = 0

    if today_key in data:
        time_completed_today = data[today_key]["completed"]
        goal_today = data[today_key]["goal"]
        for key in keys_since_last_sunday:
            time_left_since_sunday += data[key]["goal"] - data[key]["completed"]

    else:
        time_completed_today = 0
        goal_today = 0

    todays_total_str = (
        f"Today's total: {time_completed_today} min, Today's goal: {goal_today} min, "
        + f"Time left today: {goal_today - time_completed_today} min, "
        + f"Time left this week: {time_left_since_sunday} min"
    )
    todays_total = [
        sg.Text(
            text=todays_total_str,
            font=("Arial", 10),
            size=20,
            expand_x=True,
            expand_y=True,
            justification="center",
            key="-Todays Total-",
        )
    ]
    layout.append(todays_total)
    return layout, todays_total_str, goal_today, time_completed_today


def todays_date():
    today = datetime.today()
    today_int = int(datetime(today.year, today.month, today.day).timestamp())
    today_str = str(today.strftime("%y-%m-%d"))
    return today_int, today_str


def add_progress_plot(layout, num_days):
    with open("_PROGRESS_LOG.json", "r") as file:
        data = json.load(file)

    num_days = min(num_days, len(data.keys()))
    indices = [*range(num_days)]
    indices_in_between = []
    # indices_in_between.append[index-.5,index+.5 for index in indices]
    days = sorted(list(data.keys()))[-(num_days):]
    dates = [day[3:] for day in days]
    completed_times = [data[day]["completed"] for day in days]

    if len(data.keys()) - num_days > 30:
        days_for_moving_avgs = sorted(list(data.keys()))[-(num_days + 30) :]
        completed_times_for_moving_avgs = [
            data[day]["completed"] for day in days_for_moving_avgs
        ]
    else:
        completed_times_for_moving_avgs = completed_times

    goals = [data[day]["goal"] for day in days]
    # goals_doubled = [goal,goal for goal in goals]

    fig = figure.Figure(figsize=(12, 4), dpi=200)
    ax = fig.add_subplot(111)

    achieved_goals, achieved_ids, failed_goals, failed_ids = ([], [], [], [])
    for id, goal, completed in zip(indices, goals, completed_times):
        if goal > completed:
            failed_goals.append(goal)
            failed_ids.append(id)
        # else:
        #     achieved_goals.append(goal)
        #     achieved_ids.append(id)

    # ax.hlines(
    #     achieved_goals,
    #     [id - 0.5 for id in achieved_ids],
    #     [id + 0.5 for id in achieved_ids],
    #     colors="k",
    #     alpha=0.0,
    # )
    ax.hlines(
        failed_goals,
        [id - 0.5 for id in failed_ids],
        [id + 0.5 for id in failed_ids],
        colors="w",
        alpha=1,
        linewidth=2,
        label="Missed Goal",
    )
    outline = ax.step(
        indices, completed_times, "k", where="mid", linewidth=2.0, zorder=0
    )
    completed_bars = ax.bar(
        indices,
        completed_times,
        width=0.85 + 0.15,
        color="#9cff43",
        label="Completed",  # old colour:"#00B7CB"
        # edgecolor="k",
        # edgewidth=1,
    )

    goal_bars = ax.bar(
        indices,
        goals,
        width=0.95 + 0.05,
        color="#898A8A",
        alpha=0.5,
        label="Goal",
    )

    completed_series = pd.Series(completed_times_for_moving_avgs)
    _, todays_total_str, _, _ = add_todays_total([])

    if len(completed_series) >= 35:
        moving_average_7 = (
            completed_series.rolling(window=7).mean().shift(-30)[:num_days]
        )

        ax.plot(
            moving_average_7,
            color="#6fa83e",
            label="7-Day Avg",
            linewidth=2,
            path_effects=[pe.Stroke(linewidth=4, foreground="k"), pe.Normal()],
        )

        moving_average_28 = (
            completed_series.rolling(window=28).mean().shift(-30)[:num_days]
        )
        ax.plot(
            moving_average_28,
            color="#b5cca3",
            label="28-Day Avg",
            linewidth=2,
            path_effects=[pe.Stroke(linewidth=4, foreground="k"), pe.Normal()],
        )

        max_7_day_idx = moving_average_7.idxmax()
        max_7_day = moving_average_7.iloc[max_7_day_idx]
        ax.plot(max_7_day_idx, max_7_day, "k.")

        max_annotation = ax.annotate(
            f"{(max_7_day/60*7):.1f} hr/wk",
            xy=(max_7_day_idx, max_7_day),
            xytext=(max_7_day_idx - len(dates) * 0.075, max_7_day * 1.10),
        )
        max_annotation.set_bbox(dict(facecolor="white", alpha=0.4, edgecolor="white"))
        ax.set_title(
            f"Past 7 Days: {(moving_average_7.iloc[-1]/60*7):.1f} hrs, {todays_total_str}"
        )
    else:
        ax.set_title(f"{todays_total_str}")

    tick_labels = dates[::-7]
    tick_indices = indices[::-7]
    # adding extra tick at the end to ensure space between last bar and end of graph.
    # Otherwise rightmost bar is half cut off.
    tick_labels.append("")
    tick_indices.append(num_days + 1)

    ax.set_xlim(0.0, num_days + 1.0)
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, rotation=90)
    ax.tick_params(right=True, labelright=True)
    ax.set_facecolor("#353535")
    fig.set_facecolor("#6C6C6C")
    ax.legend(loc="upper left", fontsize="8", facecolor="#6C6C6C")

    loc = plticker.MultipleLocator(base=60.0)
    ax.yaxis.set_major_locator(loc)

    fig.tight_layout()
    ax.grid(alpha=0.3, linewidth=0.5)

    plot_path = "plot.png"
    plot_path_copy = (
        "plot_copies/1.png"  # so Windows background slideshow refreshs image
    )
    plot_path_copy2 = "plot_copies/2.png"
    plot_path_copy3 = "plot_copies/3.png"
    fig.savefig(plot_path)
    try:
        shutil.copyfile(plot_path, plot_path_copy)
        shutil.copyfile(plot_path, plot_path_copy2)
        shutil.copyfile(plot_path, plot_path_copy3)
        shutil.copyfile(plot_path_copy, plot_path)
    except:
        "Failed to make the plots. idk sometimes there's issues w this sorry."

    rescaled_plot = cv_rescale(plot_path, plot_path, scale=0.5)

    layout.append([sg.Image(rescaled_plot)])
    return layout


def set_theme():
    my_theme = {
        "BACKGROUND": "#2b2b2b",
        "TEXT": "#Faffef",
        "INPUT": "#709053",  # "#c7e78b",
        "TEXT_INPUT": "#000000",
        "SCROLL": "#c7e78b",
        "BUTTON": ("#Faffef", "#234f00"),  # "#709053"
        "PROGRESS": ("#01826B", "#D0D0D0"),
        "BORDER": 5,
        "SLIDER_DEPTH": 0,
        "PROGRESS_DEPTH": 0,
    }

    # Add your dictionary to the PySimpleGUI themes
    sg.theme_add_new("My Theme", my_theme)
    sg.theme("My Theme")

    return


def main():
    set_theme()

    while True:
        (
            task,
            goal,
            interval,
            pictures_allowed,
            abort,
            streaks_bool,
            secret_button_allowed,
            time_this_morn,
        ) = startup_gui()
        if abort:
            return

        time_completed, streak_minutes = countdown_and_checkins(
            task,
            goal,
            interval,
            pictures_allowed,
            streaks_bool,
            secret_button_allowed,
            time_this_morn,
        )

        keepGoing = keep_going(goal, task, time_completed, time_this_morn)
        if keepGoing == "Count Up":
            time_completed = countup_and_checkins(
                task,
                goal,
                interval,
                pictures_allowed,
                streak_minutes,
                streaks_bool,
                secret_button_allowed,
                time_this_morn,
            )
            if not keep_going(goal, task, time_completed, time_this_morn):
                return

        elif keepGoing == True:
            continue
        else:
            return


if __name__ == "__main__":
    main()

    # take_photo()
    # checkin("f", True)
    # keep_going(21, "werk", 10)
    # clear_images()
    # todays_date()
    # update_log(60, 4)
    # countup_and_checkins("nothin", 60, 10)
    # give_up(False)
