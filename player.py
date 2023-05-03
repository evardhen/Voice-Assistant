from loguru import logger
import time
import os
import ffmpeg
import sounddevice as sd
import soundfile as sf
import multiprocessing
import queue
import numpy as np

class AudioPlayer:
    def __init__(self, volume=0.5):
        self.volume = volume
        self.process = None

    def play_file(self, file):
        self._play(self._play_file, file)

    def play_stream(self, source):
        self._play(self._play_stream, source)

    def _play(self, func, arg):
        if self.process:
            self.stop()
        self.process = multiprocessing.Process(target=func, args=(arg,))
        self.process.start()

    def _play_file(self, file):
        sd.default.reset()
        data, fs = sf.read(file, dtype='float32')
        sd.play(data * self.volume, fs, device=sd.default.device['output'])
        status = sd.wait()
        if status:
            logger.error("Fehler bei der Soundwiedergabe {}.", status)

    def _play_stream(self, source):
        sd.default.reset()
        q = queue.Queue(maxsize=20)
        logger.info("Spiele auf Device {}.", sd.default.device['output'])

        def callback(outdata, frames, time, status):
            if status.output_underflow:
                raise sd.CallbackAbort
            assert not status
            try:
                data = q.get_nowait() * self.volume
            except queue.Empty as e:
                raise sd.CallbackAbort from e
            assert len(data) == len(outdata)
            outdata[:] = data

        try:
            info = ffmpeg.probe(source)
        except ffmpeg.Error as e:
            logger.error(e)

        stream = info.get('streams', [])[0]
        if stream.get('codec_type') != 'audio':
            logger.error("Stream muss ein Audio Stream sein")
        channels = stream['channels']
        samplerate = float(stream['sample_rate'])
        print(channels)
        print(samplerate)

        try:
            process = ffmpeg.input(source).output('pipe:', format='f32le', acodec='pcm_f32le', ac=channels, ar=samplerate, loglevel='quiet').run_async(pipe_stdout=True)
            stream = sd.OutputStream(samplerate=samplerate, blocksize=1024, device=sd.default.device['output'], channels=channels, dtype='float32', callback=callback)
            print(stream.samplesize)
            read_size = 1024 * channels * stream.samplesize
            for _ in range(20):
                data = np.frombuffer(process.stdout.read(read_size), dtype='float32')
                data.shape = -1, channels
                q.put_nowait(data)
            logger.debug("Starte Stream...")
            with stream:
                timeout = 1024 * 20 / samplerate
                while True:
                    data = np.frombuffer(process.stdout.read(read_size), dtype='float32')
                    data.shape = -1, channels
                    q.put(data, timeout=timeout)
        except queue.Full as e:
            logger.error("Streaming-Queue ist voll.")
        except Exception as e:
            logger.error(e)

    def stop(self):
        if self.process:
            self.process.terminate()

    def is_playing(self):
        return self.process and self._process.is_alive()


    def set_volume(self, volume):
        self.volume = max(0.0, min(volume, 1.0))

    def get_volume(self):
        return self.volume




if __name__ == "__main__":
    #player = AudioPlayer("http://mp3channels.webradio.rockantenne.de/classic-perlen")
    player = AudioPlayer(0.3)
    #player.play_file("Do I Wanna Know.wav")
    player.play_file("http://mp3channels.webradio.rockantenne.de/classic-perlen")

    # Wait for 30 seconds before stopping the player
    time.sleep(8)

    player.stop()
