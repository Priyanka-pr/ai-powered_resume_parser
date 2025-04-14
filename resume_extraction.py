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
    name: str = ""
    date: Optional[str] = ""
    issuing_organization: Optional[str] = ""

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

base_parser = PydanticOutputParser(pydantic_object=Resume)

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



def extract_text_from_pdf(file_path):
    text = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # print(f"\n--- Page {i + 1} ---")

                if i == 0:  # Handle only the first page as double column
                    width = page.width
                    height = page.height

                    # Define bounding boxes for columns
                    left_bbox = (0, 0, width / 2, height)
                    right_bbox = (width / 2, 0, width, height)

                    left_text = page.within_bbox(left_bbox).extract_text() or ""
                    right_text = page.within_bbox(right_bbox).extract_text() or ""
                    print('Divide page into two halves')
                    text += left_text + "\n" + right_text
                else:  # All other pages treated normally
                    text = page.extract_text() or ""
                    print(text)


    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def analyze_cv_from_content(file_path, file_type):
    """Analyzes CV content and extracts structured data using AI."""
    print("Step 2: Detect file type and extract text")
    print(f"file-content----: {file_type}")
    try:
        if file_type == "pdf":
            extracted_text = extract_text_from_pdf(file_path)
            print(f"extracted text::: {extracted_text}")
        elif file_type == "docx":
            extracted_text = extract_text_from_docx(file_path)
            print(f"extracted text::: {extracted_text}")

        if not extracted_text.strip():
            print(repr(extracted_text))


        print("🧠 Step 2: Initialize LLM and parser")
        print("Step ")
        print("Step ")
        print("Step ")

        # # ------------------ LLM Call ------------------
        llm = ChatOllama(
            model=Config.MODEL,
            temperature=0.5,
            base_url=Config.LOCALHOST,
            streaming=True
        )
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)
        print("📄 Step 3: Construct prompt")
        prompt = PromptTemplate(
            template=
            "You are an AI resume parser. Extract structured resume details from the resume text below.\n\n"
            "- Extract ALL information present in the resume and organize it according to the schema provided.\n"
            "- It is CRITICAL to include EVERY SINGLE work experience entry, no matter how brief or old.\n"
            "- Include ALL entries for education, skills, projects, certifications.\n"
            "- Leave fields blank if information is missing. DO NOT invent or hallucinate data.\n"
            "- For skills, separate technical skills, languages, and other competencies.\n"
            "- For dates, maintain the format as it appears in the resume.\n\n"
            "- At the end of the response, include a **remark** indicating what went wrong **if** the JSON is empty or any section is incomplete."
            "{format_instructions}\n\n"
            "Resume Text:\n{document}",
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        print("Extracted Text:::", extracted_text[:500])  
        formatted_prompt = prompt.format(document=extracted_text)
        print("🚀 Step 4: Invoking LLM...")
        llm_response = llm.invoke(formatted_prompt)
        print("🧾 Raw LLM Output:", llm_response.content[:500])
        response = parser.parse(llm_response.content)
        print("✅ Step 5: Parsed response successfully")
        return response.model_dump()
    except Exception as e:
        print(f"Error analyzing CV: {traceback.format_exc()}")
        return None


def extract_and_save_json(data, output_file):
    print(f"LLM Response::: {data}")
    # try:
    #     with open(output_file, 'w', encoding='utf-8') as f:
    #         # Use the dict() method to convert the Pydantic object to a serializable dictionary.
    #         json.dump(data.dict(), f, indent=4)
    #     print(f"JSON data successfully saved to {output_file}")
    # except Exception as e:
    #     print(f"Error saving JSON: {e}")



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
        extract_and_save_json(extracted_data, "outputfiles/new_outputs/Bhavya_Gupta.json")