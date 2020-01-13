"""
This module is responsible for all news functionality. It uses newsapi
to fetch the latest news stories every 60 seconds
"""

import json
import time
from threading import Timer, Event
import requests
from notifications import new_notification
from formatted_log import log_info, log_warning, log_error
from text_to_speech import tts

def get_api_key() -> dict:
    """Fetches the newsapi api key from the config file."""
    with open('config.json', 'r') as config_file:
        api_keys = json.load(config_file)
    return api_keys['newsapi']['api']

def update_news() -> dict:
    """
    This function reads the news stories stored in the json file and
    returns it as a dictionary.
    """
    # Attempts to load contents of the file. If it's empty, an
    # empty list is defined and a warning is sent to the log file.
    with open('news.json', 'r') as news_file:
        try:
            news = json.load(news_file)
        except Exception as error:
            news = []
            log_warning(error)
    return news

def get_news() -> None:
    """
    This function fetches the news data from newsapi as well as with
    the potentially out of date news from the json file. If a new news
    story is found, a notification and log is sent with about the new
    story. The news is then written to the json file.
    """
    api_key = get_api_key()
    country = 'gb'
    url = 'https://newsapi.org/v2/top-headlines?country={}&apiKey={}' \
    .format(country, api_key)
    new_news = requests.get(url).json()
    with open('news.json', 'r') as news_file:
        try:
            old_news = json.load(news_file)
        except Exception as error:
            log_warning(error)
    # Checks if the news is new or the same as the news already stored
    # in news.json.
    for i in range(5):
        if old_news['articles'][i] != new_news['articles'][i]:
            news_notification = ({'timestamp': \
                                    time.strftime('%H:%M:%S'),
                                    'type': 'News',
                                    'title': new_news \
                                    ['articles'][i]['title'],
                                    'description': ''})
            news_log = ({'timestamp': time.strftime('%H:%M:%S'),
                            'type': 'news',
                            'description': 'New news articles' \
                            + new_news['articles'][i]['title'],
                            'error': ''})
            new_notification(news_notification)
            log_info(news_log)
            # RuntimeError caused when text to speech is already
            # currently playing something else.
            try:
                tts('New news story.' \
                    + new_news['articles'][i]['title'])
            except RuntimeError:
                log_error(RuntimeError)

    with open('news.json', 'w') as news_file:
        json.dump(new_news, news_file, indent=2)
    # Start the timer to run this function every 60 seconds.
    Timer(60, get_news).start()

done = Event()
Timer(60, get_news).start()
done.set()
