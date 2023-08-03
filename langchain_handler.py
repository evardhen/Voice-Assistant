from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, load_tools, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
from intents.spotify_intent import spotify_player, CustomSpotifyTool


class LangChainIntegration:
    def __init__(self):
        llm = ChatOpenAI(temperature=0)
        tools = load_tools(
            ["llm-math"],
            llm=llm,
        )
        # spotify_tool = StructuredTool.from_function(spotify_player, return_direct=True)
        tools.extend([CustomSpotifyTool()])

        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.llm_chain = LLMChain(llm=ChatOpenAI(temperature=0), prompt=prompt)
        self.agent = ZeroShotAgent(llm_chain=self.llm_chain, tools=tools, verbose=True)
        self.agent_chain = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=True,
                                                              memory=self.memory)
        self.agent_executor = initialize_agent(tools=tools, llm=llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                           verbose=True)

        

if __name__ == "__main__":
    chatbot = LangChainIntegration()
    query = "Spiele Collide von Ed Sheeran aus dem Album \"=\" auf Spotify."
    try:
        response= chatbot.agent_chain.run(input=query)
    except Exception as e:
            response = str(e)
            if response.startswith("Could not parse LLM output: `"):
                response = " " + response.removeprefix("Could not parse LLM output: `").removesuffix("`")
    print(response)