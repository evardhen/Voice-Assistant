from loguru import logger
import pyttsx3
import multiprocessing
from TTS import Voice
import yaml
import sys

CONFIG_FILE = 'config.yml'

class VoiceAssistant():

    def __init__(self):
        global CONFIG_FILE
        default_language = 'de'

        with open(CONFIG_FILE, "r", encoding='utf-8') as file:
            try:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
                logger.debug('YAML Datei erfolgreich geladen.')
            except yaml.YAMLError as exc:
                logger.error(exc)
                sys.exit(1)

        language = self.config['assistant']['language']
        if not language:
            language = default_language
        logger.info('Verwende Sprache {}.', language)

        self.tts = Voice()
        voices = self.tts.get_voice_id(language)
        if len(voices) > 0:
          self.tts.set_voice(voices[0])
          logger.info('Stimme {}', voices[0])

    def run(self):
        logger.info("VoiceAssistant gestartet...")
        self.tts.say("Initialisierung abgeschlossen.")


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")
    va = VoiceAssistant()
    va.run()