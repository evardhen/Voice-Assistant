from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.tools import BaseTool


class CustomGoogleSearchTool(BaseTool):
    name = "custom_google_search"
    description = "Useful for when you need to answer questions about current events, people, locations or historic events. Search Google and return the first two results. Always give valid json argument."

    def _run(self, query: str) -> str:
        """Use the tool."""
        search = GoogleSearchAPIWrapper(k=1)
        return search.run(query) + "\n\n"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_google_search does not support async")
