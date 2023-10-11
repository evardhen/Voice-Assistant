import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import dotenv
from typing import Optional
from langchain.tools import BaseTool
from fuzzywuzzy import fuzz

import global_variables 

dotenv.load_dotenv()
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')
SCOPE="user-read-playback-state,user-modify-playback-state,user-read-private,user-read-email,playlist-read-private,playlist-read-collaborative,user-library-read"

class CustomSpotifyTool(BaseTool):
    name = "custom_spotify_playback"
    description = "Lets you specify a song, artist, album, or playlist to play on Spotify. The 4 categories are captured in a string and comma separated without spaces. The order of the categories is always song, artist, album, playlist. If one of the categories is empty, the part of the string should display \"null\" as string. An example string is \"null, Ed Sheeran, null, null\n."

    def _run(self, string) -> str:
        return parsing_spotify_player(string)
    def _arun(self, string) -> str:
        raise NotImplementedError("This tool does not support async")

def parsing_spotify_player(string):
    a, b, c, d = (part.strip() for part in string.split(","))
    return spotify_player(str(a), str(b), str(c), str(d))

def spotify_player(song_title: Optional[str] = None, artist_name: Optional[str] = None, album_name: Optional[str] = None, playlist_name: Optional[str] = None) -> str:
    """
    Lets you specify a song, artist, album, or playlist to play on Spotify.
    """
    if global_variables.radio_player.is_playing():
        global_variables.radio_player.stop()
        
    try:
        spotify_player = SpotifyPlayer()

        if song_title and artist_name and song_title != "null" and artist_name != "null":
            song_info = spotify_player.play_song_from_artist(song_title, artist_name)
            global_variables.spotify._is_playing = True
            return f"Playing {song_info['name']} by {song_info['artists'][0]['name']} 1 \n"
        if song_title and song_title != "null":
            song_info = spotify_player.play_song(song_title)
            global_variables.spotify._is_playing = True
            return f"Playing {song_info['name']} by {song_info['artists'][0]['name']} 2 \n"
        if artist_name and artist_name != "null":
            song_info = spotify_player.play_artist(artist_name)
            global_variables.spotify._is_playing = True
            return "Playing songs by " + artist_name + "3\n"
        if album_name and album_name != "null":
            song_info = spotify_player.play_album(album_name)
            global_variables.spotify._is_playing = True
            return "Playing the album " + album_name + "4\n"
        if playlist_name and playlist_name != "null":
            song_info = spotify_player.play_playlist(playlist_name)
            global_variables.spotify._is_playing = True
            return "Playing songs from the playlist " + playlist_name + "5\n"
    except Exception as e:
        return f"Error in spotify_intent: {e}"

class SpotifyPlayer:
    def __init__(self):
        SPOTIFY_AUTH=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
        ACCESS_TOKEN = SPOTIFY_AUTH.get_access_token(as_dict=False)
        self.sp = spotipy.Spotify(ACCESS_TOKEN)
        # Get the user's available devices
        try:
            self.devices = self.sp.devices()
        except Exception as e:
            if str(e).find("The access token expired") != -1:
                raise Exception("Your Spotify access token has expired.")
            elif str(e).find("Invalid access token") != -1:
                raise Exception("Invalid spotify access token.")
            raise Exception("Can't get devices list: " + str(e))

        # assuming the first device is the one we want
        try:
            self.device_id = self.devices["devices"][0]["id"]
            if not self.device_id:
                raise Exception("No device found, please make sure you have one connected.")
        except Exception as e:
            raise Exception("Can't get device id: " + str(e))
        
        global_variables.spotify.set_volume(global_variables.tts.get_volume())
        


    def play_song_from_artist(self, song_name, artist_name):
        # Search for the song
        results = self.sp.search(
            q=f"track:{song_name} artist:{artist_name}", limit=1, type="track"
        )

        # Get the first song from the search results
        song_uri = results["tracks"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, uris=[song_uri])
        return results["tracks"]["items"][0]

    def play_song(self, song_name):
        # Search for the song
        results = self.sp.search(q=song_name, limit=1, type="track")

        # Get the first song from the search results
        song_uri = results["tracks"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, uris=[song_uri])
        return results["tracks"]["items"][0]

    def play_artist(self, artist_name):
        # Search for the artist
        results = self.sp.search(q=artist_name, limit=1, type="artist")

        # Get the first artist from the search results
        artist_uri = results["artists"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=artist_uri)
        return results["artists"]["items"][0]

    def play_album_from_artist(self, album_name, artist_name):
        # Search for the album
        results = self.sp.search(
            q=f"{album_name} artist:{artist_name}", limit=1, type="album"
        )

        # Get the first album from the search results
        album_uri = results["albums"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=album_uri)
        return results["albums"]["items"][0]

    def play_album(self, album_name):
        # Search for the album
        results = self.sp.search(q=album_name, limit=1, type="album")

        # Get the first album from the search results
        album_uri = results["albums"]["items"][0]["uri"]

        # Start playback
        self.sp.start_playback(device_id=self.device_id, context_uri=album_uri)
        return results["albums"]["items"][0]

    def play_playlist(self, playlist_name):
        # Search for the playlist in current users playlists first
        playlists = self.sp.current_user_playlists()
        for playlist in playlists['items']:
            ratio = fuzz.ratio(playlist['name'].lower(), playlist_name.lower())
            if ratio > 70:
                self.sp.start_playback(device_id=self.device_id, context_uri=playlist["uri"])
                return (playlist['name'])
            
        # Search for all playlists
        results = self.sp.search(q=playlist_name, limit=1, type="playlist")
        playlist_uri = results["playlists"]["items"][0]["uri"]
        self.sp.start_playback(device_id=self.device_id, context_uri=playlist_uri)
        return results["playlists"]["items"][0]