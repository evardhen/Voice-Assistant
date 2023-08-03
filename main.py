from loguru import logger
import yaml
import sys
import pyaudio
import pvporcupine
import struct
from vosk import Model, SpkModel, KaldiRecognizer
import sys
import numpy as np
import os
import wave
import threading
import dotenv
import openai

from voice_management import Voice
from user_management import UserManagement
from intent_management import IntentManagement
from audioplayer import AudioPlayer
from spotify_management import Spotify
from chatbot_initialization import Chatbot
from usb_4_mic_array.VAD import speech_activity_detection

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
CONFIG_FILE = 'config.yml'
KEYWORD_PATH = os.path.abspath(os.path.join(".", "custom_wakewords", "Hey-Luna_de_windows_v2_2_0.ppn"))
MODEL_FILE_PATH = os.path.abspath(os.path.join(".", "custom_wakewords", "porcupine_params_de.pv"))

class VoiceAssistant():

    def __init__(self):
        global CONFIG_FILE
        self.audio_frames = []
        self.default_wakeword = 'Hey Luna'
        # device_index = 2 # select correct microphone (for PC)
        device_index = 1 # select correct microphone (for laptop)
        self.is_listening = False
        self.mute_volume = 0.1

        dotenv.load_dotenv()
        self.open_global_config()
        self.initialize_voice()
        self.initialize_chatbot()
        self.initialize_wakeword_detection(device_index)
        self.load_s2t_model()
        self.initialize_user_mgmt()
        self.initialize_intents()
        self.initialize_music_stream()
        self.initialize_spotify()
        logger.debug("Initialisierung abgeschlossen.")

    def initialize_chatbot(self):
        self.chatbot = Chatbot(self.language)

    def initialize_spotify(self):
        self.spotify = Spotify(self.volume)

    def initialize_music_stream(self):
        self.audioplayer = AudioPlayer(self.volume)

    def initialize_intents(self):
        self.intents = IntentManagement(self)
        self.callbacks = self.intents.register_callbacks()

    def initialize_user_mgmt(self):
        self.user_mgmt = UserManagement()
        self.allow_known_speaker = self.config['assistant']['allow_only_known_speaker']

    def detect_speaker(self, inputSpeaker):
        # TODO: Not yet working properly, because the qualitiy of the recorded microphone
        # data varies a lot
        bestSpeaker = None
        bestCosDIst = 1.1
        for speaker in self.user_mgmt.speaker_table.all():
            nx = np.array(speaker.get('voice'))
            ny = np.array(inputSpeaker)
            cosDist = 1 - np.dot(nx, ny) / (np.linalg.norm(nx) * np.linalg.norm(ny))
            logger.debug("Cosine similarity: {}", cosDist)
            if(cosDist < bestCosDIst and cosDist < 0.7): # always between 0 and 1
                bestCosDIst = cosDist
                bestSpeaker = speaker.get('name')
        return bestSpeaker


    def load_s2t_model(self):
        logger.debug("Lade s2t Modell...")
        s2t_model = Model('./speech_model/vosk-model-de-0.21/vosk-model-de-0.21') # path to model
        logger.debug("Lade Speaker Modell...")
        speaker_model = SpkModel('./speech_model/vosk-model-spk-0.4/vosk-model-spk-0.4') # path to model
        logger.debug("Speaker Modelle erfolgreich geladen.")
        self.recognizer = KaldiRecognizer(s2t_model, 16000, speaker_model)


    def open_global_config(self):
        with open(CONFIG_FILE, "r", encoding='utf-8') as file:
            try:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
                logger.debug('YAML Datei erfolgreich geladen.')
            except yaml.YAMLError as exc:
                logger.error(exc)
                sys.exit(1)

    def initialize_voice(self, default_language = "de"):
        self.volume = self.config["assistant"]["volume"]
        self.language = self.config['assistant']['language']
        if not self.language:
            self.language = default_language
        logger.info('Verwende Sprache {}.', self.language)

        self.tts = Voice(self.config['assistant']['voiceSpeed'], self.volume)
        voices = self.tts.get_voice_id(self.language)
        if len(voices) > 0:
          self.tts.set_voice(voices[0])
          logger.info('Stimme {}', voices[0])

    def initialize_wakeword_detection(self, device_index):
        logger.debug("Starte Wakeword Erkennung.")
        self.wakewords = self.config['assistant']['wakewords']
        if not self.wakewords:
             self.wakewords = [self.default_wakeword]
        logger.debug('Wakewords sind {}', ', '.join( self.wakewords))

        # print(pvporcupine.KEYWORDS)
        dotenv.load_dotenv()
        PICOVOICE_KEY = os.environ.get('PICOVOICE_KEY')
        self.porc = pvporcupine.create(access_key=PICOVOICE_KEY, keyword_paths=[KEYWORD_PATH], model_path=MODEL_FILE_PATH)
        self.pyAudio = pyaudio.PyAudio()
        # # select correct microphone
        # for i in range(self.pyAudio.get_device_count()):
        #     device_info = self.pyAudio.get_device_info_by_index(i)
        #     print(f"Device {i}: {device_info['name']} (Sample Rate: {device_info['defaultSampleRate']} Hz, Channels: {device_info['maxInputChannels']})")
        logger.debug("Sample rate: {}", self.porc.sample_rate)
        self.audio_stream = self.pyAudio.open(rate = self.porc.sample_rate, channels=1, format = pyaudio.paInt16, input=True, frames_per_buffer=self.porc.frame_length, input_device_index= device_index)

    def execute_callbacks(self):
        for callback in self.callbacks:
            output = callback(False, self.language)
            if output and not self.tts.is_busy():
                if self.audioplayer.is_playing():
                    self.audioplayer.set_volume(self.mute_volume)
                callback(True, self.language)
                self.tts.say(output, self.language)
                self.audioplayer.set_volume(self.tts.get_volume())

    def save_audio_to_wav(self, filename):
        wav_file = wave.open(filename, "wb")
        wav_file.setnchannels(1)  # Mono audio channel
        wav_file.setsampwidth(self.pyAudio.get_sample_size(pyaudio.paInt16))  # 2 bytes per sample (16-bit audio)
        wav_file.setframerate(self.porc.sample_rate)  # Set the frame rate to match the audio stream
        wav_file.writeframes(b''.join(self.audio_frames))
        wav_file.close()

    def speech_activity_detection(self):
        while True:
            pcm = self.audio_stream.read(self.porc.frame_length)
            if self.recognizer.AcceptWaveform(pcm):
                self.recognizer.Reset()
                logger.debug("Thread 1 zur Spracherkennung erfolgreich beendet.")
                return
    
    def recognize_speech(self):
        if self.audioplayer.is_playing():
            self.audioplayer.set_volume(self.mute_volume)
        if self.spotify.is_playing:
            self.spotify.set_volume(self.mute_volume)

        thread = threading.Thread(target=self.speech_activity_detection)
        thread.start()
        threshhold = 9
        thread2 = threading.Thread(target=speech_activity_detection, args=(threshhold,))
        thread2.start()
        while thread.is_alive() and thread2.is_alive():
            pcm = self.audio_stream.read(self.porc.frame_length)
            self.audio_frames.append(pcm)


        # Write the recorded audio data to a .wav file
        self.save_audio_to_wav("./recorded_audio.wav")
        self.audio_frames = []

        sentence = self.whisper("./recorded_audio.wav")

        # result = json.loads(self.recognizer.Result())
        # # logger.info('Result: {}', result)
        # sentence = result['text']
        logger.info("Ich habe '{}' verstanden.", sentence)

        output = self.intents.process(sentence)

        self.tts.say(output, self.language)

    def whisper(self, filename):
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        audio_file = open(filename, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript.text

    def run(self):
        logger.info("VoiceAssistant gestartet...")
        try:
            while True:
                pcm = self.audio_stream.read(self.porc.frame_length)

                pcm_unpacked =  struct.unpack_from("h" * self.porc.frame_length, pcm)
                keyword_index = self.porc.process(pcm_unpacked)
                if keyword_index >= 0: # -1, if no keyword was detected
                    logger.info("Wakeword '{}' erkannt. Wie kann ich dir helfen?",  self.wakewords[keyword_index])
                    self.recognize_speech()
                    keyword_index = -1
                                
                if not self.tts.is_busy() and self.spotify.is_playing:
                    self.audioplayer.set_volume(self.tts.get_volume())
                self.execute_callbacks()

        except KeyboardInterrupt:
            logger.info("Prozess durch Keyboard unterbrochen.")

        finally:
            try:
                self.volume = self.tts.volume
                self.config['assistant']['voiceSpeed'] = self.tts.voiceSpeed
                with open(CONFIG_FILE, "w") as file:
                    yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
            except Exception as e:
                logger.error("Konnte config.yaml nicht lesem: {}", e)

            logger.debug('Beende offene Pakete...')
            if self.porc:
                self.porc.delete()
            if self.audio_stream is not None:
                self.audio_stream.close()
            if self.pyAudio is not None:
                self.pyAudio.terminate()
            if self.audioplayer is not None:
                self.audioplayer.stop()


if __name__ == '__main__':
    va = VoiceAssistant()
    va.run()