from langchain.tools import BaseTool
import global_variables

class CustomGetVolumeTool(BaseTool):
    name = "get_volume"
    description = "useful when you want to retrieve the current volume of the assistant Luna."

    def _run(self) -> str:
        return get_volume() + "\n\n"

    async def _arun(self) -> str:
        raise NotImplementedError("custom_volume does not support async")

def get_volume():
    try:
        volume = global_variables.tts.get_volume()
        return volume
    except:
        return "An unhandled error occurred in the get_volume intent. Could not get the current volume."