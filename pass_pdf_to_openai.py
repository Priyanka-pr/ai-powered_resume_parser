import os
import json
import re
import io
import fitz  # For PDF handling
import docx2txt
from dotenv import load_dotenv
from openai import OpenAI
from pdf2image import convert_from_bytes
import pytesseract
print(pytesseract.get_tesseract_version())


load_dotenv()

# Function to extract text from PDF using fitz
# def extract_text_from_pdf(file_content):
#     text = ''
#     try:
#         # pdf_document = fitz.open(stream=file_content, filetype="pdf")
#         images = convert_from_bytes(file_content)
#         for img in images:
#             text += pytesseract.image_to_string(img)+"\n"
#         print(text)
#         # for page_num in range(pdf_document.page_count):
#         #     page = pdf_document.load_page(page_num)
#         #     text += page.get_text()
#         # pdf_document.close()
#         # print(text)
#     except Exception as e:
#         print(f"Error extracting text from PDF file: {e}")
#     return text

# # Function to extract text from .docx using docx2txt
# def extract_text_from_docx(file_content):
#     try:
#         if file_content.startswith(b'\x50\x4b\x03\x04'):
#             return docx2txt.process(io.BytesIO(file_content)).strip()
#         else:
#             print("Unsupported file type (.docx)")
#             return None
#     except Exception as e:
#         print(f"Error extracting text from .docx file: {e}")
#         return None

# # Function to analyze CV content 
# def analyze_cv_from_content(file_content):
#     try:
#         if file_content.startswith(b'%PDF'):
#             extracted_text = extract_text_from_pdf(file_content)
#         elif file_content.startswith(b'PK'):
#             extracted_text = extract_text_from_docx(file_content)
#         else:
#             print("Unsupported file type")
#             return None

#         # Define JSON structure for extraction
#         json_structure = {
#             "basic_info": {
#                 "first_name": "", "last_name": "", "phone_number": "",  "email": "", "gender": "", "location": "", 
#                 "linkedin_url": "", "designation": "", "university": "", 
#                 "education_level": "", "graduation_year": "", "graduation_month": ""
#             },
#             "objective": "",
#             "education": [{"degree_certificate": "", "institution": "", "passing_year": "", "completion_year": "", "GPA": ""}],
#             "work_experience": [],
#             "projects": [],
#             "certifications": [],
#             "publications": [],
#             "skills": [],
#             "interests": [],
#             "additional_information": []
#         }

#         prompt = (
#             "Your task is to read, analyze, and extract structured information from the CV. "
#             # "Ensure that the extracted information strictly matches the CV without adding or modifying details. "
#             # "Each education entry should be structured as follows:\n"
#             # "- 'degree_certificate': Extract the full degree name exactly as it appears (e.g., 'B.E. Computer Engineering', 'Secondary School').\n"
#             # "- 'institution': Extract the exact institution name associated with the degree.\n"
#             # "- 'passing_year': Extract only the numerical passing year (e.g., '2022'). If missing, leave blank.\n"
#             # "- 'completion_year': Extract only the numerical completion year if separately mentioned (e.g., '2018'). If missing, leave blank.\n"
#             # "- 'GPA': Extract the GPA, CGPA, or percentage if explicitly stated. If missing, leave blank.\n"
#             # "Sort the extracted education details in **reverse chronological order**, prioritizing the latest education first.\n"
#             # "Ensure that all values are **copied exactly as they appear** in the CV, without assumptions or modifications.\n"
#             # "Format the output in **strict JSON format** as follows:\n"
#             # "[\n"
#             # "  {\n"
#             # "    \"degree_certificate\": \"\",\n"
#             # "    \"institution\": \"\",\n"
#             # "    \"passing_year\": \"\",\n"
#             # "    \"completion_year\": \"\",\n"
#             # "    \"GPA\": \"\"\n"
#             # "  }\n"
#             # "]\n"
#             f"Extracted text: ```{extracted_text}```. "
#             f"Output must strictly follow this JSON structure: ```{json.dumps(json_structure, indent=4)}```."
#         )

#         # Load API key
#         api_key = os.getenv("OPENAI_API_KEY")
#         if not api_key:
#             raise ValueError("Missing OpenAI API Key! Check your .env file.")

#         client = OpenAI(api_key=api_key)

#         messages = [{"role": "system", "content": "You are an expert in extracting structured information from CVs"},
#                     {"role": "user", "content": prompt}]

#         response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
        
#         # # Extract the assistant's message
#         content = response.choices[0].message.content.strip()
        
#         # # Check if response contains JSON in backticks
#         match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
#         if not match:
#             match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        
#         json_data = match.group(1) if match else content  
#         # If no backticks, assume direct JSON
        
#         # # Parse JSON safely
#         parsed_json = json.loads(json_data)

#         return parsed_json
#     except Exception as e:
#         print(f"Error analyzing CV: {e}")
#         return None

# Function to save extracted JSON data
def extract_and_save_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            # f.write(data)
        print(f"JSON data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

def analyze_cv_using_openai_model(file_path):
    print(file_path)
    try:
        apikey= os.getenv("OPENAI_API_KEY")
        if not apikey:
             raise ValueError("Missing OpenAI API Key! Check your .env file.")
        client = OpenAI(api_key=apikey)
        print(f"File exists1:::: {client} ")
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose="user_data"
            )
        # uploaded_file=client.files.create(
        #     file=file_path,
        #     purpose="user_data"
        # )
        # print("File exists")
        # if os.path.exists(file_path):
        #     print("File exists, proceeding...")
        #     with open(file_path, "rb") as file:
        #         uploaded_file = client.files.create(
        #             file=file,
        #             purpose="user_data"
        #         )
        # else:
        #     print(f"Error: File '{file_path}' not found!")
        # Upload file to OpenAI
        # with open(file_path, "rb") as file:
        #     print("Hello")
        #     file_content= file.read()
        #     uploaded_file = client.files.create(
        #         file=file,
        #         purpose="user_data"
        #     )
        
        print("File uploaded successfully")

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
        
        # print(f'next  ::: {uploaded_file}')
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role":"user",
                "content":[
                    {
                        "type":"file",
                        "file": {"file_id": file.id}
                    },
                    {
                        "type":"text",
                        "text":prompts
                    }
                ]
            }
            ]
        )
        print('next1')

        #Extract response content
        content = response.choices[0].message.content.strip()
        print(f'next2: {content}')
        #Parse JSON response safely
        match=re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        print(f'next3: {match}')
        if not match:
            match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        json_data = match.group(1) if match else content #If no backticks, assume direct JSON
        parsed_json= json.loads(json_data)
        print(f'next4: {parsed_json}')

        return parsed_json
    except Exception as e:
        print(f"Error analyzing CV: {e}")
        return None
    


# Main execution
if __name__ == "__main__":
    file_path = "pdffiles/Naukri_RevanthHR[2y_5m].pdf"
    # with open(file_path, 'rb') as file:
    #     file_content = file.read()
    extracted_data = analyze_cv_using_openai_model(file_path)

    if extracted_data:
        extract_and_save_json(extracted_data, "outputfiles/Naukri_RevanthHR[2y_5m]/cv_output_openai_model.json")

