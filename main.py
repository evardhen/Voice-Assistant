from loguru import logger
import pyttsx3
import multiprocessing
from TTS import Voice

class VoiceAssistant():

    def __init__(self):
        self.tts = Voice()
        voiceIds = self.tts.get_voice_id(language='German')
        if len(voiceIds) > 0:
          self.tts.set_voice(voiceIds[0])
    def run(self):
        logger.info("VoiceAssistant gestartet...")
        self.tts.say("Initialisierung abgeschlossen.")


if __name__ == '__main__':
    multiprocessing.set_start_method("spawn")
    va = VoiceAssistant()
    va.run()