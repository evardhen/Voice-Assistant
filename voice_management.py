import pyttsx3
import threading
from loguru import logger
from multiprocessing import Process

def __speak__(text, voiceId, speed, vol):
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.setProperty('rate', speed)
    engine.setProperty('volume', vol)
    engine.say(text)
    engine.runAndWait()
    logger.debug("Finished speaker thread.")

class Voice():
    def __init__(self, voiceSpeed = 150, volume = 0.5):
        self.process = None
        self.voiceId = None
        self.voiceSpeed = voiceSpeed
        self.volume = volume
        

    def initialize_voice(self, voiceId, speed, vol):
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', voiceId)
        self.engine.setProperty('rate', speed)
        self.engine.setProperty('volume', vol)

    def get_volume(self):
        return self.volume
    
    def set_volume(self, volume):
        self.volume = volume
        
    def set_voiceSpeed(self, voiceSpeed):
        self.voiceSpeed = voiceSpeed
    
    def get_voiceSpeed(self):
        return self.voiceSpeed

    def say(self, text):
        thread = threading.Thread(target=__speak__, args=(text, self.voiceId, self.voiceSpeed, self.volume))
        thread.start()
    
    def is_busy(self):
        if self.process:
            return self.process.is_alive()

    def set_voice(self, voiceId):
        self.voiceId = voiceId

    def get_voice_id(self, language=''):
        result = []
        engine = pyttsx3.init()
        language_search_string = language.upper() + '-' # hardcoded as it can be found in voices
        voices = engine.getProperty('voices')
        for voice in voices:
            if language == '':
                result.append(voice.id)
            elif language_search_string in voice.id:
                result.append(voice.id)
        return result