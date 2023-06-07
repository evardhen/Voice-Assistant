import dotenv

def wiki_gpt(query, chatbot):
    dotenv.load_dotenv()
    return chatbot.agent_chain.run(input=query)

    
    
    