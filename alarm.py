"""
This module is responsible for all alarm functionality. The user can
add new alarms with the two optional options. First, they can select
days of the week for the alarm to repeat on. Secondly, an alarm label
which is displayed in notifications and read out to the user when the
alarm goes off along with an alarm sound. The alarm is also logged when
it goes off along with the appropriate data. The user edit the time of
a regular alarm or repeating alarm once it's been set and delete
alarms.
"""
from threading import Thread
import typing
import sched
import time
import datetime
import json
from flask import request
from pygame import mixer
import schedule
from notifications import new_notification
from formatted_log import log_info, log_warning, log_error
from circular_queue import CircularQueue
from text_to_speech import tts

def fetch_new_alarm():
    """
    This function fetches the alarm information entered by the user
    when they press the 'Add' button. If the user has entered a time
    (as that's the only required data), the information is formatted
    to a dictionary and returned to the add_alarm() function.
    """
    alarm_time = request.args.get('alarm_time')
    day_0 = request.args.get('day_0')
    day_1 = request.args.get('day_1')
    day_2 = request.args.get('day_2')
    day_3 = request.args.get('day_3')
    day_4 = request.args.get('day_4')
    day_5 = request.args.get('day_5')
    day_6 = request.args.get('day_6')
    label = request.args.get('label')

    # Action only taken if the user entered a time which is the only
    # mandatory argument.
    if alarm_time:
        alarm = ({'alarm_time': alarm_time, 'day_0': day_0,
                  'day_1': day_1, 'day_2': day_2,
                  'day_3': day_3, 'day_4': day_4,
                  'day_5': day_5, 'day_6': day_6,
                  'label': label})
        return add_alarm(alarm)

def add_alarm(alarm: dict) -> list:
    """
    This function reads all existing alarms from the json file, appends
    each one to a list, appends the new alarms to the same list and
    writes that list to the same json file. The start alarm thread is
    then reset.

    Arguments:
    :param alarm: a dictionary containing the new alarm information.
    """
    with open('alarms.json', 'r') as alarms_file:
        # Attempts to load contents of the file. If it's empty, an
        # empty list is defined and a warning is sent to the log file.
        try:
            alarms_object = json.load(alarms_file)
        except Exception as error:
            alarms_object = []
            log_warning(error)

    alarms_object.append(alarm.copy())

    with open('alarms.json', 'w') as alarms_file:
        json.dump(alarms_object, alarms_file, indent=2)

    # Start alarm thread reset as the alarms json has changed.
    alarm_thread = Thread(target=start_alarm, args=(), daemon=True)
    alarm_thread.start()

def get_alarms() -> dict:
    """
    This function reads the alarm json file and saves its contents to
    a dictionary.
    """
    with open('alarms.json', 'r') as alarms_file:
        try:
            alarm_list = json.load(alarms_file)
        except Exception as error:
            alarm_list = []
            log_warning(error)
    return alarm_list

def update_alarm() -> None:
    """
    This function allows the user to edit the time of an alarm. The
    alarm time to be edited and the new alarm time is fetched as an
    argument using the request module. If the user has entered a new
    time, the existing alarms are saved to a dict 'alarms_object'.
    The for loop iterates through each alarm, if an alarm is found
    with the old time, that time is replaced with the new time. The
    edited dict is then written to the json file and the start alarm
    thread is reset.
    """
    new_time = request.args.get('newtime')
    old_time = request.args.get('oldtime')

    # Action only taken if the user entered a new time.
    if new_time:
        with open('alarms.json', 'r') as alarms_file:
            try:
                alarm_list = json.load(alarms_file)
            except Exception as error:
                alarm_list = []
                log_warning(error)

            for alarm in alarms_object:
                if alarm['alarm_time'] == old_time:
                    alarm['alarm_time'] = new_time

        with open('alarms.json', 'w') as alarms_file:
            json.dump(alarms_object, alarms_file, indent=2)

        # Start alarm thread reset as the alarms json has changed.
        thread = Thread(target=start_alarm, args=(), daemon=True)
        thread.start()

def delete_alarm() -> None:
    """
    This function allows the user to delete an alarm. The alarm time to
    be deleted is fetched using the request module. The existing alarms
    are saved to a dict 'alarms_object'. The for loop iterates through
    each alarm. If an alarm time is found that is not equal to the time
    the user has requested to delete, that alarm object is appended to
    a new list 'new_alarm_objects'. The edited list of alarms is then
    written to the json file and the start alarm thread is reset.
    """
    alarm_time = request.args.get('alarm_time')
    new_alarm_objects = []

    with open('alarms.json', 'r') as alarms_file:
        try:
            alarm_list = json.load(alarms_file)
        except Exception as error:
            alarm_list = []
            log_warning(error)

        for alarm in alarms_object:
            if alarm['alarm_time'] != alarm_time:
                new_alarm_objects.append(alarm)

    with open('alarms.json', 'w') as alarms_file:
        json.dump(new_alarm_objects, alarms_file, indent=2)

    # Start alarm thread reset as the alarms json has changed.
    thread = Thread(target=start_alarm, args=(), daemon=True)
    thread.start()

def start_alarm() -> None:
    """
    This function is responsible for setting timers for each alarm.
    For each alarm, the difference in time between now and the time of
    the alarm is calculated using epoch and adds each alarm to the
    schedular. This function is run on a separate thread each time the
    user loads the program, edits or deletes an alarm.
    """
    alarm_schedule = sched.scheduler(time.time, time.sleep)
    EPOCH = datetime.datetime(1970, 1, 1)
    DAY = 86400

    with open('alarms.json', 'r') as alarms_file:
        try:
            alarm_list = json.load(alarms_file)
        except Exception as error:
            alarm_list = []
            log_warning(error)

    for alarm in alarms_object:
        counter = 0
        alarm_queue = CircularQueue()
        for day in range(6):
            if alarm['day_'+str(day)]:
                alarm_queue.enqueue(alarm['day_'+str(day)])
                counter += 1
        if counter != 0:
            # Alarm is a repeating alarm.
            delta_time, alarm_time = sched_next_repeat(alarm)
        else:
            # Alarm is a standard, one off alarm.
            # Date and time the alarm is set to go off.
            alarm_time = datetime.datetime.strptime \
            (str(datetime.date.today()) + '-' +
             alarm['alarm_time'], '%Y-%m-%d-%H:%M')
            # Time in seconds to when the alarm is due to go off.
            delta_time = int((alarm_time - EPOCH).total_seconds()) \
            - time.time()
            # If the alarm is set at a time that is eariler than the
            # time of the alarm, add 24 hours to the time.
            if delta_time < 0:
                delta_time += DAY

        # Adds alarm to the scheduler.
        alarm_schedule.enter(delta_time, 1, alarm_end,
                             (alarm_time, alarm))

    alarm_schedule.run()
    schedule.run_pending()

def alarm_end(alarm_time: datetime.datetime, alarm: dict) -> None:
    """
    This function runs when an alarm has gone off. If it is a repeating
    alarm, the start alarm thread is reset with the different day that
    the alarm is going to go off on. The notification and log
    dictionaries are created including the necessary alarm data. The
    alarm sound is played as well as the alarm label being read out to
    the user.
    """

    # If it's a repeat alarm, calculate the next time the alarm needs
    # to go off again.
    if alarm['day_0'] or alarm['day_1'] or alarm['day_2'] or \
    alarm['day_3'] or alarm['day_4'] or alarm['day_5'] or \
    alarm['day_6']:
        thread = Thread(target=start_alarm, args=(), daemon=True)
        thread.start()

    alarm_notification = ({'timestamp': time.strftime('%H:%M:%S'),
                           'type': 'Alarm',
                           'title': alarm['label'] +
                                    ' Alarm scheduled for ' +
                                    str(alarm_time) +
                                    ' has gone off.',
                           'description': ''
                           })
    alarm_log = ({'timestamp': time.strftime('%H:%M:%S'),
                  'type': 'alarm',
                  'description': 'Alarm scheduled for ' +
                                 str(alarm_time) +
                                 ' has gone off.',
                  'error': ''
                  })
    new_notification(alarm_notification)
    log_info(alarm_log)
    mixer.init()
    mixer.music.load('alarm_sound.mp3')
    mixer.music.play()
    # RuntimeError caused when text to speech is already currently
    # playing something else.
    try:
        tts('Alarm:' + alarm['label'])
    except RuntimeError:
        log_error(RuntimeError)

def day_index(day: str):
    """
    Returns the index of the day of the week from the word.

    Arguments:
    :param day: day of the week as a string.
    """
    if day == 'Monday':
        day_number = 0
    elif day == 'Tuesday':
        day_number = 1
    elif day == 'Wednesday':
        day_number = 2
    elif day == 'Thursday':
        day_number = 3
    elif day == 'Friday':
        day_number = 4
    elif day == 'Saturday':
        day_number = 5
    elif day == 'Sunday':
        day_number = 6
    return day_number

def create_queue(alarm: dict):
    """
    This function makes use of a circular queue class found here:
    https://www.pythoncentral.io/circular-queue/
    A circular queue is created including a today marker marking the
    current day. If there is a repeat scheduled for today, the today
    marker goes before the name of the day. i.e. Today is Wednesday, if
    a repeat alarm includes Wednesday the queue would look like
    (Monday, today, Wednesday, Friday).

    Arguments:
    :param alarm: A dictionary object containing the alarm time and the
                  days to be repeated on.
    """
    today = datetime.date.today()
    day_queue = CircularQueue()
    day_list = []
    for day in range(7):
        day_list.append(alarm['day_'+str(day)])

    if today.strftime('%A') not in day_list:
        for day in range(7):
            # If there is a repeat on this day.
            if alarm['day_'+str(day)]:
                # If that day is earlier on in the week than the
                # current day.
                if day_index(alarm['day_'+str(day)]) < \
                day_index(today.strftime('%A')):
                    day_queue.enqueue(alarm['day_'+str(day)])
        day_queue.enqueue('today')
        for day in range(7):
            # If there is a repeat on this day.
            if alarm['day_'+str(day)]:
                # If that day is later on in the week than the current
                # day.
                if day_index(alarm['day_'+str(day)]) > \
                day_index(today.strftime('%A')):
                    day_queue.enqueue(alarm['day_'+str(day)])
    else:
        for day in range(7):
            if alarm['day_'+str(day)] == today.strftime('%A'):
                day_queue.enqueue('today')
                day_queue.enqueue(alarm['day_'+str(day)])
            else:
                if alarm['day_'+str(day)]:
                    day_queue.enqueue(alarm['day_'+str(day)])
    return day_queue

def sched_next_repeat(alarm: dict) \
    -> typing.Union[float, datetime.datetime]:
    """
    This function schedules the next repeat for repeat alarms. The next
    day for the alarm to be scheduled is found using the today marker.
    The alarm date and time (alarm_time) and the time in seconds
    (delta_time) between now and the time of the alarm if calculated.
    These two variables are then returned to be used in the
    start_alarm() function.
    In hindsight I think it would have been simpler and easier to
    iterate through the alarms each day at midnight and check if there
    are any alarms that are scheduled to go off on that day and set them
    going then.
    Arguments:
    :param alarm: A dictionary object containing the alarm time and the
                  days to be repeated on.
    """
    WEEK = 684000
    EPOCH = datetime.datetime(1970, 1, 1)
    today = datetime.date.today()

    day_queue = create_queue(alarm)
    next_day = day_queue.dequeue()
    found = False
    # Iterates through the circular queue until 'today' is found.
    while not found:
        if next_day == 'today':
            day_queue.enqueue(next_day)
            next_day = day_queue.dequeue()
            break
        day_queue.enqueue(next_day)
        next_day = day_queue.dequeue()

    delta_time = -1
    while delta_time < 0:
        if next_day == today.strftime('%A'):
            # Date and time the alarm is set to go off.
            alarm_time = datetime.datetime.strptime \
                        (str(today) + '-' + alarm['alarm_time'],
                            '%Y-%m-%d-%H:%M')
            # Time in seconds to when the alarm is due to go off.
            delta_time = float((alarm_time - EPOCH)
                                .total_seconds()) \
                                - time.time()
            # If the time is negative, the alarm for that day has
            # already passed so the next day in the queue needs to
            # be tried.
            if delta_time < 0:
                day_queue.enqueue(next_day)
                next_day = day_queue.dequeue()
                if day_queue.size() <= 1:
                    delta_time += WEEK
        else:
            day_number = day_index(next_day)
            # Date and time the alarm is set to go off.
            alarm_time = datetime.datetime.strptime \
                            (str(today + datetime.timedelta
                                (days=-today.weekday()+day_number,
                                weeks=1))
                            + '-' + alarm['alarm_time'],
                            '%Y-%m-%d-%H:%M')
            # Time in seconds to when the alarm is due to go off.
            delta_time = (float((alarm_time - EPOCH).total_seconds())
                            - time.time())
            if day_index(today.strftime('%A')) <= day_index(next_day) \
            and time.time() > (alarm_time.timestamp()-WEEK):
                delta_time -= WEEK
            day_queue.enqueue(next_day)
            next_day = day_queue.dequeue()

    day_queue.enqueue(next_day)
    return delta_time, alarm_time
