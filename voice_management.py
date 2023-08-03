import pyttsx3
import threading
from loguru import logger
import sounddevice as sd
import soundfile as sf
from langdetect import detect
from gtts import gTTS

SPEECH_FILE_PATH = "output.wav"

def __speak__(text, voiceId, speed, vol):
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.setProperty('rate', speed)
    engine.setProperty('volume', vol)
    engine.say(text)
    engine.runAndWait()
    logger.debug("Finished speaker thread.")

def __speak_gtts__(text, volume, default_language):
    detected_language = detect_language(text, default_language)

    tts = gTTS(text=text, lang=detected_language, slow=False)
    # Saving the converted audio in an mp3 file
    tts.save(SPEECH_FILE_PATH) 

    data, fs = sf.read(SPEECH_FILE_PATH)
    scaled_data = volume * data
    sd.play(scaled_data, fs)
    sd.wait()
    logger.debug("Finished speaker thread.")

def detect_language(string, default_language):
    detected_language = detect(string)
    if detected_language not in ["de", "en"]:
        detected_language = default_language
    return detected_language

class Voice():
    def __init__(self, voiceSpeed = 150, volume = 0.5):
        self.process = None
        self.voiceId = None
        self.voiceSpeed = voiceSpeed
        self.volume = volume

    def get_volume(self):
        return self.volume
    
    def set_volume(self, volume):
        self.volume = volume
        
    def set_voiceSpeed(self, voiceSpeed):
        self.voiceSpeed = voiceSpeed
    
    def get_voiceSpeed(self):
        return self.voiceSpeed

    def say(self, text, default_language):
        thread = threading.Thread(target=__speak__, args=(text, self.voiceId, self.voiceSpeed, self.volume))
        # thread = threading.Thread(target=__speak_gtts__, args=(text, self.volume, default_language))
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