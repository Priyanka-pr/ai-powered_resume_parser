from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
apikey= os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=apikey)

file = client.files.create(
    file=open("pdffiles/Naukri_YashDive[2y_6m].pdf", "rb"),
    purpose="user_data"
)

        #Define JSON structure for extraction
json_struct={
    "basic_info":{
    "first_name":"","last_name":"","phone_number": "", "email": "","gender": "","location": "", "linkedin_url": "", "designation": "","university": "","education_level": "", "graduation_year": "", "graduation_month": ""
    },
            "objective":"",
            "education":[{"degree_certificate": "", "institution": "", "passing_year": "", "completion_year": "", "GPA": ""}],
            "work_experience": [],
            "projects": [],
            "certifications": [],
            "publications": [],
            "skills": [],
            "interests": [],
            "additional_information": []
        }

prompts=("Your task is to analyze and extract structured information from the uploaded CV. "
                 "Ensure the extracted information matches the CV without modifications. "
                 "Format the output strictly in the following JSON structure:\n"
                 f"```{json.dumps(json_struct, indent=4)}```")
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "file",
                    "file": {
                        "file_id": file.id,
                    }
                },
                {
                    "type": "text",
                    "text": prompts,
                },
            ]
        }
    ]
)

print(completion.choices[0].message.content)