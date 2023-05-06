import unittest
import time
import os, sys
import dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
dir = os.path.join(os.path.dirname(__file__), '../intents/functions/start_spotify/')
sys.path.insert(0, dir)
#import intent_start_spotify


class StartSpotifyTest(unittest.TestCase):

    def test_play_spotify(self):
        #intent_start_spotify.start_spotify("Perfekt", "track")
        dotenv.load_dotenv()

        # Get the spotify credentials from environment variables
        CLIENT_ID = os.environ.get('SPOTIFY_USERNAME')
        CLIENT_SECRET = os.environ.get('SPOTIFY_PASSWORD')
        REDIRECT_URI = os.environ.get('SPOTIFY_URI')
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI))
        # Set the Spotify URI of the album or playlist you want to play
        search_result = sp.search(q="Perfekt", limit=1)
        uri = search_result['tracks']['items'][0]['uri']

        # Start playback for the specified album or playlist URI
        sp.start_playback(context_uri=uri)
if __name__ == '__main__':
    unittest.main()
