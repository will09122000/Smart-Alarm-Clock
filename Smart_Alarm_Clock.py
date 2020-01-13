"""
This program is a smart alarm clock intended to be run 24/7. It enables
the user to schedule, edit and cancel alarms. The user is notified when
an alarm is up via an alarm sound, text to speech and a notification
which is displayed in the notifications column. The user is also
notified when the weather in the location selected has changed and when
there is a new news story. The web page will automatically refresh
every 5 minutes to keep the notifications, weather and news up to date
on screen.
"""
from flask import Flask, render_template, redirect
from alarm import fetch_new_alarm, get_alarms, update_alarm, \
delete_alarm
from weather import change_location, update_weather
from news import update_news
from notifications import update_notifications, notification_clear, \
notification_filter

smart_alarm_clock = Flask(__name__)

@smart_alarm_clock.route('/', methods=['GET', 'POST'])
def home() -> list:
    """
    This function is responsible for fetching a list of alarms, current
    weather, latest news and a list of notifications. This data is
    fetched to be displayed on the main page.
    """
    alarm_list = get_alarms()
    weather_now = update_weather()
    news = update_news()
    notification_list = update_notifications()
    return render_template('index.html', alarm_list=alarm_list,
                           weather_now=weather_now, news=news,
                           notification_list=notification_list)

@smart_alarm_clock.route('/add-alarm', methods=['GET', 'POST'])
def fetch_new_alarm_function():
    """
    See 'fetch_new_alarm()' docstring for more information.
    """
    fetch_new_alarm()
    return redirect('/')

@smart_alarm_clock.route('/update-alarm', methods=['GET', 'POST'])
def update_alarm_function():
    """
    See 'update_alarm()' docstring for more information.
    """
    update_alarm()
    return redirect('/')

@smart_alarm_clock.route('/delete-alarm', methods=['GET', 'POST'])
def delete_alarm_function():
    """
    See 'delete_alarm()' docstring for more information.
    """
    delete_alarm()
    return redirect('/')

@smart_alarm_clock.route('/notification-clear', \
                         methods=['GET', 'POST'])
def notification_clear_function():
    """
    See 'notification_clear()' docstring for more information.
    """
    notification_clear()
    return redirect('/')

@smart_alarm_clock.route('/notification-filter', \
                         methods=['GET', 'POST'])
def notification_filter_function():
    """
    See 'notification_filter' docstring for more information.
    """
    notification_filter()
    return redirect('/')

@smart_alarm_clock.route('/weather-change', \
                         methods=['GET', 'POST'])
def change_location_function():
    """
    See 'change_location()' docstring for more information.
    """
    change_location()
    return redirect('/')

if __name__ == '__main__':
    smart_alarm_clock.run(threaded=True)
