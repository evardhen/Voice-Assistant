import glob
import os
from loguru import logger
import importlib, importlib.util
from pathlib import Path
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_DE
from snips_nlu.dataset import Dataset
import sys

class IntentManagement():

    def __init__(self, va):
        self.va = va
        self.language = va.config['assistant']['language']
        logger.debug("Starte intent management...")
        self.dynamic_intents = []
        self.import_modules()



    def get_dynamic_intent(self):
        if not self.parser["intent"]["intentName"]: # Wurde ein Intent erkannt?
            logger.debug("Kein Intent erkannt.")
            return
        for intent in self.dynamic_intents:
            if self.parser["intent"]["intentName"].lower() == intent.lower() and self.parser["intent"]["probability"] > 0.45:
                logger.debug("Intent {} wurde erkannt.", intent)
                arguments = self.set_dynamic_arguments(intent)
                return getattr(globals()[intent], intent)(**arguments)
        return "Ich habe dich nicht verstanden."

    def set_dynamic_arguments(self, intentName):
        arguments = dict()
        if intentName.lower() == "gettime":
            arguments["va"] = self.va
            arguments["language"] = self.language
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        elif intentName == "interrupt":
            arguments["va"] = self.va
        elif intentName == "wiki_gpt":
            arguments["chatbot"] = self.va.chatbot
            for slot in self.parser["slots"]:
                arguments["query"] = slot["value"]["value"]
        elif intentName == "reminder":
            arguments["language"] = self.language
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        elif intentName == "set_volume":
            arguments["spotify"] = self.va.spotify
            arguments["voice"] = self.va.tts
            arguments["audioplayer"] = self.va.audioplayer
            arguments["sentence"] = self.sentence
            arguments["language"] = self.language
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        elif intentName == "get_volume":
            arguments["voice"] = self.va.tts
            arguments["language"] = self.language
        elif intentName == "set_voiceSpeed":
            arguments["voice"] = self.va
            arguments["sentence"] = self.sentence
            arguments["language"] = self.language
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        elif intentName == "get_voiceSpeed":
            arguments["voice"] = self.va.tts
            arguments["language"] = self.language
        elif intentName == "start_radio":
            arguments["audioplayer"] = self.va.audioplayer
            arguments["volume"] = self.va.tts.volume
            arguments["language"] = self.language
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        elif intentName == "start_spotify":
            arguments["spotify"] = self.va.spotify
            arguments["volume"] = self.va.tts.volume
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        else:
            return ("{} ist nicht in set_dynamic_arguments() zur Auswahl.", intentName)

        return arguments

    def process(self):
        return self.get_dynamic_intent()



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


    def load_snips_model(self, sentence, language):
        # detects intents from training files
        # load files from intents/snips_nlu/ folder
        try:
            self.sentence = sentence
            snips_files = glob.glob(os.path.join("./intents/snips_nlu", '*.yaml'))
            dataset = Dataset.from_yaml_files(language, snips_files)
            nlu_engine = SnipsNLUEngine(CONFIG_DE)
            self.nlu_engine = nlu_engine.fit(dataset)
            self.parser = self.nlu_engine.parse(sentence)
            logger.debug("NLU Objekt: {}", self.parser)
            logger.debug("Konfidenzen: {}", self.nlu_engine.get_intents(sentence))
        except Exception as e:
            logger.error("Snips Engine konnte nicht geladen werden: {}", e)
            sys.exit(1)

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
