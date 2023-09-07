from langchain.tools import BaseTool
import global_variables

class CustomChangeVolumeTool(BaseTool):
    name = "change_volume"
    description = "useful when you want to change the volume of the assistant Luna. The volume is between 0 and 3. In some languages, like the german language, a float is serarated by a comma. Python allows this separation only with a \".\". Please change the volume to that format."

    def _run(self, volume: str) -> str:
        return volume_handler(volume) + "\n\n"

    async def _arun(self, volume: str) -> str:
        raise NotImplementedError("custom_volume does not support async")

def volume_handler(volume):
    volume = float(volume)
    old_volume = global_variables.tts.get_volume()

    # if global_variables.tts.voice_engine == "gTTs":
    #     return "Die Lautstärke von dem gTTS engine kann nicht automatisch angepasst werden, bitte benutzte dafür die Regler am Lautsprecher."
    if volume > 0 and volume <= 1.5:
        global_variables.tts.set_volume(volume)
        return f"Successfully changed volume from {old_volume} to {volume}."
    elif (volume <= 0 or volume >1):
        return f"Could not change the volume. The volume has to be between 0 and 1.5, but you entered {volume}"
    else:
        return "Not defined error in volume_handler."