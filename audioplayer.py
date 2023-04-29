import sounddevice as sd
import ffmpeg
from multiprocessing import Process, Queue
import sys
from loguru import logger

class AudioPlayer:
    def __init__(self, stream_url, volume = 0.05):
        self.stream_url = stream_url
        self.output_queue = Queue()
        self.process = None
        self.volume_scale = volume

    def play(self):
        if self.process:
            self.stop() 
        self.process = Process(target=self.play_stream)
        self.process.start()

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None

    def play_stream(self):
        sd.default.reset()
        logger.info("Spiele auf Device {}.", sd.default.device['output'])
        # Set up the input stream
        input_stream = ffmpeg.input(self.stream_url)

        # Set up the output stream
        output_stream = ffmpeg.output(input_stream, 'pipe:', format='wav')
        out, _ = output_stream.run(capture_stdout=True)

        # Set up the sound device stream
        stream = sd.OutputStream(channels=2, blocksize=2048, callback=self.audio_callback)
        stream.start()

        # Loop through the output stream and send audio data to the sound device stream
        while True:
            data = out.read(2048)
            if not data:
                break
            self.output_queue.put(data)

        # Stop the sound device stream
        stream.stop()

    def audio_callback(self, outdata, frames, time, status):
        if status:
            logger.error(status, file=sys.stderr)
        if not self.output_queue.empty():
            data = self.output_queue.get_nowait() * self.volume_scale
            outdata[:] = data
        else:
            outdata[:] = 0
            
    def set_volume(self, volume_scale):
        self.volume_scale = volume_scale
    