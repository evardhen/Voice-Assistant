import unittest
import time
import os, sys
parent = os.path.abspath('.')
sys.path.insert(1, parent)
from audioplayer import AudioPlayer


class AudioPlayerTest(unittest.TestCase):

    def test_play_audio(self):
        player = AudioPlayer("http://icecast.omroep.nl/3fm-bb-aac")
        player.play()

        # Assert that the player is playing audio
        time.sleep(4)
        # Stop playing audio and assert that the player is no longer playing
        player.stop()


if __name__ == '__main__':
    unittest.main()