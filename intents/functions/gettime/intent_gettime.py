from datetime import datetime
import pytz
import os
import random
import yaml
from loguru import logger
import pycountry
import gettext

def gettime(va, language, place="default"):
    config_path = os.path.join('intents','functions','gettime','config_gettime.yml')
    language = va.config['assistant']['language']
    
    with open(config_path, 'r', encoding='utf8') as file:
        yml_file = yaml.load(file, Loader=yaml.FullLoader)
    if not yml_file:
        logger.error("Kontne yml file in intent_gettime.py, Funktion gettime() nicht laden.")
    place_unknown = random.choice(yml_file["intent"]["gettime"][language]["place_not_found"])
    place_unknown = place_unknown.format(place)
    
    # no input country, default to local
    if place == "default":
        now = datetime.now()
        time_here = random.choice(yml_file["intent"]["gettime"][language]["time_here"])
        time_here = time_here.format(str(now.hour), str(now.minute))
        return time_here

    if place.lower() == "england": # pycountry only knows GB
        place = "great britain"
        
    timezone = get_timezone(place, language)
    if timezone is None:
        return place_unknown
    
    now = datetime.now(timezone)
    time_at_place = random.choice(yml_file["intent"]["gettime"][language]["time_in_place"])
    time_at_place = time_at_place.format(str(now.hour), str(now.minute), place.capitalize())
    return time_at_place

def get_timezone(country_name, language):
    if language != "en":
        country_code = language_to_english(country_name, language)
    if country_code is None:
        logger.error("Konnte das angegebene Land nicht ins Englische übersetzen: {}", country_name)
        return None
    
    # Get the timezones for the country
    timezones = pytz.country_timezones.get(country_code)
    # Return the first timezone if available
    if timezones:
        return pytz.timezone(timezones[0])
    else:
        logger.error("Keine Zeitzone für diesen Ort verfügbar: {}", country_name)
    
    return None

def language_to_english(country_name, language):
    english_to_language = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[language])
    english_to_language.install()
    _ = english_to_language.gettext

    for english_country in pycountry.countries:
        country_name = country_name.lower()
        language_country = _(english_country.name).lower()
        if language_country == country_name:
            return english_country.alpha_2
    return None