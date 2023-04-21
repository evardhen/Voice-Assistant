from datetime import datetime
import pytz
import os
import random
import yaml
from loguru import logger

def gettime(va, place="default"):
    config_path = os.path.join('intents','functions','gettime','config_gettime.yml')
    language = va.config['assistant']['language']
    
    with open(config_path, 'r', encoding='utf8') as file:
        yml_file = yaml.load(file, Loader=yaml.FullLoader)
    if not yml_file:
        logger.error("Kontne yml file in intent_gettime.py, Funktion gettime() nicht laden.")
    
    
    country_timezone_map = {}
    for key, value in yml_file["intent"]["gettime"]["timezones"].items():
        country_timezone_map[key] = value
    
    timezone = None
    for country in country_timezone_map:
        if place.strip().lower() in country_timezone_map[country]:
            timezone = pytz.timezone(country)
            break
    if timezone:
        now = datetime.now(timezone)
        time_at_place = random.choice(yml_file["intent"]["gettime"][language]["time_in_place"])
        time_at_place = time_at_place.format(str(now.hour), str(now.minute), place.capitalize())
        return time_at_place
    elif place == "default":
        now = datetime.now()
        time_here = random.choice(yml_file["intent"]["gettime"][language]["time_here"])
        time_here = time_here.format(str(now.hour), str(now.minute))
        return time_here
    place_unknown = yml_file["intent"]["gettime"][language]["place_not_found"]
    place_unknown = place_unknown.format(place)
    return place_unknown