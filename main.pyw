'''
Description: The accountability partner for those who have no friends.

To install:

cd "C:\Users\Surface Pro 6\Documents\GitHub\Focus-Pal"

pyinstaller --onefile --name StudyShame --distpath "C:\Users\Surface Pro 6\Documents\GitHub\Focus-Pal\EXE" main.pyw

'''

import numpy as np
import time
from functools import partial
from datetime import datetime, timedelta
import os
import glob
import json

import cv2 as cv # pip install opencv-python / pip install opencv-contrib-python
import matplotlib # pip install matplotlib
import PySimpleGUI as sg  # pip install pysimplegui
from PIL import ImageGrab #pip install PIL


def cv_rescale(original_path, resized_path, scale=0.5):
    frame = cv.imread(original_path)
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    resized_frame = cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)
    cv.imwrite(resized_path, resized_frame)
    return resized_path


def clear_images():
    confirmation = input("Are you sure you want to delete all your images? (type y/n): ")
    if confirmation == 'y':
        files = glob.glob(pathname="**/*.png", recursive=True)
        for f in files:
            print(f"Now deleting: {f}")
            os.remove(f)
    else: print("Ok, your images will remain.")
    return


def convert_to_int(string):
    if string.isdigit():
        return int(string)
    else:
        sg.popup_error(
            f'"{string}" is not a valid integer.',
            keep_on_top=True,
        )
        return None


def startup_gui():
    text_background_color = "#477320"
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
            sg.Text("What will you be working on?:", font=("Arial", 18)),
            sg.Input(
                key="Task",
                font=("Arial", 24),
                size=(20, 20),
                default_text="serious important work",
            ),
        ],
        [
            sg.Text("For how long?:", font=("Arial", 18)),
            sg.Input(
                key="Duration hr", font=("Arial", 24), size=(5, 5), default_text="8"
            ),
            sg.Text("hours", font=("Arial", 18)),
            sg.Input(
                key="Duration min", font=("Arial", 24), size=(5, 5), default_text="0"
            ),
            sg.Text("mins", font=("Arial", 18)),
        ],
        [
            sg.Text("How often should I check in?: every", font=("Arial", 18)),
            sg.Input(
                key="Interval", font=("Arial", 24), size=(5, 5), default_text="10"
            ),
            sg.Text("mins", font=("Arial", 18)),
        ],
        [
            sg.Text("Do you want photo evidence?:", font=("Arial", 12)),
            sg.Checkbox(
                "",
                default=False,
                checkbox_color=text_background_color,
                key="-Pictures Allowed-",
            ),
        ],
        [sg.Button("Let's GO!!!", font=("Arial Bold", 32)), sg.Exit()],
    ]

    layout = add_todays_total(layout)

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
            return None, None, None, None, abort
        if event == "Let's GO!!!":
            abort = False
            task = values["Task"]
            if not task:
                task = "focused work"
            duration_hr = values["Duration hr"]
            duration_min = values["Duration min"]
            interval = values["Interval"]
            pictures_allowed = values["-Pictures Allowed-"]

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

            break

    window.close()
    return task, duration, interval, pictures_allowed, abort


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


def give_up(goal_already_achieved):
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
    ]

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
    window.close()
    return abort


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
    goal_str = "Goal: 0:00"

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
        [
            sg.Button(
                "Quit",
                font=("Arial Bold", 8),
                border_width=0,
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
    )

    return timer_window


def checkin_times(interval):
    # generates a set of times that are semi-random. This is to
    # ensure that there are roughly every X minutes there will
    # be a checkin while maintaining unpredictibility

    max_num_minutes = 60 * 24 * 7
    checkin_times = [*range(interval, max_num_minutes, interval)]
    std_dev = interval / 2
    noisy_checkin_times = add_noise(checkin_times, std_dev)
    return noisy_checkin_times


def countup_and_checkins(task, goal, interval, pictures_allowed):
    num_millisecs = 1000  # decrease to speed up

    time_completed = goal
    time_elapsed = goal
    time_since_last_checkin = 0

    checkins = checkin_times(interval)

    timer_window = countup_window()
    event, values = timer_window.read(timeout=0)

    while True:
        if its_bedtime():
            update_log(goal, time_since_last_checkin)
            timer_window.close()
            return time_completed

        time_completed_str = timedelta(minutes=time_completed + time_since_last_checkin)
        time_completed_str = str(time_completed_str)[:-3]
        goal_str = timedelta(minutes=goal)
        goal_str = "Goal: " + str(goal_str)[:-3]
        timer_window["-Completed-"].update(time_completed_str)
        timer_window["-Goal-"].update(goal_str)

        timer_window.refresh()

        event, values = timer_window.read(timeout=60 * num_millisecs)

        if event == "Quit":
            if give_up(True):
                update_log(goal, time_since_last_checkin)
                timer_window.close()
                return time_completed
            else:
                continue

        time_elapsed += 1
        time_since_last_checkin += 1

        if time_elapsed in checkins:
            is_on_task = checkin(task, pictures_allowed)
            if not is_on_task:
                time_since_last_checkin -= interval
            update_log(goal, time_since_last_checkin)
            time_completed += time_since_last_checkin
            time_since_last_checkin = 0


def countdown_and_checkins(task, goal, interval, pictures_allowed):
    num_millisecs = 1000  # decrease to speed up
    time_elapsed = 0
    time_completed = 0
    time_remaining = goal
    time_since_last_checkin = 0

    timer_window = countdown_window(time_remaining)

    checkins = checkin_times(interval)

    while (time_completed + time_since_last_checkin) < goal:
        if its_bedtime():
            update_log(goal, time_since_last_checkin)
            timer_window.close()
            return time_completed

        event, values = timer_window.read(timeout=60 * num_millisecs)

        if event == "Give up":
            if give_up(False):
                timer_window.close()
                return time_completed
            else:
                continue

        time_since_last_checkin += 1
        time_elapsed += 1

        if time_elapsed in checkins:
            is_on_task = checkin(task, pictures_allowed)
            if not is_on_task:
                time_since_last_checkin -= interval
            update_log(goal, time_since_last_checkin)
            time_completed += time_since_last_checkin
            time_since_last_checkin = 0

        time_remaining = goal - time_completed - time_since_last_checkin

        completion_time, time_remaining_string = update_countdown_times(time_remaining)
        timer_window["-Remaining-"].update(time_remaining_string)
        timer_window["-Completion-"].update(completion_time)

        timer_window.refresh()

    timer_window.close()
    time_completed = goal
    update_log(goal, time_since_last_checkin)

    return time_completed


def update_countdown_times(time_remaining):
    current_time = datetime.now()
    time_to_add = timedelta(minutes=time_remaining)
    completion_time = current_time + time_to_add
    completion_time = str(completion_time.strftime("%I:%M %p"))
    time_remaining_string = str(time_to_add)[:-3]
    return completion_time, time_remaining_string


def its_bedtime():
    bedtime = 21 * 60 + 30  # 9:30PM
    # floor divide time for seconds since midnight, -5hrs for CST
    now = (time.time() / 60 - 5 * 60) % (24 * 60)
    return now >= bedtime


def update_log(goal, completed):
    today = datetime.now().date()
    today_key = str(today.strftime("%y-%m-%d"))

    # Define a dictionary
    new_entry = {today_key: {"goal": goal, "completed": completed}}

    filename = "logbook.json"

    # 1. Read the JSON file
    with open(filename, "r") as file:
        data = json.load(file)

    # 2. Add the new entry to the dictionary only if the key does not exist
    if today_key not in data:
        data = fill_empty_days_in_log(data, today)
        data.update(new_entry)
    else:
        data[today_key]["completed"] += completed

    # 3. Write the updated JSON data back to the file
    with open(filename, "w") as file:
        json.dump(data, file)

    return


def fill_empty_days_in_log(data, today):
    # updating previous days with 0 completed if inactive
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


def keep_going_layout(goal, time_completed, task):
    if its_bedtime():
        header = "Go to bed."
        subheader_1 = f"It's 9:30PM. You accomplished {time_completed} out of {goal} minutes of {task}. But I'm cutting you off."
        button_1 = "Let's try again tomorrow"
    elif time_completed < goal:
        header = "You failed:("
        subheader_1 = f"I believed in you but you only did {time_completed} out of the {goal} minutes of {task} that you promised."
        button_1 = "I'm sorry, lemme try again"
    elif time_completed == goal:
        header = "You did it!🥳"
        subheader_1 = (
            f"You completed {time_completed} minutes of {task}! I'm very proud."
        )
        button_1 = "Keep going"
    else:
        header = "Nice job!🥳"
        subheader_1 = f"You completed {time_completed} minutes of {task}! I'm speechless. You are killing the game."
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
    layout.append(
        [
            sg.Button(button_1, font=("Arial Bold", 16), key="-Button 1-"),
            sg.Button("Quit", font=("Arial Bold", 16)),
        ]
    )
    layout = add_todays_total(layout)
    return layout


def keep_going(goal, task, time_completed):
    layout = keep_going_layout(goal, time_completed, task)

    window = sg.Window(
        "StudyShame.ai",
        layout,
        text_justification="center",
        element_justification="center",
        grab_anywhere=True,
        keep_on_top=True,
    )
    event, values = window.read()
    if event == "-Button 1-":
        keep_going = True
    if event in (sg.WINDOW_CLOSED, "Quit"):
        keep_going = False
    window.close()
    return keep_going


def add_todays_total(layout):
    """adds a total number of completed minutes for
    the day under give_up, keep_going and startup"""

    filename = "logbook.json"

    today = datetime.now().date()
    today_key = str(today.strftime("%y-%m-%d"))

    # 1. Read the JSON file
    with open(filename, "r") as file:
        data = json.load(file)

    if today_key in data:
        time_completed_today = data[today_key]["completed"]
        goal_today = data[today_key]["goal"]
    else:
        time_completed_today = 0
        goal_today = 0

    todays_total_str = f"Today's total: {time_completed_today} min, Today's goal: {goal_today} min, Time left: {goal_today - time_completed_today} min"
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
    return layout


def todays_date():
    today = datetime.now().date()
    today_int = int(datetime(today.year, today.month, today.day).timestamp())
    today_str = str(today.strftime("%y-%m-%d"))
    return today_int, today_str


def add_progress_plot(layout, num_days):
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    matplotlib.use("TkAgg")

    with open("logbook.json", "r") as file:
        data = json.load(file)

    num_days = min(num_days, len(data.keys()))
    indices = [*range(num_days)]

    # Prepare the data for the bar chart
    days = sorted(list(data.keys()))[-num_days:]
    dates = [day[3:] for day in days]
    completed_times = [data[day]["completed"] for day in days]
    goals = [data[day]["goal"] for day in days]

    # Create the bar chart
    fig = matplotlib.figure.Figure(figsize=(12, 4), dpi=100)
    ax = fig.add_subplot(111)

    opacity = 0.7

    completed_bars = ax.bar(
        indices,
        completed_times,
        width=0.85 + 0.15,
        color="#9cff43",
        label="Completed",  # old colour:"#00B7CB"
    )
    goal_bars = ax.bar(
        indices,
        goals,
        width=0.95 + 0.05,
        color="#898A8A",
        alpha=opacity,
        label="Goal",
    )

    tick_labels = dates[::-7]
    tick_indices = indices[::-7]
    # adding extra tick at the end to ensure space between last bar and end of graph.
    # Otherwise rightmost bar is half cut off.
    tick_labels.append("")
    tick_indices.append(num_days + 1)

    ax.set_xlim(0.0, num_days + 1.0)
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, rotation=90)
    ax.set_facecolor("#414141")
    fig.set_facecolor("#6C6C6C")
    ax.legend(loc="upper left", facecolor="#6C6C6C")
    ax.set_title("Your Progress")
    fig.tight_layout()

    plot_path = "chart_image.png"

    fig.savefig(plot_path)

    rescaled_plot = cv_rescale(plot_path, plot_path, scale=1)

    layout.append([sg.Image(rescaled_plot)])

    print

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

    # Switch your theme to use the newly added one. You can add spaces to make it more readable
    sg.theme("My Theme")

    # Call a popup to show what the theme looks like
    # sg.popup_get_text("This how the MyNewTheme custom theme looks")

    return


def main():
    set_theme()

    while True:
        task, goal, interval, pictures_allowed, abort = startup_gui()
        if abort:
            return

        time_completed = countdown_and_checkins(task, goal, interval, pictures_allowed)

        if keep_going(goal, task, time_completed):
            if time_completed >= goal:
                time_completed = countup_and_checkins(
                    task, goal, interval, pictures_allowed
                )
                if not keep_going(goal, task, time_completed):
                    return
            else:
                continue
        else:
            return


if __name__ == "__main__":
    main()

    # take_photo()
    # checkin("f", True)
    # keep_going(21, "fuckshit", 10)
    # clear_images()
    # todays_date()
    # update_log(60, 4)
    # countup_and_checkins("nothin", 60, 10)
    # give_up(False)
