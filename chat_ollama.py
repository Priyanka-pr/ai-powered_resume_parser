import openai
from openai import OpenAI

# client = OpenAI()

# Define the ChatOllama class
# class ChatOllama:
#     def __init__(self, model,temperature,base_url):
#         self.model=model
#         self.temperature=temperature
#         # TODO: The 'openai.api_base' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(base_url=base_url)'
#         # openai.api_base=base_url
        

#     def chat(self, prompt):
#         response = client.chat.completions.create(
#             model=self.model,
#             messages=[{"role":"user","content":prompt}],
#             temperature=self.temperature
#         )
#         return response.choices[0].message.content

# # Initialize ChatOllama with parameters
# base_url_=OpenAI(base_url="http://172.16.6.101:11434")
# llm=ChatOllama(
#     model="mistral-nemo",
#     temperature=0,
#     base_url=base_url_
# )

# # Test the model
# if __name__ == "__main__":
#     user_input = input("what do we call a person who is focused on developing, training, and optimizing LLMs for various applications")
#     response=llm.chat(user_input)
#     print("ChatOllama Response : ", response)

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage
# llm = ChatOllama(
#     model="mistral-nemo",
#     temperature=0.7,
#     base_url="http://172.16.6.101:11434" or "http://127.0.0.1:11434"
# )
# import socket

# ip = "192.168.1.100"
# port = 8080

# try:
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.settimeout(5)  # Timeout after 5 seconds
#     s.connect((ip, port))
#     print(f"Connected to {ip}:{port} successfully!")
#     s.close()
# except Exception as e:
#     print(f"Failed to connect: {e}")
llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0.7,
    # stream=True,
    base_url="http://localhost:11434" 
)
# for chunk in llm:
#   print(chunk, end='', flush=True)
# print(f"llm :: {llm}")
try:
    response = llm.invoke("Tell me a fun fact about space!")
    print("Success! Response:")
    print(response.content)

except Exception as e:
    print(f"Error: {e}")


# from ollama import chat
# from ollama import ChatResponse

# response: ChatResponse = chat(model='llama3.2:1b', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])
# print(response['message']['content'])
# # or access fields directly from the response object
# print(response.message.content)