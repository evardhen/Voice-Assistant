import os
import yaml
from loguru import logger
import random

config_path = os.path.join("./intents/functions/get_volume/config_get_volume.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as file:
        config_file = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    logger.error("Konnte config_get_volume.yaml nicht laden, Fehler: {}", e)

def get_volume(voice, language = "de"):
    vol = random.choice(config_file["intent"]["get_volume"][language]["current_volume"])
    return vol.format(voice.get_volume())