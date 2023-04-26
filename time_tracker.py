import csv
from typing import List, Dict, Tuple, Any, Union, Optional
import os.path
import datetime



# mode = work or study
mode = None


def initialise_work_study_log_file():
    try:
        with open("work_study_log.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Work or Study'])
        file.close()
    except:
        raise FileNotFoundError(f"Could not create work_study_log.csv")
    return

def initialise_task_tracker_files(mode):
    try:
        with open(f"{mode}_task_tracker.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Task Description', 'Predicted Time', 'Actual Time', 'Start Time', 'End Time', 'Comments', 'Diff', 'Status', 'Work or Study'])
        file.close()
    except:
        raise FileNotFoundError(f"Could not create {mode}_task_tracker.csv")
    return

def initialise_time_log_files(mode):
    try:
        with open(f"{mode}_time_log.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time Stamp', 'Shift Start or End'])
        file.close()
    except:
        raise FileNotFoundError(f"Could not create {mode}_time_log.csv")
    return
    

def set_mode():
    global mode
    if _check_clocked_in():
        file_rows = []
        with open("work_study_log.csv", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                file_rows.append(row)
        file.close()
        mode = file_rows[-1][0]
    else:
        mode = None
    return

    


def read_task_tracker(mode):
    file_rows = []
    try:
        with open(f"{mode}_task_tracker.csv", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                file_rows.append(row)
        file.close()
        return file_rows
    except:
        raise FileNotFoundError("Could not find task_tracker file")
    
def read_time_log(mode):
    file_rows = []
    try:
        with open(f"{mode}_time_log.csv", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                file_rows.append(row)
        file.close()
        return file_rows
    except:
        raise FileNotFoundError("Could not find time_log file")


# Returns the last line in time_log.csv or False
def _check_clocked_in():
    for i in ['work', 'study']:
        time_log_file: List[List[str]] = read_time_log(i)
        if time_log_file[-1][1] == 'Start':
            return i
    return False

def check_clocked_in():
    if _check_clocked_in():
        print("You are clocked in.")
    else:
        print("You are not clocked in.")
    

def clock_in():
    global mode
    if _check_clocked_in():
        print("You are already clocked in. Please clock out before clocking in again.")
        return
    
     # Get  'Work or Study' input
    work_or_study: str = ''
    for i in ["work", "study"]:
        task_tracker_rows = read_task_tracker(i)
        if not task_tracker_rows[-1][5]:
            work_or_study = task_tracker_rows[-1][8]

            break
    if not work_or_study:    
        while True:
            user_input = input("Are you working or studying (0: Work, 1: Study)?: ")
            if user_input == '0':
                work_or_study = 'Work'
                break
            elif user_input == '1':
                work_or_study = 'Study'
                break
            else:
                print("Please enter a valid input (0 or 1).")
                continue
    mode = work_or_study
    print(f"Mode set to {mode}.")
    
    with open("work_study_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([mode.lower()])
    file.close()
    

    # Get 'Time Stamp' input
    time_string: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(f"{work_or_study}_time_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time_string, 'Start'])
    file.close()

    print("Clocked in.")

    mode = work_or_study
    return


def clock_out():
    global mode
    clocked_in = _check_clocked_in()
    if not clocked_in:
        print("You are not clocked in. Please clock in before clocking out again.")
        return

    # Get 'Time Stamp' input
    time_string: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(f"{mode}_time_log.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time_string, 'End'])
    file.close()

    print("Clocked out.")
    
    mode = None
    return







def add_new_task():
    global mode
    clocked_in = _check_clocked_in()
    if not clocked_in:
        print("You are not clocked in. Please clock in to add a new task.")
        return
    
    task_description = input("Enter task description: ")

    while True:
        predicted_time = input("Enter predicted time (in minutes): ")
        try:
            # TODO: check if valid input by converting to integer and back to string
            break
        except:
            break
             
    start_time: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # read work_study_log and append last isntance to end of row

    task_row: List[str] = [task_description, predicted_time, '', start_time, '', '', '', '', mode]
    with open(f"{mode}_task_tracker.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(task_row)
    file.close()
    print(f"New task added: {task_row}")
    return


# log has to be a clock out
def find_next_log(time_log_file, comparison_time):
    for i in range(len(time_log_file))[::-1]:
        if datetime.datetime.strptime(time_log_file[i][0], "%Y-%m-%d %H:%M:%S") >= comparison_time:
            continue
        elif i + 1 > (len(time_log_file) - 1):
            return None
        else:
            return i + 1
        
def get_log_slice(start_time):
    global mode
    time_log_file: List[List[str]] = read_time_log(mode)

    first_log_index = find_next_log(time_log_file, start_time)
    if not first_log_index:
        return None

    return time_log_file[first_log_index : ]
    
       

def get_task_actual_time(current_task, end_time):
    start_time = datetime.datetime.strptime(current_task[3], "%Y-%m-%d %H:%M:%S")
    time_logs = get_log_slice(start_time)

    if not time_logs:
        return (end_time - start_time).seconds / 60
    
    task_total_time = 0

    # first clock out
    task_total_time = (datetime.datetime.strptime(time_logs[0][0], "%Y-%m-%d %H:%M:%S") - start_time).seconds / 60
    time_logs = time_logs[1 : ]

    # last clock in
    task_total_time = (end_time - datetime.datetime.strptime(time_logs[-1][0], "%Y-%m-%d %H:%M:%S")).seconds / 60
    time_logs = time_logs[ : -1]

    while True:
        if len(time_logs) > 0:
            task_total_time = (datetime.datetime.strptime(time_logs[1][0], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(time_logs[0][0], "%Y-%m-%d %H:%M:%S")).seconds / 60
            time_logs = time_logs[2 : ]
        else:
            break
    print(task_total_time)
    return task_total_time

 
def update_current_task(task_tracker_file, current_task):
    global mode
    try:
        with open(f"{mode}_task_tracker.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in task_tracker_file[:-1]:
                writer.writerow(row)
            writer.writerow(current_task)
        file.close()
    except:
        raise FileNotFoundError(f"Could not create {mode}_task_tracker.csv")
    return

def cancel_task():
    _end_current_task('cancelled')
    return

def complete_task():
    _end_current_task('completed')
    return
# {
#     0: 'Task Description', 
#     1: 'Predicted Time',
#     2: 'Actual Time',
#     3: 'Start Time',
#     4: 'End Time',
#     5: 'Comments',
#     6: 'Diff', 
#     7: 'Status'
# }
def _end_current_task(status):
    if not _check_clocked_in():
        print("You are not clocked in. Please clock in to complete a task.")
        return


    global mode
    task_tracker_file: List[List[str]] = read_task_tracker(mode)
    current_task: List[str] = task_tracker_file[-1]

    if current_task[5]:
        print("You do not currently have an open task. Please call add_new_task() to create a task.")
        return
    
    # Get End Time input
    end_time = datetime.datetime.now()
    current_task[4] = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Get Actual Time input
    time_of_task = get_task_actual_time(current_task, end_time)
    current_task[2] = time_of_task

    # Get Comments input
    current_task[5] = input("Please enter a comment: ")

    # Get Diff input
    current_task[6] = str(time_of_task - float(current_task[1]))

    current_task[7] = status

    update_current_task(task_tracker_file, current_task)
    print(current_task)



if not os.path.exists('work_task_tracker.csv'):
    initialise_task_tracker_files('work')
if not os.path.exists('study_task_tracker.csv'):
    initialise_task_tracker_files('study')    
if not os.path.exists('work_time_log.csv'):
    initialise_time_log_files('work')
if not os.path.exists('study_time_log.csv'):
    initialise_time_log_files('study')
if not os.path.exists('work_study_log.csv'):
    initialise_work_study_log_file()
    print("Files created\n\n Please start your day by calling clock_in() and enter a new task by calling add_new_task()\n\n")


set_mode()
list_of_functions: List[str] = ['clock_in()', 'clock_out()', 'add_new_task()', 'cancel_task()', 'complete_task()', 'add_comment()', 'finish_task()', 'cancel_task()']
print("Functions:")
for function in list_of_functions:
    print(f"    {function}")
while True:
    user_input = input("Enter a function: ")
    try:
        list_of_functions.index(user_input)
        exec(f"{user_input}")
    except ValueError:
        print("Please enter a valid function name.")
        continue
