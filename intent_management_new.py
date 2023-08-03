from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory

from intents.spotify_intent import CustomSpotifyTool
from intents.image_identification_intent import ImageCaptionTool


class IntentManagement():
    def __init__(self, va) -> None:
        pass
llm = ChatOpenAI(temperature=0)

tools = load_tools(["llm-math"], llm=llm)
tools.extend([CustomSpotifyTool(), ImageCaptionTool()])

system_message = SystemMessage(content="Assistant is a large language model trained by OpenAI. Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics." \
                               "As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand. Assistant is" \
                               "constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions." \
                               "Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics. Unfortunately, Assistant is terrible at maths." \
                               "When provided with math questions, no matter how simple, assistant always refers to it's trusty tools and absolutely does NOT try to answer math questions by itself. Overall, Assistant is a powerful system that can help with a wide range of" \
                               "tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.")

prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message, extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

query = "Spiele I See Fire von Ed Sheeran auf Spotify."
query2 = "What is 5+5?"
query3 = "Can you add 7 the the result?"
img_url = 'https://images.unsplash.com/photo-1616128417859-3a984dd35f02?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2372&q=80'
query4 = f"What does this image show?\n{img_url}"
answer = agent_executor.run(query2)
print("Answer: ", answer)
# agent_executor.run(query3)