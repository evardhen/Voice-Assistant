from datetime import datetime
import pytz
from langchain.tools import BaseTool

class CustomGetTimeTool(BaseTool):
    name = "get_time"
    description = "useful when you want to get the current time. The function takes no input parameters. Returns a string including the current time."

    def _run(self, query: str) -> str:
        return get_time() + "\n\n"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("custom_get_time does not support async")

def get_time():
    # Define the timezone for Germany
    germany_timezone = pytz.timezone('Europe/Berlin')

    # Get current date and time in Germany
    germany_time = datetime.now(germany_timezone)

    # Format the time
    formatted_time = germany_time.strftime("%H:%M")

    # Return the formatted time
    return f"Current time in Germany: {formatted_time}"