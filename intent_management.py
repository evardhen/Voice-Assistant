import pip
import glob
import os
from loguru import logger
import importlib, importlib.util
from pathlib import Path
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_DE
from snips_nlu.dataset import Dataset
import random
import json
import sys


class IntentManagement():
    
    def __init__(self):
        self.intent_count = 0
        self.function_folders = [os.path.abspath(name) for name in glob.glob("./intents/functions/*/")]
        self.dynamic_intents = []
        self.import_functions()
    
    
    def process(self, text, speaker):
        pass
    
    def import_functions(self):
        # load files from intents/functions/ folder
        for folder in self.function_folders:
            logger.debug("Scuhe nach Funktionen in {}", folder)
            req_file = os.path.join(folder, 'requirements.txt')
            if os.path.exists(req_file):
                self.install_requirements(req_file)
            intent_files = glob.glob(os.path.join(folder, "intent_*.py"))
            for file in intent_files:
                logger.debug("Lade intent-Datei {}", file)
                name = file.strip(".py")
                name = "intent.functions." + Path(folder).name + ".intent_" + Path(folder).name
                name = name.replace(os.path.sep, ".")
                globals()[Path(folder).name] = importlib.import_module(name)
                self.dynamic_intents.append(Path(folder).name)
                self.intent_count +=1
                
        # load files from intents/snips_nlu/ folder
        snips_files = glob.glob(os.path.join("intents/snips_nlu", ".yml"))
        try:
            snips_engine = SnipsNLUEngine(CONFIG_DE)
            dataset = Dataset.from_yaml_files("de", [snips_files])
            self.output = snips_engine.fit(dataset)
        except Exception as e:
            logger.error("Snips Engine konnte nicht geladen werden.")
            sys.exit(1)
                
                
                
    
    def install_requirements(self, packages):
        with open(packages, 'r') as file:
            for line in file:
                try:
                    pip.main(['install', line.strip()])
                except Exception as e:
                    logger.error("Fehler beim installieren der requirements in install_requirements(), Paket: {}", line.strip())
    
    def get_intent_count(self):
        return self.intent_count
    
    