from langchain.tools import BaseTool
import global_variables

class CustomSetVolumeTool(BaseTool):
    name = "set_volume"
    description = "useful when you want to change the volume of the assistant Luna. The volume is between 0 and 150. In some languages, like the german language, a float is serarated by a comma. Python allows this separation only with a \".\". Please change the volume to that format."

    def _run(self, volume: str) -> str:
        return set_volume(volume) + "\n\n"

    async def _arun(self, volume: str) -> str:
        raise NotImplementedError("custom_volume does not support async")

def set_volume(volume):
    volume = float(volume)
    volume = volume / 100
    old_volume = global_variables.tts.get_volume()

    # if global_variables.tts.voice_engine == "gTTs":
    #     return "Die Lautstärke von dem gTTS engine kann nicht automatisch angepasst werden, bitte benutzte dafür die Regler am Lautsprecher."
    engine = global_variables.tts.get_voice_engine()
    if engine == "gTTS":
        if volume > 0 and volume <= 1.5:
            global_variables.tts.set_volume(volume)
            return f"Successfully changed volume from {int(old_volume*100)}% to {int(volume*100)}%."
        else:
            global_variables.tts.set_volume(1.5)
            return f"Could not change the volume to {int(volume*100)}. The volume has to be between 0% and 150%. I therefore changed the volume to the maximum of 150%."
    else:
        if volume > 0 and volume <= 1:
            global_variables.tts.set_volume(volume)
            return f"Successfully changed volume from {int(old_volume*100)}% to {int(volume*100)}%."
        else:
            global_variables.tts.set_volume(1)
            return f"Could not change the volume to {int(volume*100)}. The volume has to be between 0% and 100%. I therefore changed the volume to the maximum of 100%."