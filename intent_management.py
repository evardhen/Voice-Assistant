from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, OpenAIFunctionsAgent, AgentExecutor
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.memory import ConversationBufferMemory

import glob
import os
from loguru import logger
from pathlib import Path
import sys
import dotenv
import importlib

from intents.spotify_intent import CustomSpotifyTool
from intents.image_identification_intent import ImageCaptionTool
from intents.google_search_intent import CustomGoogleSearchTool
from intents.set_volume_intent import CustomSetVolumeTool
from intents.get_volume_intent import CustomGetVolumeTool
from intents.set_voice_speed_intent import CustomSetVoiceSpeedTool
from intents.get_voice_speed_intent import CustomGetVoiceSpeedTool

SYSTEM_MESSAGE = SystemMessage(content="Luna is a large language model trained by OpenAI. Luna is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics." \
                               "As a language model, Luna is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide accurate and informative responses that are coherent and relevant to the topic at hand. Luna is" \
                               "constantly learning and improving, and its capabilities are constantly evolving. Luna is located in the ZEKI office kitchen at Technische Universität Berlin. Therefore, it either answers in german or english. Luna always gives very short answers, with no more than 100 words." \
                               "When provided with a question or any other input, no matter how simple, Luna always refers to its trusty tools and absolutely does NOT try to answer questions by itself. If Luna cannot associate an input or question with one of its tools, it gives a very short response, asking the user to repeat the question." \
                                "Overall, Luna is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Luna is here to assist.")


class IntentManagement():

    def __init__(self, va):
        self.dynamic_intents = []
        self.va = va
        self.language = va.config['assistant']['language']
        logger.debug("Starting intent management...")

        self.initialize_llm()

    def initialize_llm(self):
        dotenv.load_dotenv()
        llm = ChatOpenAI(temperature=0)

        # Load predefined tools
        tools = load_tools(["llm-math"], llm=llm)
        # tools = load_tools(["llm-math", "google-search"], llm=llm)

        # Load custom tools/intents
        tools.extend([CustomSpotifyTool(), ImageCaptionTool(), CustomGoogleSearchTool(), CustomGetVolumeTool(), CustomSetVolumeTool(), CustomSetVoiceSpeedTool(), CustomGetVoiceSpeedTool()])

        # Create a prompt
        prompt = OpenAIFunctionsAgent.create_prompt(system_message=SYSTEM_MESSAGE, extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])
        
        # Set up memory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Create agent to select correct intent
        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

    def process(self, query):
        return self.agent_executor.run(query)


    def register_callbacks(self):
		# Register all callback functions
        logger.info("Register callback intents...")
        callbacks = []
        intent_folder = [os.path.abspath(name) for name in glob.glob("./intents/")]
        intent_files = glob.glob(os.path.join(intent_folder[0], "*_intent.py"))
        for file in intent_files:
            module_name = 'intents.' + Path(file).stem
            globals()[Path(file).name] = importlib.import_module(module_name)
            module_obj = sys.modules[module_name]
            if hasattr(module_obj, 'callback'):
                logger.info('Register callback for: {}.', module_name)
                callbacks.append(getattr(module_obj, 'callback'))
        return callbacks
