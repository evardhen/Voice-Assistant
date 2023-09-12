from langchain.tools import BaseTool
import global_variables

class CustomSetVoiceSpeedTool(BaseTool):
    name = "set_voice_speed"
    description = "useful when you want to change the voice speed of the assistant Luna. The voice speed is between 100 and 200. In some languages, like the german language, a float is serarated by a comma. Python allows this separation only with a \".\". Please change the volume to that format."

    def _run(self, voice_speed: str) -> str:
        return set_voice_speed(voice_speed) + "\n\n"

    async def _arun(self, voice_speed: str) -> str:
        raise NotImplementedError("custom_set_voice_speed does not support async")

def set_voice_speed(voice_speed):
    voice_speed = float(voice_speed)
    old_voice_speed = global_variables.tts.get_voiceSpeed()

    if voice_speed >= 150 and voice_speed <= 200:
        global_variables.tts.set_voiceSpeed(voice_speed)
        return f"Successfully changed volume from {old_voice_speed} to {voice_speed}."
    elif (voice_speed < 150 or voice_speed > 200):
        return f"Could not change the volume. The volume has to be between 100 and 200, but you entered {voice_speed}"
    else:
        return "Not defined error in volume_handler."