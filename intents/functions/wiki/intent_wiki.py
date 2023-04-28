import wikipedia
import os
import yaml
import random
import re

def wiki(query, language = "de"):
    config_path = os.path.join("intents", "functions", "wiki", "config_wiki.yml")
    with open(config_path, "r", encoding="utf8") as file:
        configFile = yaml.load(file, Loader=yaml.FullLoader)
        
    query = query.strip()
    wikipedia.set_lang(language)
    try:
        sentences = wikipedia.summary(new_query, sentences = 2)
        return remove_brackets(sentences)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                sentences = wikipedia.summary(new_query, sentences = 2)
                return remove_brackets(sentences)
            except Exception:
                pass
    return random.choice(configFile["intent"]["wiki"][language]["unknown_entity"]) # no result found


def remove_brackets(sentences):
    return re.sub("[\(\[].*?[\)\]]", "", sentences)

def remove_brackets(sentences):
    ret = ''
    skipRoundBrackets = 0
    skipSquareBracekts = 0
    for i in sentences:
        if i == '[':
            skipSquareBracekts += 1
        elif i == '(':
            skipRoundBrackets += 1
        elif i == ']' and skipSquareBracekts > 0:
            skipSquareBracekts -= 1
        elif i == ')'and skipRoundBrackets > 0:
            skipRoundBrackets -= 1
        elif skipSquareBracekts == 0 and skipRoundBrackets == 0:
            ret += i
    return re.sub(' +', ' ', ret)