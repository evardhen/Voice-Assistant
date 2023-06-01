from loguru import logger
import multiprocessing
from voice_management import Voice
import yaml
import sys
import pyaudio
import pvporcupine
import struct
from vosk import Model, SpkModel, KaldiRecognizer
import json
import sys
from user_management import UserManagement
import numpy as np
from intent_management import IntentManagement
import os
from audioplayer import AudioPlayer
from spotify_management import Spotify

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
CONFIG_FILE = 'config.yml'


class VoiceAssistant():

    def __init__(self):
        global CONFIG_FILE
        default_wakeword = 'terminator'
        device_index = 2 # select correct microphone
        self.is_listening = False
        self.mute_volume = 0.1

        self.open_global_config()
        self.initialize_voice()
        self.initialize_wakeword_detection(default_wakeword, device_index)
        self.load_s2t_model()
        self.initialize_user_mgmt()
        self.initialize_intents()
        self.initialize_music_stream()
        self.initialize_spotify()
        logger.debug("Initialisierung abgeschlossen.")
        
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
        s2t_model = Model('./vosk-model-de-0.21/vosk-model-de-0.21') # path to model
        logger.debug("Lade Speaker Modell...")
        speaker_model = SpkModel('./vosk-model-spk-0.4/vosk-model-spk-0.4') # path to model
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

    def initialize_wakeword_detection(self, default_wakeword, device_index):
        logger.debug("Starte Wakeword Erkennung.")
        self.wakewords = self.config['assistant']['wakewords']
        if not  self.wakewords:
             self.wakewords = [default_wakeword]
        logger.debug('Wakewords sind {}', ', '.join( self.wakewords))

        self.porc = pvporcupine.create(keywords= self.wakewords)
        self.pyAudio = pyaudio.PyAudio()
        # # select correct microphone
        # for i in range(self.pyAudio.get_device_count()):
        #     logger.debug('id: {}, name: {}', self.pyAudio.get_device_info_by_index(i).get('index'), self.pyAudio.get_device_info_by_index(i).get('name'))
        self.audio_stream = self.pyAudio.open(rate = self.porc.sample_rate, channels=1, format = pyaudio.paInt16, input=True, frames_per_buffer=self.porc.frame_length, input_device_index= device_index)

    def execute_callbacks(self):
        for callback in self.callbacks:
            output = callback(False, self.language)
            if output and not self.tts.is_busy():
                if self.audioplayer.is_playing():
                    self.audioplayer.set_volume(self.mute_volume)
                callback(True, self.language)
                self.tts.say(output)
                self.audioplayer.set_volume(self.tts.get_volume())

    def run(self):
        logger.info("VoiceAssistant gestartet...")
        try:
            while True:
                pcm = self.audio_stream.read(self.porc.frame_length)
                pcm_unpacked =  struct.unpack_from("h" * self.porc.frame_length, pcm)
                keyword_index = self.porc.process(pcm_unpacked)
                if keyword_index >= 0 and not self.is_listening: # -1, if no keyword was detected
                    logger.info("Wakeword '{}' erkannt. Wie kann ich dir helfen?",  self.wakewords[keyword_index])
                    self.is_listening = True
                    tmp = True
                if self.is_listening:
                    if self.audioplayer.is_playing() and tmp:
                        self.audioplayer.set_volume(self.mute_volume)
                        tmp = False
                    if self.spotify.is_playing and tmp:
                        self.spotify.set_volume(self.mute_volume)
                        tmp = False

                    if self.recognizer.AcceptWaveform(pcm):
                        result = json.loads(self.recognizer.Result())
                        # logger.info('Result: {}', result)
                        sentence = result['text']

                        self.intents.load_snips_model(sentence, self.language)
                        output = self.intents.process()

                        logger.info("Ich habe '{}' verstanden.", sentence)
                        logger.info("Chatbot Ausgabe: '{}'.", output)
                        self.tts.say(output)
                        self.is_listening = False
                                
                else:
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
    multiprocessing.set_start_method("spawn")
    va = VoiceAssistant()
    va.run()