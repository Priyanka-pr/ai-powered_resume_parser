import os
import json
import traceback
import pdfplumber
import docx2txt
import pydantic
from dotenv import load_dotenv
from typing import Optional, List
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from openai import OpenAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# ------------------ Data Models ------------------

class Education(BaseModel):
    course: str
    institution: str
    location: Optional[str] = None
    year_of_passing: Optional[str] = None
    performance: Optional[str] = None


class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[str] = None


class SkillSet(BaseModel):
    technical_skills: List[str]
    soft_skills: List[str]


class Project(BaseModel):
    title: str
    organization: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    date_range: Optional[str] = None


class PositionOfResponsibility(BaseModel):
    title: str
    organization: str
    description: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class VolunteerWork(BaseModel):
    role: str
    organization: Optional[str] = None
    description: Optional[str] = None


class Resume(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[Education]
    certifications: List[Certification]
    skills: SkillSet
    internships_and_projects: List[Project]
    positions_of_responsibility: List[PositionOfResponsibility]
    volunteer_experience: List[VolunteerWork]
    interests: Optional[List[str]] = None
    remarks:str=""
# Parser based on schema
base_parser = PydanticOutputParser(pydantic_object=Resume)

# ------------------ File Extraction ------------------
def extract_text_from_pdf(file_path):
    text = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                width = page.width
                height = page.height
                if i == 0:
                    left_text = page.within_bbox((0, 0, width / 2, height)).extract_text() or ""
                    right_text = page.within_bbox((width / 2, 0, width, height)).extract_text() or ""
                    text += left_text + "\n" + right_text
                else:
                    text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ""

# ------------------ CV Analyzer ------------------
def analyze_cv_from_content(file_path, file_type):
    try:
        print("📥 Step 1: Extracting text")
        extracted_text = extract_text_from_pdf(file_path) if file_type == "pdf" else extract_text_from_docx(file_path)

        if not extracted_text or not extracted_text.strip():
            print("No text extracted from file.")
            return None

        print(f"🤖 Step 2: Initializing LLM & prompt::: {extracted_text}")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API Key")

        # Use LangChain-compatible LLM
        llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo")

        # Parser setup
        parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

        # Prompt template
        prompt = PromptTemplate(
            template=(
                "You are an AI resume parser. Extract structured resume details from the resume text below.\n\n"
                "- Extract all available details and follow this schema:\n"
                "- If there is no date given than add year only and add it to the start_date key"
                "- Explain the error if my prompt needs corrections"
                "{format_instructions}\n\n"
                "Resume Text:\n{document}"
            ),
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        formatted_prompt = prompt.format(document=extracted_text)
        print("🚀 Step 3: Sending request to LLM")

        # Call LLM via LangChain
        llm_response = llm.invoke(formatted_prompt)

        print("✅ Step 4: Received response")

        response = parser.parse(llm_response.content)
        return response.model_dump()
        # return "hello"

    except Exception as e:
        print(f"Error analyzing CV:\n{traceback.format_exc()}")
        return None
# ------------------ Output Helper ------------------
def extract_and_save_json(data, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"✅ JSON saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

# ------------------ Main Execution ------------------
if __name__ == "__main__":
    file_path = "pdffiles/CV-Kapil_kaushik.pdf"
    file_type = ""

    with open(file_path, 'rb') as file:
        file_content = file.read()
        if file_content.startswith(b'%PDF'):
            file_type = "pdf"
        elif file_content.startswith(b'PK\x03\x04'):
            file_type = "docx"
        else:
            print("Unsupported file type")

    if file_type:
        print("🚦 Starting Resume Parsing...")
        extracted_data = analyze_cv_from_content(file_path, file_type)
        if extracted_data:
            extract_and_save_json(extracted_data, "outputfiles/new_outputs/CV-Kapil_kaushik_2.json")
