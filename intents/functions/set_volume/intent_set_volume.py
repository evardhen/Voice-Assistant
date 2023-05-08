import os
import yaml
from loguru import logger
import random

config_path = os.path.join("./intents/functions/set_volume/config_set_volume.yaml")
try:
    with open(config_path, "r", encoding="utf8") as file:
        config_volume = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    logger.error("Konnte config_volume.yaml nicht laden, Fehler: {}", e)


def set_volume(spotify, voice, audioplayer, sentence, language = "de", volume = None):
    if volume:
        if volume < 0 or volume > 10:
            return random.choice(config_volume["intent"]["set_volume"][language]["invalid_volume"])
        old_volume = voice.get_volume()
        voice.set_volume(volume)
        audioplayer.set_volume(volume)
        spotify.set_volume(volume)
        logger.debug("Lautstärke auf {} gesetzt.", voice.get_volume())
        if volume > old_volume:
            message = random.choice(config_volume["intent"]["set_volume"][language]["increase_volume_by_value"])
        if volume < old_volume:
            message = random.choice(config_volume["intent"]["set_volume"][language]["decrease_volume_by_value"])
        if volume == old_volume:
            message = random.choice(config_volume["intent"]["set_volume"][language]["same_volume"])
        return message.format(volume)
    if not sentence:
        logger.error("Sentence wurde nicht als Parameter übergeben: {}", sentence)
        return ""
    if any([x in sentence.lower() for x in ["laut","erhöhe", "loud", "increase"]]):
        old_volume = voice.get_volume()
        voice.set_volume(old_volume + 0.2)
        message = random.choice(config_volume["intent"]["set_volume"][language]["increase_volume"])
        logger.debug("Lautstärke auf {} gesetzt.", voice.get_volume())
    if any([x in sentence.lower() for x in ["leise","niedrig", "quiet", "decrease"]]):
        old_volume = voice.get_volume()
        voice.set_volume(old_volume - 0.2)
        message = random.choice(config_volume["intent"]["set_volume"][language]["decrease_volume"])
        logger.debug("Lautstärke auf {} gesetzt.", voice.get_volume())
    return message.format(volume)
