import openai
import os
import dotenv
from openai import OpenAI
dotenv.load_dotenv()
client = OpenAI()

def whisper(filename):
    audio_file= open(filename, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return transcript.text


def TTS(filename, sentence):
    response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=sentence
    )

    response.stream_to_file(filename)

sentence = "Barack Obama ist ein amerikanischer Politiker und Anwalt, der von 2009 bis 2017 der 44. Pr▒sident der Vereinigten Staaten war. Er ist bekannt f▒r seine historische Wahl als erster afroamerikanischer Pr▒sident der USA. Weitere Informationen finden Sie auf der offiziellen Website von Barack und Michelle Obama oder auf der Obama Foundation Website."
print(sentence)
TTS("./audios/test.wav", sentence)
