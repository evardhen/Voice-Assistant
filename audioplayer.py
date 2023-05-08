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

	def __init__(self, volume = 0.5):
		self._process = None
		self._volume = volume
		self.process = None

	def play_file(self, file):
		if self._process:
			self.stop()

		self._process = multiprocessing.Process(target=self._play_file, args=(file,))
		self._process.start()

	def play_stream(self, source):
		if self._process:
			self.stop()
		self._process = multiprocessing.Process(target=self._play_stream, args=(source, ))
		self._process.start()

	def _play_file(self, file):
		sd.default.reset()
		data, fs = sf.read(file, dtype='float32')
		sd.play(data * self._volume, fs, device=sd.default.device['output'])
		status = sd.wait()
		if status:
			logger.error("Fehler bei der Soundwiedergabe {}.", status)

	def _play_stream(self, source):
		sd.default.reset()
		_q = queue.Queue(maxsize=20)
		logger.info("Spiele auf Device {}.", sd.default.device['output'])

		def _callback_stream(outdata, frames, time, status):
			if status.output_underflow:
				raise sd.CallbackAbort
			assert not status

			try:
				data = _q.get_nowait()
				data = data * self._volume
			except queue.Empty as e:
				raise sd.CallbackAbort from e
			assert len(data) == len(outdata)
			outdata[:] = data

		try:
			info = ffmpeg.probe(source)
		except ffmpeg.Error as e:
			logger.error(e)

		streams = info.get('streams', [])
		if len(streams) != 1:
			logger.error('Es darf nur genau ein Stream eingegeben werden.')

		stream = streams[0]

		if stream.get('codec_type') != 'audio':
			logger.error("Stream muss ein Audio Stream sein")

		channels = stream['channels']
		samplerate = float(stream['sample_rate'])

		print(channels)
		print(samplerate)

		try:
			self.process = ffmpeg.input(source).output('pipe:', format='f32le', acodec='pcm_f32le', ac=channels, ar=samplerate, loglevel='quiet').run_async(pipe_stdout=True)
			stream = sd.OutputStream(samplerate=samplerate, blocksize=1024, device=sd.default.device['output'], channels=channels, dtype='float32', callback=_callback_stream)
			print(stream.samplesize)
			read_size = 1024 * channels * stream.samplesize
			for _ in range(20):
				data = np.frombuffer(self.process.stdout.read(read_size), dtype='float32')
				data.shape = -1, channels
				_q.put_nowait(data)
			logger.debug("Starte Stream...")
			with stream:
				timeout = 1024 * 20 / samplerate
				while True:
					data = np.frombuffer(self.process.stdout.read(read_size), dtype='float32')
					data.shape = -1, channels
					_q.put(data, timeout=timeout)
		except queue.Full as e:
			logger.error("Streaming-Queue ist voll.")
		except Exception as e:
			logger.error(e)

	def stop(self):
		if self.process:
			self.process.terminate()

	def is_playing(self):
		return self.process and self.process.is_alive()

	def set_volume(self, volume):
		self._volume = max(0.0, min(volume, 1.0))
		if volume > 1.0:
			logger.debug("Die Lautstärke des Audioplayers wird maximal auf 1.0 angehoben, nicht auf den angefragten Wert {}.", volume)

	def get_volume(self):
		return self._volume


if __name__ == "__main__":
    #player = AudioPlayer("http://mp3channels.webradio.rockantenne.de/classic-perlen")
    player = AudioPlayer()
    player.set_volume(0.5)
    #player.play_file("Do I Wanna Know.wav")
    #player.play_stream("http://mp3channels.webradio.rockantenne.de/classic-perlen")
    player.play_stream("http://mp3channels.webradio.rockantenne.de/classic-perlen")
    # Run the player for 10 seconds
    time.sleep(30)

    player.stop()