import requests
from langchain.tools import BaseTool
import subprocess

SHELF_MANIPULATION_PATH = "shelf_manipulation/shelf_manipulation.py" 

class CustomSwitchShelfPositionTool(BaseTool):
    name = "switch_shelf_position"
    description = "useful when you want to open or close one of the shelves in the kitchen, where Luna is located. This tool can both close and open the shelf. The function parameter is the name of the shelf either as a written out number represented as string or as a direction, indicating where the shelf is located. The input is always in english. The available options for the input parameter are: \"one\", \"two\", \"three\", \"four\", \"left\", \"middle-left\", \"middle\", \"middle-right\", \"right\".  Returns a string, indicating whether the operation succeded. Always pass valid json objects."

    def _run(self, shelf_identifier: str) -> str:
        return switch_shelf_position(shelf_identifier) + "\n\n"

    async def _arun(self, shelf_identifier: str) -> str:
        raise NotImplementedError("custom_switch_shelf does not support async")

def switch_shelf_position(shelf_identifier):

    # Replace with the IP address or hostname of your ESP32
    esp32_url = "http://10.42.8.218"  # Use the mDNS hostname

    # Endpoint to switch the relay
    relay_endpoint_left_shelf = "/relay_left_shelf"
    relay_endpoint_middle_left_shelf = "/relay_middle_left_shelf"
    relay_endpoint_middle_right_shelf = "/relay_middle_right_shelf"
    relay_endpoint_right_shelf = "/relay_right_shelf"

    try:
        if shelf_identifier in ["one", "left"]:
            return activate_relay(esp32_url + relay_endpoint_left_shelf, shelf_identifier)
        elif shelf_identifier in ["two", "middle-left"]:
            return activate_relay(esp32_url + relay_endpoint_middle_left_shelf, shelf_identifier)
        elif shelf_identifier in ["three", "middle-right"]:
            return activate_relay(esp32_url + relay_endpoint_middle_right_shelf, shelf_identifier)
        elif shelf_identifier in ["four", "right"]:
            return activate_relay(esp32_url + relay_endpoint_right_shelf, shelf_identifier)
        else:
            return "Unhandled error..."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


def activate_relay(url, shelf_identifier):
    response = requests.get(url)
    print(response.text)
    if response.status_code == 200:
        return f"Shelf {shelf_identifier} switched successfully"
    else:
        return f"Failed to open shelf. HTTP Status Code: {response.status_code}"

# if __name__ == "__main__":
#     subprocess.run(["python", SHELF_MANIPULATION_PATH, "open_shelf"])
