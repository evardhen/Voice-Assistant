import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from fuzzywuzzy import fuzz, process
import text2numde
import re
import dotenv
from loguru import logger


def start_spotify(spotify_query, query_type = None):
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
    CLIENT_ID = os.environ.get('SPOTIFY_USERNAME')
    CLIENT_SECRET = os.environ.get('SPOTIFY_PASSWORD')
    REDIRECT_URI = os.environ.get('SPOTIFY_URI')

    # Initialize Spotipy with your credentials
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI))
    # Set the default options for the playlist, artist, album and track playback
    options = {
        'context_uri': None,
        'repeat_mode': 'context', # Whether to repeat the playlist or not ('off', 'context', 'track')
        'shuffle': True, # Whether to shuffle the playlist or not
    }

    # convert text numbers to real numbers
    modified_query = text2numde.sentence2num(spotify_query)
    # eliminate unnecessary spaces
    modified_query = re.sub(' +', ' ', modified_query)


    # If a query time is set and detected, play the first query result of that type
    if query_type:
        query_types = dict()
        query_types["query_type_artist"] = ["artist", "künstler", "musiker", "interpret", "sänger", "singer"]
        query_types["query_type_album"] = ["album"]
        query_types["query_type_playlist"] = ["playlist"]
        query_types["query_type_track"] = ["song", "lied", "track", "single"]
        best_match, best_score = None
        for query_name, type in query_types:
            _, score = process.extractOne(query_type, type, scorer=fuzz.token_sort_ratio)
            if best_score is None or best_score < score:
                best_match, best_score = query_name, score
        if best_match == 'query_type_track':
            options['repeat_mode'] = 'off'
            search_result = sp.search(q=modified_query, type="track", limit=1)
            options['uri'] = search_result['tracks']['items'][0]['uri']
        elif best_match == 'query_type_album':
            options['repeat_mode'] = 'off'
            search_result = sp.search(q=modified_query, type="album", limit=1)
            options['uri'] = search_result['albums']['items'][0]['uri']
        elif best_match == 'query_type_playlist':
            if search_user_playlists(spotify_query, modified_query, options, sp) is None:
                search_result = sp.search(q=modified_query, type="playlist", limit=1)
                options['uri'] = search_result['playlists']['items'][0]['uri']
            else:
                return search_user_playlists(spotify_query, modified_query, options, sp)
        elif best_match == 'query_type_artist':
            options['repeat_mode'] = 'off'
            options['uri'] = search_result['artists']['items'][0]['uri']
        else:
            logger.error("Musiktyp konnte nicht erkannt werden. Es liegt ein Fehler in der Implementierung vor")
        sp.start_playback(**options)
        return ("Spiele {}.", modified_query)


    # Search for a playlist in current user's playlists
    if search_user_playlists(spotify_query, modified_query, options, sp) is not None:
        return search_user_playlists(spotify_query, modified_query, options, sp)

    # Search for the item based on the search spotify_query
    search_result = sp.search(q=modified_query, limit=1)
    # Get the URI of the item to play
    item_type = search_result['tracks']['items'][0]['type']
    if item_type == 'track':
        options['repeat_mode'] = 'off'
        options['uri'] = search_result['tracks']['items'][0]['uri']
    elif item_type == 'album':
        options['repeat_mode'] = 'off'
        options['uri'] = search_result['albums']['items'][0]['uri']
    elif item_type == 'playlist':
        options['uri'] = search_result['playlists']['items'][0]['uri']
    elif item_type == 'artist':
        options['repeat_mode'] = 'off'
        options['uri'] = search_result['artists']['items'][0]['uri']
    else:
        return logger.debug("Spotify konnte die Anfrage {} nicht finden.", modified_query)
    if fuzz.ratio(search_result['tracks']['items'][0]['name'].lower(), spotify_query.lower()) > 70 \
                or fuzz.ratio(search_result['tracks']['items'][0]['name'].lower(), modified_query.lower()) > 70:
        sp.start_playback(**options)
    else:
        logger.debug("Die Anfragen {} und {} konnten nicht zugeorgdnet werden.", spotify_query, modified_query)
    return ""

def search_user_playlists(spotify_query, modified_query, options, sp):
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        ratio = max(fuzz.ratio(playlist['name'].lower(), spotify_query.lower()), fuzz.ratio(playlist['name'].lower(), modified_query.lower()))
        if ratio > 70:
            options['context_uri'] = playlist['uri']
            sp.start_playback(**options)
            return ("Spiele Playlist {}", playlist['name'])
    return None