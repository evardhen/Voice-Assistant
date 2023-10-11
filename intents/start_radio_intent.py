import yaml
import text2numde
from fuzzywuzzy import fuzz
import os
import re
from loguru import logger
import random
from langchain.tools import BaseTool
import global_variables
from audioplayer import AudioPlayer
from voice_management import Voice

class CustomStartRadioTool(BaseTool):
    name = "start_radio"
    description = "useful when you want to play radio. The input is the name of the radio station."

    def _run(self, station_name: str) -> str:
        return start_radio(station_name) + "\n\n"

    async def _arun(self, station_name: str) -> str:
        raise NotImplementedError("custom_set_voice_speed does not support async")
    
def start_radio(name):
    if global_variables.spotify.is_spotify_playing():
        global_variables.spotify.stop()

    config_path = os.path.join("./intents/config_start_radio.yaml")
    with open(config_path, "r", encoding="utf-8") as file:
        config_file = yaml.load(file, Loader=yaml.FullLoader)
    station_dict = config_file['intent']['start_radio']['radio_station']

    station_name, URL = find_best_match(name, station_dict)
    if station_name != None:
        global_variables.radio_player.set_volume(global_variables.tts.get_volume())
        global_variables.radio_player.play_stream(URL)
        return f"Playing the radio station {station_name}"

    # if no slot has been detected, play a random radio stream (see config_start_radio.yaml)
    station_name, URL = random.choice(list(station_dict.items()))
    global_variables.radio_player.set_volume(global_variables.tts.get_volume())
    global_variables.radio_player.play_stream(URL)
    return f"Could not find any station which matched the query. Playing a random radio station {station_name}."

def find_best_match(query, station_dict):
    # convert text numbers to real numbers
    radio_station = text2numde.sentence2num(query)
    # eliminate unnecessary spaces
    radio_station = re.sub(' +', ' ', radio_station)

    best_match = None
    best_score = -1
    
    for station_name, _ in station_dict.items():
        score = fuzz.ratio(radio_station.lower(), station_name.lower())
        if score > best_score and score > 50:
            logger.debug(f"Found radio station: {station_name} with a score of {score}")
            best_match = station_name
            best_score = score
    
    return (best_match, station_dict.get(best_match)) if best_match else (None, None)

if __name__ == "__main__":
    global_variables.tts = Voice(170, 0.5)
    voices = global_variables.tts.get_voice_id("de")
    if len(voices) > 0:
        global_variables.tts.set_voice(voices[0])
        logger.info('Active pytts voice: {}', voices[0])
    global_variables.radio_player = AudioPlayer()
    start_radio("blablabla")