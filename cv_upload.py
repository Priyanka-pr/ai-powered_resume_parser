import os  
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) 

file_path = "pdffiles/Naukri_YashDive[2y_6m].pdf"
try:
    with open(file_path, "rb") as file:
        response = client.files.create(file=file,
        purpose="user_data")
        file_id=response.id
        print(f"File uploaded successfully! File ID: {file_id}")
except Exception as e:
    print(f"Error uploading file: {e}")
    exit()

try:
    completion=client.chat.completions.create(model="gpt-4o",
    messages=[
        {
            "role":"user",
            "content":[
                {
                    "type":"file",
                    "file":{
                        "file_id":file_id,
                    }
                }
            ]
        }
    ])

    print("ChatGPT Response:", completion.choices[0].message.content)
except Exception as e:
    print(f"Error in chat completion: {e}")