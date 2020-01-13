"""This module is responsible for playing text to speech messages."""

import pyttsx3
import pythoncom

def tts(text:str) -> None:
    """
    This function takes in a message and plays it using pyttsx3.
    :param text: The message to be read aloud.
    """
    pythoncom.CoInitialize()
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
