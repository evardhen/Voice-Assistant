import requests
from langchain.tools import BaseTool
import subprocess

SHELF_MANIPULATION_PATH = "shelf_manipulation/shelf_manipulation.py" 

class CustomOpenShelfTool(BaseTool):
    name = "open_shelf"
    description = "useful when you want to open one of the shelves in the kitchen, where Luna is located. The function parameter is the name of the shelf either as a written out number represented as string or as a direction, indicating where the shelf is located. The input is always in english. The available options for the input parameter are: \"one\", \"two\", \"three\", \"four\", \"five\", \"left\", \"middle-left\", \"middle\", \"middle-right\", \"right\".  Returns a string, indicating whether the operation succeded."

    def _run(self, shelf_identifier: str) -> str:
        return open_shelf(shelf_identifier) + "\n\n"

    async def _arun(self, shelf_identifier: str) -> str:
        raise NotImplementedError("custom_get_date does not support async")

def open_shelf(shelf_identifier):

    # Replace with the IP address or hostname of your ESP32
    esp32_url = "http://10.42.0.166"  # Use the mDNS hostname

    # Endpoint to switch the relay
    relay_endpoint = "/switch_relay"

    try:
        response = requests.get(esp32_url + relay_endpoint)
        if response.status_code == 200:
            return f"Shelf {shelf_identifier} opened successfully"
        else:
            return f"Failed to open shelf. HTTP Status Code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# if __name__ == "__main__":
#     subprocess.run(["python", SHELF_MANIPULATION_PATH, "open_shelf"])
