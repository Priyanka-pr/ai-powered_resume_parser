from pdf2image import convert_from_path
import pydantic
import json
import docx2txt
import io
import re
import fitz  # PyMuPDF
import traceback
from typing import Optional,List
from langchain.prompts import PromptTemplate
from langchain_core.messages.ai import AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders.pdf import PyPDFLoader
# from langchain.output_parsers import PydanticOutputParser, SimpleJsonOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers import StructuredOutputParser
from config import Config

# import langchain.output_parsers
# print(dir(langchain.output_parsers))

# ------------------ Data Models ------------------
class Experience(pydantic.BaseModel):
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: Optional[str] = ""

class Study(Experience):
    degree: Optional[str] = ""
    university: Optional[str] = ""
    country: Optional[str] = ""
    grade: Optional[str] = ""

class WorkExperience(Experience):
    company: str = ""
    job_title: str = ""

class Certification(pydantic.BaseModel):
    name: str=""
    date: Optional[str] =""
    issuing_organization: Optional[str]=""

class Project(pydantic.BaseModel):
    name: str = ""
    description: Optional[str] = ""
    technologies_used: Optional[List[str]] = []

class Training(pydantic.BaseModel):
    name: str = ""
    organization: Optional[str] = ""
    date: Optional[str] = ""

class Resume(pydantic.BaseModel):
    first_name: str = ""
    last_name: str = ""
    linkedin_url: Optional[str] = ""
    email_address: Optional[str] = ""
    nationality: Optional[str] = ""
    skill: Optional[List[str]] = []
    study: Optional[List[Study]] = []
    projects: Optional[List[Project]] = []
    work_experience: Optional[List[WorkExperience]]=[]
    hobby: Optional[List[str]]=[]
    certification:Optional[List[Certification]]=[]
    trainings:Optional[List[Training]]=[]

parser = PydanticOutputParser(pydantic_object=Resume)

# ------------------ PDF Extraction ------------------
def extract_text_from_pdf(file_content):
    """Extracts text from a PDF file."""
    text = ''
    try:
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        for page in pdf_document:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

# ------------------ DOCX Extraction ------------------
def extract_text_from_docx(file_content):
    """Extracts text from a .docx file."""
    try:
        if file_content.startswith(b'\x50\x4b\x03\x04'):
            return docx2txt.process(io.BytesIO(file_content)).strip()
        else:
            print("Unsupported file type (.docx)")
            return None
    except Exception as e:
        print(f"Error extracting text from .docx file: {e}")
        return None

# ------------------ CV Parsing Logic ------------------
def analyze_cv_from_content(file_content):
    """Analyzes CV content and extracts structured data using AI."""
    print("Step 2: Detect file type and extract text")

    try:
        if file_content.startswith(b'%PDF'):
            extracted_text = extract_text_from_pdf(file_content)
        elif file_content.startswith(b'PK'):
            extracted_text = extract_text_from_docx(file_content)
        else:
            print("Unsupported file type")
            return None

        print("Step 3: Generating prompt")
        print(f"Extracted_text ::: {extracted_text}")

        format_instructions=parser.get_format_instructions()

        prompt = PromptTemplate(
            template="Extract structured resume details.\n{format_instructions}\nResume Text:\n{document}\n",
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        print(f"Generated Prompt: {prompt.template}")
        # Step 3: Format input for the prompt
        formatted_prompt = prompt.format(document=extracted_text)
        print(f"Formatted Prompt: {formatted_prompt}")

        # # ------------------ LLM Call ------------------
        llm = ChatOllama(
            model=Config.MODEL,
            temperature=0.7,
            base_url=Config.LOCALHOST
        )
        print(f"Using LLM model: {Config.MODEL} at {Config.LOCALHOST}")
        # chain = prompt | llm | parser

         # Step 5: Send prompt to LLM
        llm_response = llm.invoke(formatted_prompt)
        print(f"Raw LLM Response: {llm_response}")

        # Step 6: Parse response using the parser
        parsed_response = parser.parse(llm_response.content)
        print(f"Parsed Response: {parsed_response}")

        # response = chain.invoke({"document": extracted_text})
        
        # Step 7: Normalize data (Ensure lists are properly formatted)
        parsed_response.skill = parsed_response.skill if isinstance(parsed_response.skill, list) else [parsed_response.skill]  
        parsed_response.hobby = parsed_response.hobby if isinstance(parsed_response.hobby, list) else [parsed_response.hobby]  
        parsed_response.study = parsed_response.study if isinstance(parsed_response.study, list) else [parsed_response.study]
        print(f"Final Parsed Data: {parsed_response}")

        # ✅ Fix: Convert incorrect fields
        # response.skill = response.skill if isinstance(response.skill, list) else [response.skill]  
        # response.hobby = response.hobby if isinstance(response.hobby, list) else [response.hobby]  
        # response.study = response.study if isinstance(response.study, list) else [response.study]
        # print(f"LLM Res:::: {response}")
        # return response.dict()
        # return response.model_dump()
        return parsed_response.model_dump()
        # return"Hello"
    except Exception as e:
        print(f"Error analyzing CV: {traceback.format_exc()}")
        return None

# ------------------ Save Extracted JSON ------------------
def extract_and_save_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"JSON data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

# ------------------ Main Execution ------------------
if __name__ == "__main__":
    file_path = "pdffiles/Naukri_Rajaraman[3y_0m].pdf"

    with open(file_path, 'rb') as file:
        file_content = file.read()

    print("Step 1: Start CV Analysis")
    extracted_data = analyze_cv_from_content(file_content)

    if extracted_data:
        extract_and_save_json(extracted_data, "outputfiles/Naukri_Rajaraman[3y_0m]/resume_1.json")
