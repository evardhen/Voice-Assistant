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


SPEECH_FILE_PATH = "output.mp3"

def __speak__(text, voiceId, speed, vol):
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.setProperty('rate', speed)
    engine.setProperty('volume', vol)
    engine.say(text)
    engine.runAndWait()
    logger.debug("Finished speaker thread.")

def __speak_gtts__(text, volume_change_percent, speed, default_language):
    detected_language = detect_language(text, default_language)

    tts = gTTS(text=text, lang=detected_language, slow=False)
    # Saving the converted audio in a BytesIO object
    tts.save(SPEECH_FILE_PATH)

    audio = AudioSegment.from_mp3(SPEECH_FILE_PATH)
    audio = change_volume(audio, volume_change_percent)

    chunk_size = 150 # in milliseconds
    if speed != 1.0:
        audio = speedup(audio, speed, chunk_size)
        
    outfile_path = "./output_modified.wav"
    outfile_format = "wav"
    audio.export(outfile_path, format=outfile_format)

    # Read the wav file
    data, fs = sf.read(outfile_path)
    # Play the audio
    sd.play(data, fs)
    sd.wait()
    logger.debug("Finished speaker thread.")

def detect_language(string, default_language):
    detected_language = detect(string)
    if detected_language not in ["de", "en"]:
        detected_language = default_language
    return detected_language

def change_volume(audio, volume_change_percent):
    # Convert volume change from percent to dB
    if volume_change_percent > 0:
        volume_change_db = 20 * np.log10(1 + volume_change_percent / 100)
    else:
        volume_change_db = -20 * np.log10(1 - volume_change_percent / 100)
    # Apply volume change
    return audio + volume_change_db

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
        # thread = threading.Thread(target=__speak__, args=(text, self.voiceId, self.voiceSpeed, self.volume))
        thread = threading.Thread(target=__speak_gtts__, args=(text, self.volume, self.voiceSpeed, default_language))
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