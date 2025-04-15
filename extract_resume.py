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
from pydantic import BaseModel,Field

# Load environment variables
load_dotenv()

# ------------------ Data Models ------------------

class BasicInfo(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = ""
    email: Optional[str] = ""
    gender: Optional[str] = ""
    location: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    designation: Optional[str] = ""
    university: Optional[str] = ""
    education_level: Optional[str] = ""
    graduation_year: Optional[str] = ""
    graduation_month: Optional[str] = ""


class EducationEntry(BaseModel):
    degree_certificate: str
    institution: str
    passing_year: Optional[str] = ""
    completion_year: Optional[str] = ""
    GPA: Optional[str] = ""


class WorkExperience(BaseModel):
    company_name: str
    job_title: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: Optional[str] = ""


class Project(BaseModel):
    project_name: str
    client: Optional[str] = ""
    role: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    description: Optional[str] = ""


class Certification(BaseModel):
    certification_name: str
    issuer: Optional[str] = ""
    date: Optional[str] = ""
    description: Optional[str] = ""


class Interest(BaseModel):
    interest_name: str
    description: Optional[str] = ""


class Resume(BaseModel):
    basic_info: BasicInfo
    objective: Optional[str] = ""
    education: List[EducationEntry] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    additional_information: List[str] = Field(default_factory=list)
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
        # print(f"Error analyzing CV:\n{traceback.format_exc()}")
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
            extract_and_save_json(extracted_data, "outputfiles/new_outputs/CV-Kapil_kaushik_AI.json")
