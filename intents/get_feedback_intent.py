from langchain.tools import BaseTool
import shutil

class CustomProcessFeedbackTool(BaseTool):
    name = "process_feedback"
    description = "Custom Feedback handling tool. Whenever the user says he has feedback, this tool should be used. The function takes as input parameter a string containing the feedback."

    def _run(self, feedback: str) -> str:
        return process_feedback(feedback) + "\n\n"

    async def _arun(self, feedback: str) -> str:
        raise NotImplementedError("custom_process_feedback does not support async")

def process_feedback(feedback):
    # Specify the file name where feedback will be stored
    file_name = "./feedback/feedback.txt"

    # Open the file in append mode
    with open(file_name, "a") as file:
        # Write the feedback to the file with a newline
        file.write(feedback)

    save_wav_to_feedback("./audios/recorded_audio.wav")

    return f"Your feedback has been successfully saved: {feedback}"

def save_wav_to_feedback(source_file_path):
    # Define the destination folder path
    feedback_folder_path = "./feedback/"

    # Extract the file name from the source path
    file_name = source_file_path.split('/')[-1]

    # Define the destination file path
    destination_file_path = feedback_folder_path + file_name

    # Copy the file from source to destination
    shutil.copy(source_file_path, destination_file_path)

    print(f"File copied to {destination_file_path}.")