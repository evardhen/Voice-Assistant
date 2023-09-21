from datetime import datetime
from langchain.tools import BaseTool

class CustomGetDateTool(BaseTool):
    name = "get_date"
    description = "useful when you want to get the current date or the current weekday of the assistant Luna. Returns a string including the current date and the weekday."

    def _run(self) -> str:
        return get_date() + "\n\n"

    async def _arun(self) -> str:
        raise NotImplementedError("custom_get_date does not support async")

def get_date():
    # Get current date and time
    current_datetime = datetime.now()
    # Extract date
    current_date = current_datetime.date()
    formatted_date = current_date.strftime("%d.%m.%Y")

    # Get the day of the week as an integer (0=Monday, 1=Tuesday, ..., 6=Sunday)
    day_of_week_int = current_date.weekday()

    # Define a list of weekday names
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Get the actual name of the day of the week
    day_of_week_name = weekday_names[day_of_week_int]

    # Print the day of the week
    return f"Today is {day_of_week_name}, the {formatted_date}."