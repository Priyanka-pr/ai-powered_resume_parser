from ollama import Client
from config import Config

# client = Client(
#   host='http://172.16.6.163:11434',
#   headers={'x-some-header': 'some-value'}
# )
# print(f"client: {client}")
# response = client.chat(model="mistral-nemo", messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   }
# ])
# print(f"Response: {response}")
# from ollama import chat
# from ollama import ChatResponse

# response = chat(model='mistral-nemo', messages=[
#   {
#     'role': 'user',
#     'content': 'Why is the sky blue?',
#   },
# ])
# print(response['message']['content'])
# # or access fields directly from the response object
# print(response.message.content)

client = Client(
  host=Config.LOCALHOST,
  headers={'x-some-header': 'some-value'}
)
response = client.chat(model=Config.MODEL, messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
print(f"res :: {response}")