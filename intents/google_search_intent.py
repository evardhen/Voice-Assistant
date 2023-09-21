from langchain import GoogleSearchAPIWrapper
from langchain.tools import BaseTool
from typing import Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

class CustomGoogleSearchTool(BaseTool):
    name = "custom_google_search"
    description = "useful for when you need to answer questions about current events, people, locations or historic events. Always give valid json objects."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""
        search = GoogleSearchAPIWrapper()
        return search.run(query) + "\n\n"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_google_search does not support async")