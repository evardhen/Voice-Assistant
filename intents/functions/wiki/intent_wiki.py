import wikipedia
import os
import yaml
import random

def wiki(query, language = "de"):
    config_path = os.path.join("intents", "functions", "wiki", "config_wiki.yml")
    with open(config_path, "r", encoding="utf8") as file:
        configFile = yaml.load(file, Loader=yaml.FullLoader)
        
    query = query.strip()
    wikipedia.set_lang(language)
    try:
       return wikipedia.summary(query, sentences = 1)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                return wikipedia.summary(new_query, sentences = 1)
            except Exception:
                pass
    return random.choice(configFile["intent"]["wiki"][language]["unknown_entity"]) # no result found