from datetime import datetime
from langchain.tools import BaseTool

class CustomGetTimeTool(BaseTool):
    name = "get_time"
    description = "useful when you want to get the current time. Returns a string including the current time."

    def _run(self) -> str:
        return get_time() + "\n\n"

    async def _arun(self) -> str:
        raise NotImplementedError("custom_get_time does not support async")

def get_time():
    # Get current date and time
    current_datetime = datetime.now()
    current_time = current_datetime.time()
    formatted_time = current_time.strftime("%H:%M")
    # Print the current date and time
    return f"Current time: {formatted_time}"