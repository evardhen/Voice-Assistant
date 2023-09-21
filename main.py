import argparse
import sys
import os
import threading
from loguru import logger
import yaml
import pyaudio
import struct
import wave
import dotenv

import pvporcupine
from vosk import Model, SpkModel, KaldiRecognizer
import openai

from voice_management import Voice
from intent_management import IntentManagement
from audioplayer import AudioPlayer
from chatbot_initialization import Chatbot
from spotify_management import Spotify
from usb_4_mic_array.VAD import speech_activity_detection
import global_variables

CONFIG_FILE = 'config.yml'
KEYWORD_PATH = os.path.abspath(os.path.join(".", "custom_wakewords", "Hey-Luna_de_windows_v2_2_0.ppn"))
MODEL_FILE_PATH = os.path.abspath(os.path.join(".", "custom_wakewords", "porcupine_params_de.pv"))

class VoiceAssistant():

    def __init__(self):
        global CONFIG_FILE
        self.audio_frames = []
        self.default_wakeword = 'Hey Luna'
        self.is_listening = False
        self.mute_volume = 0.1
        self.recognizer = None

        dotenv.load_dotenv()
        microphone_index = self.select_microphone()
        self.open_global_config()
        self.initialize_voice()
        self.initialize_chatbot()
        self.initialize_spotify()
        self.initialize_wakeword_detection(microphone_index)
        if self.config['assistant']['is_vosk_model']:
            self.load_vosk_model()
        self.initialize_intents()
        self.initialize_music_stream()
        logger.debug("Initialization completed.")

    def select_microphone(self):
        self.pyAudio = pyaudio.PyAudio()
        parser = argparse.ArgumentParser(description='Select microphone.')
        parser.add_argument('-m', '--microphone', type=int, help='Index of the microphone to use')

        args = parser.parse_args()

        if args.microphone is not None:
            selected_microphone = args.microphone
        else:
            selected_microphone = None

            # Print available microphones
            print("\nList of available microphones:\n")
            for i in range(self.pyAudio.get_device_count()):
                device_info = self.pyAudio.get_device_info_by_index(i)
                print(f"Device {i}: {device_info['name']} (Sample Rate: {device_info['defaultSampleRate']} Hz, Channels: {device_info['maxInputChannels']})")

            # Ask user to select a microphone
            while selected_microphone is None:
                try:
                    selected_microphone = int(input("\nEnter the index of the microphone you want to use: "))
                    if not (0 <= selected_microphone < self.pyAudio.get_device_count()):
                        print(f"Invalid microphone index. Please select an index between 0 and {self.pyAudio.get_device_count()}.")
                        selected_microphone = None
                except ValueError:
                    print("Invalid input format. Please enter a valid microphone index as an integer.")

        return selected_microphone


    def initialize_spotify(self):
        global_variables.spotify = Spotify()

    def initialize_chatbot(self):
        self.chatbot = Chatbot(self.language)

    def initialize_music_stream(self):
        self.audioplayer = AudioPlayer(self.volume)

    def initialize_intents(self):
        self.intents = IntentManagement(self)
        self.callbacks = self.intents.register_callbacks()

    def load_vosk_model(self):
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
                logger.debug('Global Config (YAML) file loaded successfully.')
            except yaml.YAMLError as exc:
                logger.error(exc)
                sys.exit(1)

    def initialize_voice(self, default_language = "de"):
        self.volume = self.config["assistant"]["volume"]
        self.language = self.config['assistant']['language']
        if not self.language:
            self.language = default_language
        logger.info('Use language: {}.', self.language)

        global_variables.tts = Voice(self.config['assistant']['voiceSpeed'], self.volume)
        voices = global_variables.tts.get_voice_id(self.language)
        if len(voices) > 0:
          global_variables.tts.set_voice(voices[0])
          logger.info('Active pytts voice: {}', voices[0])

    def initialize_wakeword_detection(self, device_index):
        logger.debug("Starting wake word detection....")
        self.wakewords = self.config['assistant']['wakewords']
        if not self.wakewords:
             self.wakewords = [self.default_wakeword]
        logger.debug('Wake words are: {}', ', '.join( self.wakewords))
        # print(pvporcupine.KEYWORDS)

        PICOVOICE_KEY = os.environ.get('PICOVOICE_KEY')
        self.porc = pvporcupine.create(access_key=PICOVOICE_KEY, keyword_paths=[KEYWORD_PATH], model_path=MODEL_FILE_PATH)
        self.audio_stream = self.pyAudio.open(rate = self.porc.sample_rate, channels=1, format = pyaudio.paInt16, input=True, frames_per_buffer=self.porc.frame_length, input_device_index= device_index)

    def execute_callbacks(self):
        for callback in self.callbacks:
            output = callback(False, self.language)
            if output and not global_variables.tts.is_busy():
                if self.audioplayer.is_playing():
                    self.audioplayer.set_volume(self.mute_volume)
                callback(True, self.language)
                global_variables.tts.say(output, self.language)
                self.audioplayer.set_volume(global_variables.tts.get_volume())

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
        # Mute other devices while listening
        if self.audioplayer.is_playing():
            logger.debug(f"Set audioplayer volume to mute volume: {self.mute_volume}")
            self.audioplayer.set_volume(self.mute_volume)
        if global_variables.spotify.is_spotify_playing():
            logger.debug(f"Set spotify volume to mute volume: {self.mute_volume}")
            global_variables.spotify.set_volume(self.mute_volume)
        
        # Start 2 different threads for 2 different speech activity detections algorithms
        threshhold = 9
        thread2 = threading.Thread(target=speech_activity_detection, args=(threshhold,))
        thread2.start()
        if self.recognizer is None:
            while thread2.is_alive():
                pcm = self.audio_stream.read(self.porc.frame_length)
                self.audio_frames.append(pcm)
        else:
            thread = threading.Thread(target=self.speech_activity_detection)
            thread.start()
            while thread.is_alive() and thread2.is_alive():
                pcm = self.audio_stream.read(self.porc.frame_length)
                self.audio_frames.append(pcm)


        # Write the recorded audio data to a .wav file
        self.save_audio_to_wav("./audios/recorded_audio.wav")
        self.audio_frames = []

        sentence = self.whisper("./audios/recorded_audio.wav")

        # result = json.loads(self.recognizer.Result())
        # # logger.info('Result: {}', result)
        # sentence = result['text']
        logger.info("Ich habe '{}' verstanden.", sentence)

        output = self.intents.process(sentence)

        global_variables.tts.say(output, self.language)

    def whisper(self, filename):
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        audio_file = open(filename, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript.text

    def run(self):
        logger.info("VoiceAssistant started...")
        try:
            while True:
                pcm = self.audio_stream.read(self.porc.frame_length)
                pcm_unpacked =  struct.unpack_from("h" * self.porc.frame_length, pcm)
                keyword_index = self.porc.process(pcm_unpacked)
                if keyword_index >= 0: # -1, if no keyword was detected
                    logger.info("Wakeword '{}' detected. How can I help you?",  self.wakewords[keyword_index])
                    self.recognize_speech()
                    keyword_index = -1
                                
                self.execute_callbacks()

        except KeyboardInterrupt:
            print("\n")
            logger.info("Process interrupted by keyboard.")

        finally:
            try:
                self.volume = global_variables.tts.volume
                self.config['assistant']['voiceSpeed'] = global_variables.tts.voiceSpeed
                with open(CONFIG_FILE, "w") as file:
                    yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)
            except Exception as e:
                logger.error("Could not read config.yaml: {}", e)

            logger.debug('Closing open packages...')
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