import pyttsx3
import threading
from loguru import logger
from langdetect import detect
from gtts import gTTS
import numpy as np
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import speedup

SPEECH_FILE_PATH = "./audios/gtts_output.mp3"
MODIFIED_SPEECH_FILE_PATH = "./audios/gtts_output_modified.wav"

def __speak__(text, voiceId, speed, vol):
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.setProperty('rate', speed)
    engine.setProperty('volume', vol)
    engine.say(text)
    engine.runAndWait()
    logger.debug("Finished pytts speaker thread.")

def __speak_gtts__(text, volume, pytts_speed, default_language):
    detected_language = detect_language(text, default_language)

    tts = gTTS(text=text, lang=detected_language, slow=False)
    # Saving the converted audio in a BytesIO object
    tts.save(SPEECH_FILE_PATH)

    audio = AudioSegment.from_mp3(SPEECH_FILE_PATH)
    
    # Calculate the volume change in percent, where 0.5 is the reference with a rane from 0 to 1
    volume_change_percent = ((volume/0.5) - 1) * 100
    if volume_change_percent != 0:
        audio = change_volume(audio, volume_change_percent)

    chunk_size = 150 # in milliseconds

    # convert the scale from pytts to gtts
    gtts_speed = pytts_speed / 150
    if gtts_speed > 1.0:
        audio = speedup(audio, gtts_speed, chunk_size)
    elif gtts_speed < 1:
        logger.error(f"Value out of range for voice speed: {gtts_speed}, only allowed between 1. and 1.33!")
        
    audio.export(MODIFIED_SPEECH_FILE_PATH, format="wav")

    # Read the wav file
    data, fs = sf.read(MODIFIED_SPEECH_FILE_PATH)
    # Play the audio
    sd.play(data, fs)
    sd.wait()
    logger.debug("Finished gTTS speaker thread.")

def detect_language(string, default_language):
    detected_language = detect(string)
    if detected_language not in ["de", "en"]:
        detected_language = default_language
    return detected_language

def change_volume(audio, volume_change_percent):
    # Calculate the linear gain factor based on the percentage change in volume
    gain = 1 + (volume_change_percent / 100.0)

    # Apply the gain to the audio
    adjusted_audio = audio.apply_gain(gain)
    
    return adjusted_audio

class Voice():
    def __init__(self, voiceSpeed = 150, volume = 0.5):
        self.process = None
        self.voiceId = None
        self.voiceSpeed = voiceSpeed
        self.volume = volume
        self.voice_engine = "gTTS"

    def get_volume(self):
        return self.volume
    
    def get_voice_engine(self):
        return self.voice_engine
    
    def set_voice_engine(self, voice_type):
        self.voice_engine = voice_type

    def set_volume(self, volume):
        self.volume = volume
        
    def set_voiceSpeed(self, voiceSpeed):
        self.voiceSpeed = voiceSpeed
    
    def get_voiceSpeed(self):
        return self.voiceSpeed

    def say(self, text, default_language):
        if self.voice_engine == "gTTS":
            thread = threading.Thread(target=__speak_gtts__, args=(text, self.volume, self.voiceSpeed, default_language))
        else:
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