from loguru import logger

def start_spotify(spotify, volume, spotify_query, query_type = None):
    spotify.set_volume(volume)
    return spotify.play_spotify(spotify_query, query_type)
