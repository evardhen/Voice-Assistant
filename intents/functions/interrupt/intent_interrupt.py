from loguru import logger

def interrupt(va):
    if not va.tts.is_busy():
        return "Ich sage doch gar nichts du Lurch!"
    va.tts.stop()
    logger.debug("Voice Assistant wurde gestoppt.")