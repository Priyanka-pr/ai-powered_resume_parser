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
def extract_text_from_pdf(file_content):
    text = ''
    try:
        # pdf_document = fitz.open(stream=file_content, filetype="pdf")
        images = convert_from_bytes(file_content)
        for img in images:
            text += pytesseract.image_to_string(img)+"\n"
        print(text)
        # for page_num in range(pdf_document.page_count):
        #     page = pdf_document.load_page(page_num)
        #     text += page.get_text()
        # pdf_document.close()
        # print(text)
    except Exception as e:
        print(f"Error extracting text from PDF file: {e}")
    return text

# Function to extract text from .docx using docx2txt
def extract_text_from_docx(file_content):
    try:
        if file_content.startswith(b'\x50\x4b\x03\x04'):
            return docx2txt.process(io.BytesIO(file_content)).strip()
        else:
            print("Unsupported file type (.docx)")
            return None
    except Exception as e:
        print(f"Error extracting text from .docx file: {e}")
        return None

# Function to analyze CV content
def analyze_cv_from_content(file_content):
    try:
        if file_content.startswith(b'%PDF'):
            extracted_text = extract_text_from_pdf(file_content)
        elif file_content.startswith(b'PK'):
            extracted_text = extract_text_from_docx(file_content)
        else:
            print("Unsupported file type")
            return None

        # Define JSON structure for extraction
        json_structure = {
            "basic_info": {
                "first_name": "", "last_name": "", "phone_number": "",  "email": "", "gender": "", "location": "", 
                "linkedin_url": "", "designation": "", "university": "", 
                "education_level": "", "graduation_year": "", "graduation_month": "","remarks": "Extract personal details carefully. Ensure the phone number follows a standard format."
            },
            "objective": {"text": "","remarks": "Extract the career objective or summary mentioned at the beginning of the resume. If not explicitly mentioned, try to infer from the resume content."},
            "education": [{"degree_certificate": "", "institution": "", "passing_year": "", "completion_year": "", "GPA": "", "remarks": "Ensure all education details are extracted, including missing dates or GPA."}],
            "work_experience": [{"company": "","role": "","start_date": "","end_date": "","responsibilities": "","remarks": "Extract role, company name, and work period. If dates are missing, try to infer them from the resume."}],
            "projects": [],
            "certifications": [],
            "publications": [],
            "skills": [],
            "interests": [],
            "additional_information": []
        }

        prompt = (
            "You are an intelligent resume parser. Your task is to carefully analyze the given resume, "
            "extract relevant structured information, and return the data in a well-formatted JSON structure. "
            "Ensure that no important details are missed, and infer missing information where possible based on context. "
            "Pay special attention to sections like education, work experience, skills, and certifications. "
            "If certain details are missing, return them as empty strings instead of omitting them. "
            "Use the following extracted resume text for analysis: \n\n"
            f"Extracted Resume Text: ```{extracted_text}```. "
            "The extracted information must strictly adhere to this JSON structure:\n"
            f"Output must strictly follow this JSON structure: ```{json.dumps(json_structure, indent=4)}```."
            "Maintain the exact structure and field names while filling in the extracted values."
        )

        # Load API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API Key! Check your .env file.")

        client = OpenAI(api_key=api_key)

        messages = [{"role": "system", "content": "You are an expert in extracting structured information from CVs"},
                    {"role": "user", "content": prompt}]

        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
        
        # # Extract the assistant's message
        content = response.choices[0].message.content.strip()
        
        # # Check if response contains JSON in backticks
        match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if not match:
            match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        
        json_data = match.group(1) if match else content  
        # If no backticks, assume direct JSON
        
        # # Parse JSON safely
        parsed_json = json.loads(json_data)

        return parsed_json
    except Exception as e:
        print(f"Error analyzing CV: {e}")
        return None

# Function to save extracted JSON data
def extract_and_save_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            # f.write(data)
        print(f"JSON data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")


# Main execution
if __name__ == "__main__":
    file_path = "pdffiles/Naukri_RevanthHR[2y_5m].pdf"
    with open(file_path, 'rb') as file:
        file_content = file.read()
    
    extracted_data = analyze_cv_from_content(file_content)

    if extracted_data:
        extract_and_save_json(extracted_data, "outputfiles/Naukri_RevanthHR[2y_5m]/resume.json")

