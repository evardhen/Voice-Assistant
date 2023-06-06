import dotenv
from langchain.llms import OpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain import OpenAI,ConversationChain,LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.utilities import GoogleSearchAPIWrapper

def wiki_gpt(request_string):
    # LangChain API endpoint
    dotenv.load_dotenv()

    template = """This is a conversation between a human and a bot:

    {chat_history}

    Write a summary of the conversation for {input}:
    """

    prompt = PromptTemplate(
        input_variables=["input", "chat_history"], 
        template=template
    )
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    summry_chain = LLMChain(
        llm=OpenAI(), 
        prompt=prompt, 
        verbose=True, 
        memory=readonlymemory, # use the read-only memory to prevent the tool from modifying the memory
    )
    
    search = GoogleSearchAPIWrapper()
    tools = [
        Tool(
            name = "Search",
            func=search.run,
            description="useful for when you need to answer questions about current events"
        ),
        Tool(
            name = "Summary",
            func=summry_chain.run,
            description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary."
        )
    ]
    
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
    
    llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)
    agent_chain.run(input="What is ChatGPT?")
    agent_chain.run(input="Who developed it?")
    agent_chain.run(input="Thanks. Summarize the conversation, for my daughter 5 years old.")
    print(agent_chain.memory.buffer)
    # template="""Assistant is a large language model trained by OpenAI.

    # Assistant is designed to interact with humans as a chatbot with taks such as answering simple questions to providing in-depth explanations and discussions on a wide range of topics. 
    # As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    # Assistant answers in no more than 4 sentences. At the end of an answer, Assistant asks the human user a question. This question is either supposed to better understand and answer the human user's previous prompt or a general follow up question to keep the conversation going.


    # {history}
    # Human: {human_input}
    # Assistant:"""

    

if __name__ == '__main__':
    wiki_gpt("")
    
    
    