from alarm import sched_next_repeat
import time, datetime

def alarm_test():
    time_now = time.strftime('%H:%M')
    today = datetime.datetime.now().strftime("%A")
    alarm = {
    "alarm_time": time_now,
    "day_0": "Monday",
    "day_1": "Tuesday",
    "day_2": "Wednesday",
    "day_3": "Thursday",
    "day_4": "Friday",
    "day_5": "Saturday",
    "day_6": "Sunday",
    "label": ""
  }
    assert sched_next_repeat(alarm) <= 86400, 'sched_next_repeat: FAILED'



alarm_test()