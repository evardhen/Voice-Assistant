import pyttsx3
import threading
from loguru import logger
from langdetect import detect
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

SPEECH_FILE_PATH = "./audios/gtts_output.mp3"

def __speak__(text, voiceId, speed, vol):
    engine = pyttsx3.init()
    engine.setProperty('voice', voiceId)
    engine.setProperty('rate', speed)
    engine.setProperty('volume', vol)
    engine.say(text)
    engine.runAndWait()
    logger.debug("Finished pytts speaker thread.")

def __speak_gtts__(text, volume, pytts_voice_speed, default_language):
    detected_language = detect_language(text, default_language)

    tts = gTTS(text=text, lang=detected_language, slow=False)
    # Saving the converted audio in a BytesIO object
    tts.save(SPEECH_FILE_PATH)

    # Load the audio file
    audio = AudioSegment.from_file(SPEECH_FILE_PATH, format="mp3")

    # Change volume in percentage
    audio_mod = change_volume(audio, volume * 100)
    
    # Speed up the audio, 150 is used as lowest ground speed using the pytts library
    converted_speed = pytts_voice_speed / 150 - 0.05
    if converted_speed > 1:
        audio_mod = audio_mod.speedup(playback_speed=converted_speed)
    
    play(audio_mod)
    logger.debug("Finished gTTS speaker thread.")

def change_volume(audio, percent):
    if percent == 0:
        return audio - 100
    if percent <= 100:
        return audio + (audio.dBFS - (percent / 100) * audio.dBFS)
    elif percent > 100:
        vol_change = audio.dBFS - (percent / 100) * audio.dBFS
        if audio.dBFS - vol_change >= 0:
            vol_change = audio
        return audio + vol_change

def detect_language(string, default_language):
    detected_language = detect(string)
    if detected_language not in ["de", "en"]:
        detected_language = default_language
    return detected_language

class Voice():
    def __init__(self, voiceSpeed, volume):
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