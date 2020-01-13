"""
This module is responsible for all weather functionality. It uses
openweathermap to fetch the current weather in the given location
every 30 seconds. This data is then displayed on the main page. A
notification is sent each time weather has been fetched and some
data has changed, this is also logged. The user can change the
location of the weather with the name of a Town or City.
"""

import time
import json
from threading import Timer, Event
from flask import request
import requests
from jsondiff import diff
from notifications import new_notification
from formatted_log import log_info, log_warning, log_error
from text_to_speech import tts

def get_api_key() -> str:
    """Fetches the openweathermap api key from the config file."""
    with open('config.json', 'r') as config_file:
        api_keys = json.load(config_file)
    return api_keys['openweathermap']['api']

def update_weather() -> dict:
    """
    This function reads the weather stored in the json file and returns
    it as a dictionary.
    """
    global location
    # Attempts to load contents of the file. If it's empty, an
    # empty list is defined and a warning is sent to the log file.
    with open('weather.json', 'r') as weather_file:
        try:
            weather_now = json.load(weather_file)
            location = weather_now['name']
        except Exception as error:
            log_warning(error)
    return weather_now

def get_weather() -> None:
    """
    This function fetches the weather data from openweathermap as well
    as with the potentially out of date weather from the json file. If
    the locations are the same and there is a difference in the data, a
    notification and log are sent, as well as a text to speech
    notification and the weather data in the json file is updated. If
    the location is different, the new weather is written to the json
    file without checking for any differences in the data.
    """
    global location
    api_key = get_api_key()
    url = 'https://api.openweathermap.org/data/2.5/weather?q={} \
    &appid={}&units=metric'.format(location, api_key)
    new_weather = requests.get(url).json()
    old_weather = update_weather()
    # If the weather has been fetched from the same location.
    if old_weather['name'] == new_weather['name']:
        weather_difference = diff(old_weather, new_weather)
        # If there's a difference, send a notification and log.
        if len(weather_difference) > 0:
            weather_notification = ({'timestamp': \
                                     time.strftime('%H:%M:%S'),
                                     'type': 'Weather',
                                     'title': 'Current Weather in ' \
                                     + new_weather['name'] \
                                     + ' has been updated.',
                                     'description': ''})
            weather_log = ({'timestamp': time.strftime('%H:%M:%S'),
                            'type': 'weather',
                            'description': 'Current Weather in ' \
                            + new_weather['name'] \
                            + ' has been updated.',
                            'error': ''})
            new_notification(weather_notification)
            log_info(weather_log)
            # RuntimeError caused when text to speech is already
            # currently playing something else.
            try:
                tts('Current Weather in ' + new_weather['name'] \
                    + ' has been updated.')
            except RuntimeError:
                log_error(RuntimeError)

    with open('weather.json', 'w') as weather_file:
        json.dump(new_weather, weather_file, indent=2)
    # Start the timer to run this function every 30 seconds.
    Timer(30, get_weather).start()

def change_location():
    """
    This function fetches the new location requested by the user.
    Checks it against all Cities and Towns that openweathermap has
    weather data for. If it's in that json file, the location is
    accepted and the new weather from the new location is fetched.
    If the location can't be found, the exiting location is kept.
    """
    global location
    new_location = request.args.get('new_location')
    # If the text box is not empty.
    if new_location:
        # Checks that the input is valid for openweathermap.
        with open('city.list.json', 'r', encoding='utf8') \
        as city_list_file:
            city_list = json.load(city_list_file)
        for city in city_list:
            if new_location.lower() == city['name'].lower():
                location = new_location
                break
    return get_weather()

update_weather()

done = Event()
Timer(30, get_weather).start()
done.set()
