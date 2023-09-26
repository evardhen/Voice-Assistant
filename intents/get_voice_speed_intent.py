from langchain.tools import BaseTool
import global_variables

class CustomGetVoiceSpeedTool(BaseTool):
    name = "get_voice_speed"
    description = "useful when you want to retrieve the current voice speed of the assistant Luna."

    def _run(self) -> str:
        return get_voice_speed() + "\n\n"

    async def _arun(self) -> str:
        raise NotImplementedError("custom_get_voice_speed does not support async")

def get_voice_speed():
    try:
        voice_speed = global_variables.tts.get_voiceSpeed()
        return str(voice_speed)
    except:
        return "An unhandled error occurred in the get_voice_speed intent. Could not get the current voice speed."