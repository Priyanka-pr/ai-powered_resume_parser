import os
from langchain_ollama import ChatOllama
OPENAI_API_KEY=""
HUGGINGFACEHUB_API_TOKEN = ""
# I'm omitting all other keys
def set_environment():
    # Set connection with ChatOllama
    # llm = ChatOllama(
    # model="mistral-nemo",
    # temperature=0.7,
    # # stream=True,
    # base_url="http://172.16.6.101:11434" 
    # )

    variable_dict = globals().items()
    for key, value in variable_dict:
        if "API" in key or "ID" in key:
            os.environ[key] = value

