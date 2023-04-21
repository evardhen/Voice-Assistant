import pip
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

    def __init__(self,sentence, va, language):
        logger.debug("Starte intent management...")
        self.va = va
        self.language = language
        self.intent_detected = True
        self.dynamic_intents = []
        
        self.load_snips_model(sentence)
        self.import_functions()
        logger.debug("Initialisierung intent management abgeschlossen...")


    def get_dynamic_intent(self):
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
            for slot in self.parser["slots"]:
                arguments[slot["slotName"]] = slot["value"]["value"]
        elif intentName == "interrupt":
            arguments["va"] = self.va
        elif intentName == "wiki":
            for slot in self.parser["slots"]:
                arguments["query"] = slot["value"]["value"]
            arguments["language"] = self.language
        return arguments
    
    def process(self):
        if self.intent_detected:
            return self.get_dynamic_intent()
        return "Kein Intent erkannt."



    def import_functions(self):
        # load files from intents/functions/ folder
        function_folders = [os.path.abspath(name) for name in glob.glob("./intents/functions/*/")]
        for folder in function_folders:
            if not self.parser["intent"]["intentName"]: # Wurde ein Intent erkannt?
                self.intent_detected = False
                logger.debug("Kein Intent erkannt.")
                return
            if Path(folder).name.lower() != self.parser["intent"]["intentName"].lower(): # only load required intent
                continue
            req_file = os.path.join(folder, 'requirements.txt')
            if os.path.exists(req_file):
                self.install_requirements(req_file)
            intent_files = glob.glob(os.path.join(folder, "intent_*.py"))
            for file in intent_files:
                name = file.strip(".py")
                name = "intents.functions." + Path(folder).name + ".intent_" + Path(folder).name
                name = name.replace(os.path.sep, ".")
                globals()[Path(folder).name] = importlib.import_module(name)
                logger.debug("Modul {} geladen.", str(Path(folder).name))
                self.dynamic_intents.append(Path(folder).name)
    
    
    def load_snips_model(self, sentence):
        # detects intents from training files
        # load files from intents/snips_nlu/ folder
        try:
            snips_files = glob.glob(os.path.join("./intents/snips_nlu", '*.yaml'))
            dataset = Dataset.from_yaml_files("de", snips_files)
            nlu_engine = SnipsNLUEngine(CONFIG_DE)
            self.nlu_engine = nlu_engine.fit(dataset)
            self.parser = self.nlu_engine.parse(sentence)
            logger.debug("NLU Objekt: {}", self.parser)
            logger.debug("Konfidenzen: {}", self.nlu_engine.get_intents(sentence))
        except Exception as e:
            logger.error("Snips Engine konnte nicht geladen werden: {}", e)
            sys.exit(1)




    def install_requirements(self, packages):
        with open(packages, 'r') as file:
            for line in file:
                try:
                    pip.main(['install', line.strip()])
                except Exception as e:
                    logger.error("Fehler beim installieren der requirements in install_requirements(), Paket: {}", line.strip())

