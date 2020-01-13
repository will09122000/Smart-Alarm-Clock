"""
This module is responsible for all notification functionality. It
displays the latest notifications in the centre column on the webpage
ordered by time. The user can clear the notifications or filter the
displayed notifications from three categories: alarms, weather and
news.
"""
import json
from flask import request
from formatted_log import log_warning
global filter_request
global notifications_filtered

filter_request = False
notifications_filtered = []

def new_notification(notification_object: dict) -> None:
    """
    Each time an alarm goes off, a change in weather has been detected
    or there's a new news story, the data is sent to this function. The
    data for that notification is then appended to the json file.
    """
    # Attempts to load contents of the file. If it's empty, an
    # empty list is defined and a warning is sent to the log file.
    with open('notifications.json', 'r') as notification_file:
        try:
            notifications = json.load(notification_file)
        except Exception as error:
            notifications = []
            log_warning(error)

    notifications.append(notification_object.copy())

    with open('notifications.json', 'w') as notification_file:
        json.dump(notifications, notification_file, indent=2)

def update_notifications() -> dict:
    """
    This function will run each time the page is refreshed or the user
    clicks the 'Filter button'. It returns the appropriate list of
    notifications depending if the 'Filter' button was pressed or the
    page was refreshed.
    """
    if filter_request:
        return notifications_filtered

    with open('notifications.json', 'r') as notification_file:
        try:
            notifications = json.load(notification_file)
        except Exception as error:
            notifications = []
            log_warning(error)
    return notifications

def notification_clear() -> None:
    """
    This function will clear the notification json file when the
    'Clear' button is pressed.
    """
    notifications = []
    with open('notifications.json', 'w') as notification_file:
        json.dump(notifications, notification_file, indent=2)

def notification_filter() -> None:
    """
    This function creates a list of filtered notifications depending
    on which boxes are checked when the user presses the 'Filter'
    button.
    """
    global filter_request
    global notifications_filtered
    filter_request = True
    notifications_filtered = []

    alarm = request.args.get('alarm')
    weather = request.args.get('weather')
    news = request.args.get('news')

    with open('notifications.json', 'r') as notification_file:
        if os.stat('notifications.json').st_size != 0:
            notification_list = json.load(notification_file)
            for notification in notification_list:
                # If the notification is an alarm and they checked the
                # alarm box, add it to the filtered list.
                if notification['type'] == 'Alarm' and alarm == 'True':
                    notifications_filtered.append(notification)
                if notification['type'] == 'Weather' and \
                weather == 'True':
                    notifications_filtered.append(notification)
                if notification['type'] == 'News' and news == 'True':
                    notifications_filtered.append(notification)
