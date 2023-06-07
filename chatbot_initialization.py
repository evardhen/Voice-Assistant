import dotenv
from langchain.llms import OpenAI
from langchain import OpenAI,LLMChain, PromptTemplate
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.utilities import WikipediaAPIWrapper

class Chatbot():
    """
    This class initilizes the openai api. The api uses the below defined tools to have a conversation with a human. It has a memory.
    """
    def __init__(self, language) -> None:
        dotenv.load_dotenv()
        summary_template = """This is a conversation between a human and a bot:

        {chat_history}

        Write a summary of the conversation for {input}:
        """

        prompt = PromptTemplate(
            input_variables=["input", "chat_history"], 
            template=summary_template
        )
        memory = ConversationBufferMemory(memory_key="chat_history")
        readonlymemory = ReadOnlySharedMemory(memory=memory)
        summry_chain = LLMChain(
            llm=OpenAI(), 
            prompt=prompt, 
            verbose=True, 
            memory=readonlymemory, # use the read-only memory to prevent the tool from modifying the memory
        )
        
        google_search = GoogleSearchAPIWrapper()
        wikipedia_search = WikipediaAPIWrapper()
        
        tools = [
            Tool(name = "Google Search", func=google_search.run, description="useful for when you need to answer questions about current events"),
            Tool(name = "Summary", func=summry_chain.run, description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary."),
            Tool(name = "Wikipedia Search", func=wikipedia_search.run, description="useful for when you need to answer questions about scientific problems or facts.")
        ]
        
        prefix = f"""Assistant is a large language model trained by OpenAI.
        Assistant is designed to interact with humans as a chatbot with taks such as answering simple questions to providing in-depth explanations and discussions on a wide range of topics. 
        As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
        Assistant answers in no more than 4 sentences. Instead of answering, Assistant can also ask a question regarding the previous prompt, if Assistant is not sure how to answer the current question or needs more input for a good response. I want you to answer in the following language: {language}. You have access to the following tools:"""
        
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(tools, prefix=prefix, suffix=suffix, input_variables=["input", "chat_history", "agent_scratchpad"])
        
        llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        self.agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)    