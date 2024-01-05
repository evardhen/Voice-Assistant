from langchain.tools import BaseTool
import global_variables

class CustomStopAllMusicTool(BaseTool):
    name = "stop_all_music"
    description = "useful when you want to stop the music played over the assistant Luna. The input parameter is mandatory and always the string \"stop\"."

    def _run(self, tmp: str) -> str:
        return stop_all_music() + "\n\n"

    async def _arun(self, tmp: str) -> str:
        raise NotImplementedError("custom_stop_all_music does not support async")

def stop_all_music():
    try:
        if global_variables.radio_player.is_playing():
            global_variables.radio_player.stop()
        if global_variables.spotify.is_spotify_playing():
            global_variables.spotify.stop()
        return "Successfully stopped playing music."
    except Exception as e:
        return f"Could not stop the music, an error occurred: {e}"
