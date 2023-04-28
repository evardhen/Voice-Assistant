import os
import yaml
from loguru import logger
import random

config_path = os.path.join("./intents/functions/set_voiceSpeed/config_set_voiceSpeed.yaml")
try:
    with open(config_path, "r", encoding="utf8") as file:
        config_voiceSpeed = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    logger.error("Konnte config_set_voiceSpeed.yaml nicht laden, Fehler: {}", e)


def set_voiceSpeed(voice, sentence, language = "de", voiceSpeed = None):
    if voiceSpeed:
        old_voiceSpeed = voice.get_voiceSpeed()
        voice.set_voiceSpeed(voiceSpeed)
        logger.debug("Geschwindigkeit auf {} gesetzt.", voice.get_voiceSpeed())
        if voiceSpeed > old_voiceSpeed:
            message = random.choice(config_voiceSpeed["intent"]["set_voiceSpeed"][language]["increase_voiceSpeed_by_value"])
        if voiceSpeed < old_voiceSpeed:
            message = random.choice(config_voiceSpeed["intent"]["set_voiceSpeed"][language]["decrease_voiceSpeed_by_value"])
        if voiceSpeed == old_voiceSpeed:
            message = random.choice(config_voiceSpeed["intent"]["set_voiceSpeed"][language]["same_voiceSpeed"])
        return message.format(voiceSpeed)
    if not sentence:
        logger.error("sentence wurde nicht als Parameter übergeben: {}", sentence)
        return ""
    if any([x in sentence.lower() for x in ["schnell", "erhöhe", "fast", "increase"]]):
        old_voiceSpeed = voice.get_voiceSpeed()
        voice.set_voiceSpeed(old_voiceSpeed + 20)
        message = random.choice(config_voiceSpeed["intent"]["set_voiceSpeed"][language]["increase_voiceSpeed"])
        logger.debug("Geschwindikeit auf {} gesetzt.", voice.get_voiceSpeed())
    if any([x in sentence.lower() for x in ["verringer", "langsam", "reduziere", "slow", "decrease"]]):
        old_voiceSpeed = voice.get_voiceSpeed()
        voice.set_voiceSpeed(old_voiceSpeed - 20)
        message = random.choice(config_voiceSpeed["intent"]["set_voiceSpeed"][language]["decrease_voiceSpeed"])
        logger.debug("Geschwindikeit auf {} gesetzt.", voice.get_voiceSpeed())
    return message.format(voiceSpeed)