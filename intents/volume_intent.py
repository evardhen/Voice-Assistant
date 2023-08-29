from langchain.tools import BaseTool
import global_variables

class CustomChangeVolumeTool(BaseTool):
    name = "change_volume"
    description = "useful when you want to change the volume of the assistant Luna. The volume can be changed by a percentage, represented as a 0, or an absolute value, represented by a 1. Absolute values are likely between 0 and 3. Percentages are likely between 5 and 100. If the volume is changes by percentage and the change is negative, the percentage value should be followed by a '-'. This information is captured in a string and comma separated with the value. The first part of the string is always the type followed by a comma followed by the value. An example could look like this: \"0, -10\", or: \"1, 1.3\". Be careful to pass a valid json object."

    def _run(self, query: str) -> str:
        return parser_volume_handler(query) + "\n\n"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("custom_volume does not support async")
    
def parser_volume_handler(query):
    a, b = (part.strip() for part in query.split(","))
    return volume_handler(int(a), float(b))

def volume_handler(type, query):
    old_volume = global_variables.tts.get_volume()

    if type == 0:
        new_volume = (1 + (query / 100)) * old_volume
        new_volume = round(new_volume, 1)
        global_variables.tts.set_volume(new_volume)
        return f"Successfully changed volume from {old_volume} to {new_volume}."
    if type == 1:
        if query > 0 and query < 3:
            global_variables.tts.set_volume(int(query))
            return f"Successfully changed volume from {old_volume} to {query}."
        else:
            return f"Could not change the volume. The volume has to be between 0 and 3, but you entered {query}"
    else:
        return "Undefined query type in volume_intent. Must be either 0 or 1."