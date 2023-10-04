from langchain.tools import BaseTool
import global_variables

class CustomGetVolumeTool(BaseTool):
    name = "get_volume"
    description = "useful when you want to retrieve the current volume of the assistant Luna. The function takes no input parameter."

    def _run(self) -> str:
        return get_volume() + "\n\n"

    async def _arun(self) -> str:
        raise NotImplementedError("custom_volume does not support async")

def get_volume():
    try:
        volume = global_variables.tts.get_volume()
        volume = volume * 100
        engine = global_variables.tts.get_voice_engine()
        if engine == "gTTS":
            return f"The current volume is {int(volume)}%. The volume range is betweeen 0% and 150%."
        else:
            return f"The current volume is {int(volume)}%. The volume range is betweeen 0% and 100%."
    except:
        return "An unhandled error occurred in the get_volume intent. Could not get the current volume."