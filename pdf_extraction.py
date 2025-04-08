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
from langchain.output_parsers import PydanticOutputParser,OutputFixingParser
from langchain.output_parsers import StructuredOutputParser
from config import Config
import pdfplumber

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

class Resume(pydantic.BaseModel):
    first_name: str = ""
    last_name: str = ""
    linkedin_url: Optional[str] = ""
    email_address: Optional[str] = ""
    nationality: Optional[str] = ""
    skill: Optional[List[str]] = []
    study: Optional[List[Study]] = []
    work_experience: Optional[List[WorkExperience]]=[]
    hobby: Optional[List[str]]=[]

# parser = PydanticOutputParser(pydantic_object=Resume)

base_parser = PydanticOutputParser(pydantic_object=Resume)

# ------------------ PDF Extraction ------------------
def extract_text_from_pdf(file_path):
    print(f"file88888")
    # type(file_path)
    """Extracts text from a PDF file."""
    text = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                print(text)

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
def analyze_cv_from_content(file_path):
    """Analyzes CV content and extracts structured data using AI."""
    print("Step 2: Detect file type and extract text")
    # print(f"file-content----: {file_content}")
    try:
        # if file_content.startswith(b'%PDF'):
        #     print('If')
        extracted_text = extract_text_from_pdf(file_path)
        # elif file_content.startswith(b'PK\x03\x04'):
        # elif file_content.startswith(b'PK'):
        #     extracted_text = extract_text_from_docx(file_path)
        # else:
        #     print("Unsupported file type")
        #     return None

        print("Step 3: Generating prompt")
        print(f"Extracted_text ::: {extracted_text}")


        # # ------------------ LLM Call ------------------
        llm = ChatOllama(
            model=Config.MODEL,
            temperature=0.5,
            base_url=Config.LOCALHOST
        )
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

        prompt = PromptTemplate(
            template="Extract the following from the resume text:\n\nFirst Name, Last Name, Email, Skills.\n\n{format_instructions}Resume Text:\n{document}",
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm | parser
        response = chain.invoke({"document": extracted_text})
        
        # response.skill = response.skill if isinstance(response.skill, list) else [response.skill]  
        # response.hobby = response.hobby if isinstance(response.hobby, list) else [response.hobby]  
        # response.study = response.study if isinstance(response.study, list) else [response.study]
        print(f"LLM Res:::: {response}")
        return response.model_dump()
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
    file_path = "pdffiles/Bhavya_Gupta_Fresher.pdf"



    print("Step 1: Start CV Analysis")
    extracted_data = analyze_cv_from_content(file_path)

    if extracted_data:
        extract_and_save_json(extracted_data, "outputfiles/new_outputs/Bhavya_Gupta_Fresher_llama321b.json")