from loguru import logger
import pyttsx3
from multiprocessing import Process
import time

def __speak__(text, voiceId):
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.say(text)
    engine.runAndWait()

class Voice():

    def __init__(self):
        self.process = None
        self.voiceId = None

    def say(self, text):
        if self.process:
            self.stop()
        p = Process(target=__speak__, args=(text, self.voiceId))
        p.start()
        self.process = p

    def set_voice(self, voiceId):
        self.voiceId = voiceId

    def stop(self):
        if self.process:
          self.process.terminate()

    def get_voice_id(self, language=''):
        result = []
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if language == '':
                result.append(voice.id)
            elif language.lower() in voice.name.lower():
                result.append(voice.id)
        return result