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
    name: str = ""
    linkedin_url: Optional[str] = ""
    email_address: Optional[str] = ""
    nationality: Optional[str] = ""
    skill: Optional[List[str]] = []
    study: Optional[List[Study]] = []
    certifications:Optional[List[Certification]]=[]
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
        # with pdfplumber.open(file_path) as pdf:
        #     for page in pdf.pages:
        #         text = page.extract_text()
        #         # print(text)

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
            "You are an AI resume parser. Extract structured resume details from the resume text below.\n\n"
            "- Extract ALL information present in the resume and organize it according to the schema provided.\n"
            "- It is CRITICAL to include EVERY SINGLE work experience entry, no matter how brief or old.\n"
            "- Include ALL entries for education, skills, projects, certifications.\n"
            "- Leave fields blank if information is missing. DO NOT invent or hallucinate data.\n"
            "- For skills, separate technical skills, languages, and other competencies.\n"
            "- For dates, maintain the format as it appears in the resume.\n\n"
            "{format_instructions}\n\n"
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
        return response
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
        extract_and_save_json(extracted_data, "outputfiles/new_outputs/Bhavya_Gupta_newww.json")