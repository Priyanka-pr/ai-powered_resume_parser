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
from langchain_core.messages import HumanMessage
from openai import OpenAI
from pydantic import ValidationError
from pydantic import BaseModel

# import langchain.output_parsers
# print(dir(langchain.output_parsers))

# ------------------ Data Models ------------------


class WorkExperience(BaseModel):
    jobTitle: Optional[str]
    companyName: Optional[str]
    startDate: Optional[str]
    endDate: Optional[str]
    location: Optional[str]
    description: Optional[str]


class Education(BaseModel):
    degree: Optional[str]
    fieldOfStudy: Optional[str]
    institutionName: Optional[str]
    startDate: Optional[str]
    endDate: Optional[str]
    grade: Optional[str]


class Project(BaseModel):
    projectTitle: Optional[str]
    description: Optional[str]
    technologiesUsed: Optional[List[str]]
    role: Optional[str]
    duration: Optional[str]


class Certification(BaseModel):
    name: Optional[str]
    issuingOrganization: Optional[str]
    issueDate: Optional[str]
    expirationDate: Optional[str]


class SkillSet(BaseModel):
    technicalSkills: Optional[List[str]]
    languages: Optional[List[str]]
    otherSkills: Optional[List[str]]


class PersonalDetails(BaseModel):
    fullName: Optional[str]
    email: Optional[str]
    phoneNumber: Optional[str]
    address: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    website: Optional[str]


class Resume(BaseModel):
    personalDetails: Optional[PersonalDetails]
    workExperience: List[WorkExperience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    skills: Optional[SkillSet]
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
            for i, page in enumerate(pdf.pages):
                print(f"\n--- Page {i + 1} ---")

                if i == 0:  # Handle only the first page as double column
                    width = page.width
                    height = page.height

                    # Define bounding boxes for columns
                    left_bbox = (0, 0, width / 2, height)
                    right_bbox = (width / 2, 0, width, height)

                    left_text = page.within_bbox(left_bbox).extract_text() or ""
                    right_text = page.within_bbox(right_bbox).extract_text() or ""

                    print("Left Column:\n", left_text)
                    print("Right Column:\n", right_text)

                else:  # All other pages treated normally
                    text = page.extract_text() or ""
                    print(text)


    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

# ------------------ DOCX Extraction ------------------
def extract_text_from_docx(file_content):
    """Extracts text from a .docx file."""
    try:
        if file_content.startswith(b'\x50\x4b\x03\x04'):
            return docx2txt.process()
        else:
            print("Unsupported file type (.docx)")
            return None
    except Exception as e:
        print(f"Error extracting text from .docx file: {e}")
        return None

# ------------------ CV Parsing Logic ------------------
def analyze_cv_from_content(file_path, file_type):
    """Analyzes CV content and extracts structured data using AI."""
    print("Step 2: Detect file type and extract text")
    # print(f"file-content----: {file_content}")
    try:
        # if file_content.startswith(b'%PDF'):
        #     extracted_text = extract_text_from_pdf(file_path)
        
        # elif file_content.startswith(b'PK\x03\x04'):
        # elif file_content.startswith(b'PK'):
        #     extracted_text = extract_text_from_docx(file_path)
        # else:
        #     print("Unsupported file type")
        #     return None
        if file_type == "pdf":
            extracted_text = extract_text_from_pdf(file_path)
        elif file_type == "docx":
            extracted_text = extract_text_from_docx(file_path)

        print("Step 3: Generating prompt")
        print(f"Read_text ::: {extracted_text}")
        print("Step ")
        print("Step ")
        print("Step ")
        print("Step")
        print("Step ")


        # # ------------------ LLM Call ------------------
        llm = ChatOllama(
            model=Config.MODEL,
            temperature=0.5,
            base_url=Config.LOCALHOST,
            streaming=True
        )
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

        prompt = PromptTemplate(
            template=
            "You are an intelligent resume parser. Your task is to extract and return a structured JSON object based on the schema below from the provided resume text.\n\n"
            "- Extract **all available information** from the resume, even if the entries are brief, old, or formatted differently.\n"
            "- Do not make up any information. Leave fields as `null` or `""` if not available in the resume.\n"
            "- Maintain **original formatting for dates**, even if inconsistent.\n"
            "- Ensure **all work experience**, **education**, **skills**, **projects**, **certifications**, and **personal information** are captured.\n"
            "- Classify skills into: `technicalSkills`, `languages`, and `otherSkills`.\n"
            "- For each section, return a list of entries, even if there's only one.\n"
            "- Return the result in strict accordance with the JSON schema shown in {format_instructions}.\n\n"
            "Resume Text:\n{document}",
            # "Extract the following from the resume text:{format_instructions}Resume Text:\n{document}",
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        # formatted_prompt = prompt.format(document=extracted_text)

        chain = prompt | llm | parser
        response = chain.invoke({"document": extracted_text})
        
        # response.skill = response.skill if isinstance(response.skill, list) else [response.skill]  
        # response.hobby = response.hobby if isinstance(response.hobby, list) else [response.hobby]  
        # response.study = response.study if isinstance(response.study, list) else [response.study]
        # print(f"LLM Res:::: {response}")
        print("Hello")
        # Step 1: Stream the raw response
        # raw_response = ""

        # # Stream responses
        # for chunk in llm.stream(formatted_prompt):
        #     print(chunk.content, end="", flush=True)
        #     raw_response += chunk.content
        try:
            parsed = Resume.model_validate(response)
            print(parsed)
        except ValidationError as e:
            print("Validation errors:")
            print(e.json(indent=2))
        return response
    except Exception as e:
        print(f"Error analyzing CV: {traceback.format_exc()}")
        return None

# ------------------ Save Extracted JSON ------------------
# def extract_and_save_json(data, output_file):
#     try:
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(data, f, indent=4)
#         print(f"JSON data successfully saved to {output_file}")
#     except Exception as e:
#         print(f"Error saving JSON: {e}")

def extract_and_save_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Use the dict() method to convert the Pydantic object to a serializable dictionary.
            json.dump(data.dict(), f, indent=4)
        print(f"JSON data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")


# ------------------ Main Execution ------------------
if __name__ == "__main__":
    file_path = "pdffiles/Bhavya_Gupta_Fresher.pdf"
    file_type=""
    with open(file_path, 'rb') as file:
        file_content = file.read()
        if file_content.startswith(b'%PDF'):
            file_type="pdf"
        elif file_content.startswith(b'PK\x03\x04'):
            file_type="docx"
        else:
            print("Unsupported file type")

    print("Step 1: Start CV Analysis")
    if file_type != "":
        extracted_data = analyze_cv_from_content(file_path, file_type)
    

    if extracted_data:
        extract_and_save_json(extracted_data, "outputfiles/new_outputs/Bhavya_Gupta_new_new.json")