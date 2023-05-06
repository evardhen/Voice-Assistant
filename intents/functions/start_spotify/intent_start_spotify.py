import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from fuzzywuzzy import fuzz, process
import text2numde
import re
import dotenv
from loguru import logger
import yaml
from loguru import logger

#TODO: Speziellere Anfragen, wie "spiele Perfekt von den Ärzten" können noch nicht verarbeitet werdem 

config_path = os.path.join("./intents/functions/start_spotify/config_start_spotify.yaml")
with open(config_path, "r") as file:
    config_file = yaml.load(file, Loader=yaml.FullLoader)


def start_spotify(spotify_query, volume, query_type = None):
    # to enter the credentials of your spotify account, set them as environmental variables on your machine
    # or add them to the '.env' file (listed in .gitignore) beforehand and execute this code
    # Method 1:
    # On Windows:
    # setx SPOTIFY_USERNAME your_username_here
    # setx SPOTIFY_PASSWORD your_password_here
    # setx SPOTIFY_URI your_uri_here
    # On Linux and Mac:
    # export SPOTIFY_USERNAME=your_username_here
    # export SPOTIFY_PASSWORD=your_password_here
    # export SPOTIFY_URI=your_uri_here

    # Method 2:
    # Load environment variables from .env file
    dotenv.load_dotenv()

    # Get the spotify credentials from environment variables
    volume_percent = volume_abs_to_percent(volume)
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    logger.debug(client_id)
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    logger.debug(client_secret)
    redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
    logger.debug(redirect_uri)
    scope="user-read-playback-state,user-modify-playback-state,user-read-private,user-read-email,playlist-read-private,playlist-read-collaborative,user-library-read"

    # Initialize Spotipy with your credentials
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
    # Find the ID of the device you want to use
    device_id = None
    devices = sp.devices()
    for device in devices['devices']:
        logger.debug("Gerätename: {}", device['name'])
        if device['name'] == 'HENRI': # Replace 'your_device_name' with the name of your device
            device_id = device['id']
            break
    if not device_id:
        logger.error("Keine Spotifyanwendung erkannt.")
        return ""
    
    # convert text numbers to real numbers
    modified_query = text2numde.sentence2num(spotify_query)
    # eliminate unnecessary spaces
    modified_query = re.sub(' +', ' ', modified_query)

    # If a query time is set and detected, play the first query result of that type
    if query_type:
        return play_query_type(query_type, sp, modified_query, spotify_query, device_id, volume_percent)

    # Search for a playlist in current user's playlists beforehand, because we most often want to play a user's playlist
    if result := play_user_playlists(spotify_query, modified_query, sp, device_id, volume_percent):
        return result

    # General Search: Search for the item based on the search spotify_query
    return play_unknown_query_type(sp, modified_query, spotify_query, device_id, volume_percent)


def play_unknown_query_type(sp, modified_query, spotify_query, device_id, volume_percent):
    #TODO: Similarity score müsst je nach Anfrage angepasst werden, zurZeit inaktiv
    search_result = sp.search(q=modified_query, limit=1)
    sp, context_uri = set_playback_options(sp, modified_query)
    similarity_score = fuzz.ratio(search_result['tracks']['items'][0]['name'].lower(), spotify_query.lower())
    modified_similarity_score = fuzz.ratio(search_result['tracks']['items'][0]['name'].lower(), modified_query.lower())
    logger.debug("Ähnlichkeit der Anfrage und der Spotifysuche: {}, {}: {}",search_result['tracks']['items'][0]['name'].lower(), spotify_query.lower(), similarity_score)
    logger.debug("Ähnlichkeit der angepassten Anfrage und der Spotifysuche: {}, {}: {}",search_result['tracks']['items'][0]['name'].lower(), modified_query.lower(), modified_similarity_score)

    play_music(sp, device_id, volume_percent, context_uri, search_result['tracks']['items'][0]['type'])
    return ""

def set_playback_options(sp, modified_query, item_type = None):
    if item_type:
        search_result = sp.search(q=modified_query, type=item_type, limit=1)
    else:
        search_result = sp.search(q=modified_query, limit=1)
        item_type = search_result['tracks']['items'][0]['type']
        
    sp.repeat(config_file["intent"]["start_spotify"]["query_type_options"][item_type]["repeat"])
    sp.shuffle(config_file["intent"]["start_spotify"]["query_type_options"][item_type]["shuffle"])
    if item_type == "track":
        context_uri = search_result['tracks']['items'][0]['uri']
    elif item_type == "album":
        context_uri = search_result['albums']['items'][0]['uri']
    elif item_type == "playlist":
        context_uri = search_result['playlists']['items'][0]['uri']
    elif item_type == "artist":
        context_uri = search_result['artists']['items'][0]['uri']
    else:
        return logger.debug("Spotify konnte die Anfrage {} nicht finden.", modified_query)
    return sp, context_uri

def play_query_type(query_type, sp, modified_query, spotify_query, device_id, volume_percent):
    best_match = None
    best_score = None
    for query_name, type in config_file["intent"]["start_spotify"]["query_types"].items():
        _, score = process.extractOne(query_type, type, scorer=fuzz.token_sort_ratio)
        if best_score is None or best_score < score:
            best_match, best_score = query_name, score
            
    if best_match in ['track', 'album', 'artist']:
        sp, context_uri = set_playback_options(sp, modified_query, best_match)
    elif best_match == 'playlist':
        if result := play_user_playlists(spotify_query, modified_query, sp, device_id, volume_percent):
            return result
        search_result = sp.search(q=modified_query, type="playlist", limit=1)
        context_uri = search_result['playlists']['items'][0]['uri']
        sp.repeat(config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["repeat"])
        sp.shuffle(config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["shuffle"])
    else:
        logger.error("Musiktyp konnte nicht erkannt werden. Es liegt ein Fehler in der Implementierung vor")
    play_music(sp, device_id, volume_percent, context_uri, type=best_match)
    return ("Spiele {}.", modified_query)


def play_user_playlists(spotify_query, modified_query, sp, device_id, volume_percent):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        ratio = max(fuzz.ratio(playlist['name'].lower(), spotify_query.lower()), fuzz.ratio(playlist['name'].lower(), modified_query.lower()))
        if ratio > 70:
            logger.debug("Erkannte Playlist: {}", playlist["name"])
            sp.repeat(config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["repeat"])
            sp.shuffle(config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["shuffle"])
            play_music(sp, device_id, volume_percent, playlist["uri"], type="playlist")
            return ("Spiele Playlist {}", playlist['name'])
    return None
    
def play_music(sp, device_id, volume_percent, uri, type = None):
    sp.transfer_playback(device_id=device_id, force_play=False)
    sp.volume(volume_percent=volume_percent, device_id=device_id)
    if type is not None and (type == "playlist" or type == "album"):
        sp.start_playback(device_id=device_id, context_uri=uri)
    else:
        sp.start_playback(device_id=device_id, uris=[uri])

def volume_abs_to_percent(volume):
    if volume > 2:
        logger.debug("Lautstärke von {} wirda uf 2 maximal begrenzt.", volume)
        volume = 2
    return int(volume * 100)

def main():
    start_spotify("Glas", 0.25)


if __name__ == '__main__':
    main()
