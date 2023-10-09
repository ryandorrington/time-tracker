from json import load, dump
from typing import List, Dict
import os.path
import datetime


def _read_file(file_name):
    with open(f"{file_name}.json", 'r', encoding='utf-8') as f:
        data = load(f)
    return data


def _write_file(file_name, data):
    data = [data]
    if os.path.exists(f"{file_name}.json"):
        current_data = _read_file(file_name)
        data = current_data + data

    with open(f"{file_name}.json", 'w', encoding='utf-8') as f:
        dump(data, f)


def read_task_tracker(shift_type):
    if not os.path.exists(f"{shift_type}_task_tracker.json"):
        return []
    try:
        return _read_file(f"{shift_type}_task_tracker")
    except Exception as e:
        raise  Exception(f"Could not open task_tracker file: {e}")


def read_time_log(shift_type):
    if not os.path.exists(f"{shift_type}_time_log.json"):
        return []
    try:
        return _read_file(f"{shift_type}_time_log")
    except Exception as e:
        raise Exception(f"Could not open time_log file: {e}")


def _check_clocked_in():
    for shift_type in ['tinyplan']:
        time_log_file: List = read_time_log(shift_type)
        if time_log_file and time_log_file[-1]["shift_position"] == 'start':
            return shift_type
    return False


def check_clocked_in():
    if _check_clocked_in():
        print("You are clocked in.")
    else:
        print("You are not clocked in.")


def _check_active_task(shift_type):
    task_tracker_data: List = read_task_tracker(shift_type)
    if task_tracker_data and not task_tracker_data[-1]["end_time"]:
        return True
    return False


def clock_in():
    if _check_clocked_in():
        print("You are already clocked in. Please clock out before clocking in again.")
        return

    # Get 'shift_type' input
    shift_type: str = "tinyplan"

    while True:
        input("Focus on a point on your keyboard for 30 seconds")
        user_input = input(
            "Are you motivated (1: Yes, 0: No)?: ")
        if user_input == '0':
            input("Spend 3 minutes visualising what life will be like if you fail.")
            break
        elif user_input == '1':
            input("Spend 3 minutes visualising what life will be like when you are an employee at tinycorp.")
            break
        else:
            print("Please enter a valid input (0 or 1).")
            continue

    # Get 'Time Stamp' input
    time_stamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        _write_file(f"{shift_type}_time_log", {
                   "time_stamp": time_stamp, "shift_position": "start"})
    except Exception as e:
        raise Exception(f"Could not write to time_log file: {e}")

    print("Clocked in.")
    return


def clock_out():
    clocked_in = _check_clocked_in()
    if not clocked_in:
        print("You are not clocked in. Please clock in before clocking out again.")
        return

    time_string: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        _write_file(f"{clocked_in}_time_log", {
                   "time_stamp": time_string, "shift_position": "end"})
    except Exception as e:
        raise Exception(f"Could not write to time_log file: {e}")

    print("Clocked out.")
    return


def add_new_task():
    shift_type = _check_clocked_in()
    if not shift_type:
        print("You are not clocked in. Please clock in to add a new task.")
        return

    if _check_active_task(shift_type):
        print("You already have an active task. Please complete the task before adding a new one.")
        return

    task_description = input("Enter task description: ")

    while True:
        predicted_time = input("Enter predicted time (in minutes): ")
        try:
            predicted_time = float(predicted_time)
            break
        except:
            print("Please enter a valid number.")
            continue

    start_time: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    task: Dict = {
        "task_description": task_description,
        "predicted_time": predicted_time,
        "start_time": start_time,
        "shift_type": shift_type,
        "actual_time": None,
        "end_time": None,
        "comments": None,
        "level_of_focus": None,
        "time_difference": None,
        "status": None,
    }
    try:
        _write_file(f"{shift_type}_task_tracker", task)
    except Exception as e:
        raise Exception(f"Could not write to task_tracker file: {e}")

    print(f"New task added: {task}")
    return

# log has to be a clock out


def _find_next_log(time_log_data, comparison_time):
    for i in range(len(time_log_data))[::-1]:
        if datetime.datetime.strptime(time_log_data[i]["time_stamp"], "%Y-%m-%d %H:%M:%S") >= comparison_time:
            continue
        elif i + 1 > (len(time_log_data) - 1):
            return None
        else:
            return i + 1


def _get_log_slice(start_time, shift_type):
    time_log_data: List = read_time_log(shift_type)

    first_log_index = _find_next_log(time_log_data, start_time)
    if not first_log_index:
        return None

    return time_log_data[first_log_index:]


def _get_task_actual_time(current_task, end_time, shift_type):
    start_time = datetime.datetime.strptime(
        current_task["start_time"], "%Y-%m-%d %H:%M:%S")
    time_logs = _get_log_slice(start_time, shift_type)

    if not time_logs:
        return (end_time - start_time).seconds / 60

    task_total_time = 0

    # first clock out
    task_total_time = (datetime.datetime.strptime(
        time_logs[0]["time_stamp"], "%Y-%m-%d %H:%M:%S") - start_time).seconds / 60
    time_logs = time_logs[1:]

    # last clock in
    task_total_time = (end_time - datetime.datetime.strptime(
        time_logs[-1]["time_stamp"], "%Y-%m-%d %H:%M:%S")).seconds / 60
    time_logs = time_logs[: -1]

    while True:
        if len(time_logs) > 0:
            task_total_time = (datetime.datetime.strptime(time_logs[1]["time_stamp"], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(
                time_logs[0]["time_stamp"], "%Y-%m-%d %H:%M:%S")).seconds / 60
            time_logs = time_logs[2:]
        else:
            break

    return task_total_time


def _update_current_task(updated_task_tracker_data, shift_type):
    try:
        with open(f"{shift_type}_task_tracker.json", 'w', encoding='utf-8') as f:
            dump(updated_task_tracker_data, f)
    except Exception as e:
        raise Exception(f"Could not update {shift_type}_task_tracker file: {e}")


def _end_current_task(status):
    shift_type = _check_clocked_in()

    if not shift_type:
        print("You are not clocked in. Please clock in to complete a task.")
        return

    task_tracker_data: List = read_task_tracker(shift_type)

    if not task_tracker_data:
        print("You do not currently have an open task. Please call add_new_task() to create a task.")
        return

    current_task: Dict = task_tracker_data[-1]

    if current_task["end_time"]:
        print("You do not currently have an open task. Please call add_new_task() to create a task.")
        return

    # Get 'end_time' input
    end_time = datetime.datetime.now()
    current_task["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Get 'actual_time' input
    time_of_task = _get_task_actual_time(current_task, end_time, shift_type)
    current_task["actual_time"] = time_of_task

    # Get 'comments' input
    current_task["comments"] = input("Please enter a comment: ")

    # Get 'level_of_focus' input
    current_task["level_of_focus"] = input("Please enter your level of focus (0-9): ")

    # Get 'time_difference' input
    current_task["time_difference"] = time_of_task - \
        current_task["predicted_time"]

    current_task["status"] = status

    updated_task_tracker_data = task_tracker_data[:-1] + [current_task]
    _update_current_task(updated_task_tracker_data, shift_type)

    print(f"Task updated: {current_task}")
    return


def cancel_task():
    _end_current_task('cancelled')
    return


def complete_task():
    _end_current_task('completed')
    return


def help():
    list_of_functions: List[str] = [
        'clock_in()',
        'clock_out()',
        'check_clocked_in()',
        'add_new_task()',
        'cancel_task()',
        'complete_task()',
        'read_task_tracker()',
        'read_time_log()'
    ]
    print("Functions:")
    for function in list_of_functions:
        print(f"    {function}")
