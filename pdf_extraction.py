from pdf2image import convert_from_path
import pydantic
import json5
import docx2txt
import io
import re
import fitz  # PyMuPDF
import traceback
import logging
from typing import Optional,List
from langchain.prompts import PromptTemplate
from langchain_core.messages.ai import AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders.pdf import PyPDFLoader
# from langchain.output_parsers import PydanticOutputParser, SimpleJsonOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers import StructuredOutputParser
from config import Config
from pydantic import ValidationError
from pydantic import BaseModel, Field

# import langchain.output_parsers
# print(dir(langchain.output_parsers))
# ------------------ Logger Setup ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------ Data Models ------------------

class Experience(BaseModel):
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")
    description: Optional[str] = None

class Study(Experience):
    degree: Optional[str] = None
    university: Optional[str] = None
    country: Optional[str] = None
    grade: Optional[str] = None

class WorkExperience(Experience):
    company: str
    job_title: str = Field(..., alias="jobTitle")

class Certification(BaseModel):
    name: str = Field(..., alias="title")
    date: Optional[str] = None
    issuing_organization: Optional[str] = Field(default=None, alias="issuingOrganization")

class Project(BaseModel):
    name: str = Field(..., alias="title")
    description: Optional[str] = None
    technologies_used: Optional[List[str]] = Field(default_factory=list, alias="technologiesUsed")
class Training(BaseModel):
    name: str = ""
    organization: Optional[str] = None
    date: Optional[str] = None

class Resume(BaseModel):
    full_name: str = Field(..., alias="fullName")
    linkedin_url: Optional[str] = Field(default=None, alias="linkedinUrl")
    email_address: Optional[str] = Field(default=None, alias="emailAddress")
    nationality: Optional[str] = None
    skill: List[str] = Field(default_factory=list)
    hobby: List[str] = Field(default_factory=list)
    study: List[Study] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list, alias="workExperience")
    certification: List[Certification] = Field(default_factory=list)
    trainings: List[Training] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

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
        logger.error(f"Error extracting text from PDF: {e}")
    return text

# ------------------ DOCX Extraction ------------------
def extract_text_from_docx(file_content):
    """Extracts text from a .docx file."""
    try:
        if file_content.startswith(b'\x50\x4b\x03\x04'):
            return docx2txt.process(io.BytesIO(file_content)).strip()
        else:
            logger.warning("Unsupported file type (.docx)")
            return None
    except Exception as e:
        logger.error(f"Error extracting text from .docx file: {e}")
        return None

# ------------------ CV Parsing Logic ------------------
def analyze_cv_from_content(file_content):
    # logger.info("Step 1: Detect file type and extract text")

    try:
        if file_content.startswith(b'%PDF'):
            extracted_text = extract_text_from_pdf(file_content)
        elif file_content.startswith(b'PK'):
            extracted_text = extract_text_from_docx(file_content)
        else:
            logger.warning("Unsupported file type")
            return None
        
        if not extracted_text or len(extracted_text.strip()) < 100:
            logger.warning("Resume content too short or unreadable")
            return None
        # logger.info(f"Step 2: Generate prompt and invoke LLM:: {extracted_text}")

        format_instructions=parser.get_format_instructions()
        # print(f"extracted_text type :: {type(extracted_text)}")
        # extracted_text="name : Priyanka Rana"

        prompt = PromptTemplate(
            template=(
                "You are an intelligent resume parser... Extract information from the following resume:\n\n{format_instructions}\n\n"
                "Resume Text:\n{document}"
            ),
            input_variables=["document"],
            partial_variables={"format_instructions": format_instructions},
        )
        # Step 3: Format input for the prompt
        formatted_prompt = prompt.format(document=extracted_text)
        logger.info(f"prompt ::: {formatted_prompt}")
        # # ------------------ LLM Call ------------------
        llm = ChatOllama(
            model=Config.MODEL,
            temperature=0.7,
            base_url=Config.LOCALHOST
        )
        # logger.info(f"Using LLM model: {Config.MODEL} at {Config.LOCALHOST}")
        # chain = prompt | llm | parser

        # logger.info(f"formatted_prompt LLM model: {formatted_prompt}")
         # Step 5: Send prompt to LLM
        llm_response = llm.invoke(formatted_prompt)
        # logger.debug(f"Raw LLM Response: {llm_response.content}")

        # Step 6: Parse response using the parser
        try:
            parsed_response = parser.parse(llm_response.content)
        except ValidationError as ve:
            print(f"Pydantic parsing failed: {ve}")
            return None
        # parsed_response = parser.parse(llm_response.content)
        # print(f"Parsed Response: {parsed_response}")

        # response = chain.invoke({"document": extracted_text})
        
        # Step 7: Normalize data (Ensure lists are properly formatted)
        # Normalize all list fields
        list_fields = ['skill', 'hobby', 'study', 'projects', 'work_experience', 'certification', 'trainings']
        for field in list_fields:
            val = getattr(parsed_response, field)
            if val and not isinstance(val, list):
                setattr(parsed_response, field, [val])


        # ✅ Fix: Convert incorrect fields
        # response.skill = response.skill if isinstance(response.skill, list) else [response.skill]  
        # response.hobby = response.hobby if isinstance(response.hobby, list) else [response.hobby]  
        # response.study = response.study if isinstance(response.study, list) else [response.study]
        # print(f"LLM Res:::: {response}")
        logger.info(f"Final Parsed Data: {parsed_response}")
        return parsed_response.dict()
        # return response.model_dump()
        # return parsed_response.model_dump_json()
        # return"Hello"
    except Exception as e:
        logger.error(f"Error analyzing CV: {traceback.format_exc()}")
        return None

# ------------------ Save Extracted JSON ------------------
def extract_and_save_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json5.dump(data, f, indent=4)
        # logger.info(f"JSON data successfully saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")

# ------------------ Main Execution ------------------
if __name__ == "__main__":
    file_path = "pdffiles/Naukri_SantoshKumar[0y_0m].pdf"

    with open(file_path, 'rb') as file:
        file_content = file.read()

    # logger.info("Start CV Analysis")
    extracted_data = analyze_cv_from_content(file_content)
    logger.info(f"Extracted Data: {extracted_data}")

    if extracted_data:
        extract_and_save_json(extracted_data, "outputfiles/Naukri_SantoshKumar[0y_0m]/resume_1.json")
