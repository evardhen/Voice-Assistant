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
import importlib

from intents.spotify_intent import CustomSpotifyTool
from intents.image_identification_intent import ImageCaptionTool

SYSTEM_MESSAGE = SystemMessage(content="Assistant is a large language model trained by OpenAI. Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics." \
                               "As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand. Assistant is" \
                               "constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions." \
                               "Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics. Unfortunately, Assistant is terrible at maths." \
                               "When provided with math questions, no matter how simple, assistant always refers to it's trusty tools and absolutely does NOT try to answer math questions by itself. Overall, Assistant is a powerful system that can help with a wide range of" \
                               "tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist. Assistant always gives short answers.")


class IntentManagement():

    def __init__(self, va):
        self.dynamic_intents = []
        self.va = va
        self.language = va.config['assistant']['language']
        logger.debug("Starte intent management...")

        self.import_modules()
        self.initialize_llm()

    def initialize_llm(self):
        llm = ChatOpenAI(temperature=0)

        tools = load_tools(["llm-math"], llm=llm)
        tools.extend([CustomSpotifyTool(), ImageCaptionTool()])
        prompt = OpenAIFunctionsAgent.create_prompt(system_message=SYSTEM_MESSAGE, extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
   
    def import_modules(self):
        # load files from intents/functions/ folder
        function_folders = [os.path.abspath(name) for name in glob.glob("./intents/functions/*/")]
        for folder in function_folders:
            intent_files = glob.glob(os.path.join(folder, "intent_*.py"))
            for file in intent_files:
                name = file.strip(".py")
                name = "intents.functions." + Path(folder).name + ".intent_" + Path(folder).name
                name = name.replace(os.path.sep, ".")
                globals()[Path(folder).name] = importlib.import_module(name)
                logger.debug("Modul {} geladen.", str(Path(folder).name))
                self.dynamic_intents.append(Path(folder).name)

    def process(self, query):
        return self.agent_executor.run(query)


    def register_callbacks(self):
		# Registriere alle Callback Funktionen
        logger.info("Registriere Callbacks...")
        callbacks = []
        for folder in [os.path.abspath(name) for name in glob.glob("./intents/functions/*/")]:
            module_name = "intents.functions." + Path(folder).name + ".intent_" + Path(folder).name
            module_obj = sys.modules[module_name]
            logger.debug("Verarbeite Modul {}...", module_name)
            if hasattr(module_obj, 'callback'):
                logger.info('Registriere Callback für {}.', module_name)
                callbacks.append(getattr(module_obj, 'callback'))
        return callbacks
