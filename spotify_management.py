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

class Spotify():
    def __init__(self, volume):
        self.is_playing = False
        config_path = os.path.join("./intents/functions/start_spotify/config_start_spotify.yaml")
        with open(config_path, "r") as file:
            self.config_file = yaml.load(file, Loader=yaml.FullLoader)

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
        self.volume_percent = self._volume_abs_to_percent(volume)
        client_id = os.environ.get('SPOTIPY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
        scope="user-read-playback-state,user-modify-playback-state,user-read-private,user-read-email,playlist-read-private,playlist-read-collaborative,user-library-read"

        # Initialize Spotipy with your credentials
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
        # Find the ID of the device you want to use
        self.device_id = None
        devices = self.sp.devices()
        for device in devices['devices']:
            logger.debug("Gerätename: {}", device['name'])
            name = "LAPTOP-991DG25U"
            # name = "HENRI"
            if device['name'] == name: # Replace 'your_device_name' with the name of your device
                self.device_id = device['id']
                break
        if not self.device_id:
            logger.error("Keine Spotifyanwendung erkannt.")

    def play_spotify(self, spotify_query, query_type):
        self.spotify_query = spotify_query
        # convert text numbers to real numbers
        self.modified_query = text2numde.sentence2num(self.spotify_query)
        # eliminate unnecessary spaces
        self.modified_query = re.sub(' +', ' ', self.modified_query)

        # If a query time is set and detected, play the first query result of that type
        if query_type:
            return self._play_query_type(query_type)

        # Search for a playlist in current user's playlists beforehand, because we most often want to play a user's playlist
        if result := self._play_user_playlists():
            return result

        # General Search: Search for the item based on the search self.spotify_query
        return self._play_unknown_query_type()

    def _play_unknown_query_type(self):
        #TODO: Similarity score müsst je nach Anfrage angepasst werden, zurZeit inaktiv
        search_result = self.sp.search(q=self.modified_query, limit=1)
        self.sp, context_uri = self._set_playback_options(self.sp, self.modified_query)
        similarity_score = fuzz.ratio(search_result['tracks']['items'][0]['name'].lower(), self.spotify_query.lower())
        modified_similarity_score = fuzz.ratio(search_result['tracks']['items'][0]['name'].lower(), self.modified_query.lower())
        logger.debug("Ähnlichkeit der Anfrage und der Spotifysuche: {}, {}: {}",search_result['tracks']['items'][0]['name'].lower(), self.spotify_query.lower(), similarity_score)
        logger.debug("Ähnlichkeit der angepassten Anfrage und der Spotifysuche: {}, {}: {}",search_result['tracks']['items'][0]['name'].lower(), self.modified_query.lower(), modified_similarity_score)

        self._start_playback(context_uri, search_result['tracks']['items'][0]['type'])
        return ""

    def _play_query_type(self, query_type):
        best_match = None
        best_score = None
        for query_name, type in self.config_file["intent"]["start_spotify"]["query_types"].items():
            _, score = process.extractOne(query_type, type, scorer=fuzz.token_sort_ratio)
            if best_score is None or best_score < score:
                best_match, best_score = query_name, score

        if best_match in ['track', 'album', 'artist']:
            self.sp, context_uri = self._set_playback_options(best_match)
        elif best_match == 'playlist':
            if result := self._play_user_playlists():
                return result
            search_result = self.sp.search(q=self.modified_query, type="playlist", limit=1)
            context_uri = search_result['playlists']['items'][0]['uri']
            self.sp.repeat(self.config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["repeat"])
            self.sp.shuffle(self.config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["shuffle"])
        else:
            logger.error("Musiktyp konnte nicht erkannt werden. Es liegt ein Fehler in der Implementierung vor")
        self._start_playback(context_uri, type=best_match)
        return ("Spiele {}.", self.modified_query)

    def _start_playback(self, uri, type = None):
        self.sp.transfer_playback(device_id=self.device_id, force_play=False)
        self.sp.volume(volume_percent=self.volume_percent, device_id=self.device_id)
        if type is not None and (type == "playlist" or type == "album" or type == "artist"):
            self.sp.start_playback(device_id=self.device_id, context_uri=uri)
        else:
            self.sp.start_playback(device_id=self.device_id, uris=[uri])
        self.is_playing = True

    def _play_user_playlists(self):
        playlists = self.sp.current_user_playlists()
        for playlist in playlists['items']:
            ratio = max(fuzz.ratio(playlist['name'].lower(), self.spotify_query.lower()), fuzz.ratio(playlist['name'].lower(), self.modified_query.lower()))
            if ratio > 70:
                logger.debug("Erkannte Playlist: {}", playlist["name"])
                self.sp.repeat(self.config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["repeat"])
                self.sp.shuffle(self.config_file["intent"]["start_spotify"]["query_type_options"]["playlist"]["shuffle"])
                self._start_playback(uri = playlist["uri"], type = "playlist")
                self.is_playing = True
                return ("Spiele Playlist {}", playlist['name'])
        return None

    def _set_playback_options(self, item_type = None):
        if item_type:
            search_result = self.sp.search(q=self.modified_query, type=item_type, limit=1)
        else:
            search_result = self.sp.search(q=self.modified_query, limit=1)
            item_type = search_result['tracks']['items'][0]['type']

        self.sp.repeat(self.config_file["intent"]["start_spotify"]["query_type_options"][item_type]["repeat"])
        self.sp.shuffle(self.config_file["intent"]["start_spotify"]["query_type_options"][item_type]["shuffle"])
        if item_type == "track":
            context_uri = search_result['tracks']['items'][0]['uri']
        elif item_type == "album":
            context_uri = search_result['albums']['items'][0]['uri']
        elif item_type == "playlist":
            context_uri = search_result['playlists']['items'][0]['uri']
        elif item_type == "artist":
            context_uri = search_result['artists']['items'][0]['uri']
        else:
            return logger.debug("Spotify konnte die Anfrage {} nicht finden.", self.modified_query)
        return self.sp, context_uri

    def stop(self):
        self.sp.pause_playback(device_id=self.device_id)
        self.is_playing = False

    def _volume_abs_to_percent(self, volume):
        if volume > 2:
            logger.debug("Lautstärke von {} wirda uf 2 maximal begrenzt.", volume)
            volume = 2
        return int(volume * 100)

    def get_volume(self):
        return self.volume / 100.

    def set_volume(self, volume):
        self.volume_percent = self._volume_abs_to_percent(volume)
        self.sp.volume(volume_percent=self.volume_percent, device_id=self.device_id)
        logger.debug("Spotify Lautstärke auf {} Prozent gesetzt.", self.volume_percent)
