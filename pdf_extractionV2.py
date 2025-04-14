import tkinter as tk
from tkinter import filedialog
import pdfplumber
import os
from langchain_community.chat_models import ChatOllama
from config import Config
from pydantic import BaseModel,Field
from typing import Optional,List
from langchain.output_parsers import PydanticOutputParser,OutputFixingParser
from langchain.prompts import PromptTemplate
import unittest
from pydantic import ValidationError

class Education(BaseModel):
    course: str
    institution: str
    location: Optional[str] = None
    year_of_passing: Optional[str] = None
    performance: Optional[str] = None
class Name(BaseModel):
    first: str
    last: str

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
    name: Name
    dob: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    skills: SkillSet = Field(default_factory=lambda: SkillSet(technical_skills=[], soft_skills=[]))
    internships_and_projects: List[Project] = Field(default_factory=list)
    positions_of_responsibility: List[PositionOfResponsibility] = Field(default_factory=list)
    volunteer_experience: List[VolunteerWork] = Field(default_factory=list)
    interests: Optional[List[str]] = Field(default_factory=list)
# Parser based on schema
base_parser = PydanticOutputParser(pydantic_object=Resume)

sample_resume = {
    "name": {
        "first_name": "Priyanka",
        "last_name": "Rana"
    },
    "dob": "1998-07-21",
    "address": "123 Main Street, Delhi, India",
    "email": "priyanka.rana@example.com",
    "phone": "+91-9876543210",
    "education": [
        {
            "degree": "B.Tech",
            "field_of_study": "Computer Science",
            "institution": "Delhi Technological University",
            "start_date": "2016",
            "end_date": "2020",
            "grade": "8.7 CGPA"
        }
    ],
    "certifications": [
        {
            "title": "AWS Certified Solutions Architect",
            "issuer": "Amazon Web Services",
            "issue_date": "2022-05",
            "description": "Validated expertise in cloud architecture."
        }
    ],
    "skills": {
        "technical_skills": ["Python", "React Native", "SQL", "Docker"],
        "soft_skills": ["Team Leadership", "Time Management"]
    },
    "internships_and_projects": [
        {
            "title": "Resume Parsing App",
            "description": "Built a cross-platform app using React Native and Python backend for resume parsing using LLM.",
            "technologies_used": ["React Native", "Flask", "Pydantic", "LangChain"],
            "duration": "3 months"
        }
    ],
    "positions_of_responsibility": [
        {
            "title": "Tech Lead - Developer Club",
            "organization": "DTU",
            "duration": "2019-2020",
            "description": "Led a team of 10+ members in organizing hackathons and coding events."
        }
    ],
    "volunteer_experience": [
        {
            "organization": "GirlScript Foundation",
            "role": "Volunteer Mentor",
            "duration": "2021-2022",
            "description": "Mentored students in open source and Python basics."
        }
    ],
    "interests": ["Sanskrit learning", "Open source", "Traveling"]
}

class TestResumeModel(unittest.TestCase):
    def test_valid_resume_parsing(self):
        try:
            resume_obj = Resume.model_validate(sample_resume)
            self.assertIsInstance(resume_obj, Resume)
            self.assertEqual(resume_obj.name.first, "Priyanka")
            self.assertEqual(resume_obj.name.last, "Rana")
            self.assertEqual(resume_obj.education[0].course, "B.Tech")
            self.assertEqual(resume_obj.skills.technical_skills, ["Python", "React Native", "SQL", "Docker"])
        except ValidationError as e:
            self.fail(f"Resume validation failed: {e}")


def extract_full_text_and_tables(file_path):
    full_text = ''
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # Extract regular text
                page_text = page.extract_text() or ""
                full_text += f"\n--- Page {page_number} Text ---\n"
                full_text += page_text.strip() + "\n"

                # Extract tables, if any
                tables = page.extract_tables()
                for table_index, table in enumerate(tables, start=1):
                    full_text += f"\n--- Page {page_number} Table {table_index} ---\n"
                    for row in table:
                        row_text = " | ".join(cell if cell else "" for cell in row)
                        full_text += row_text + "\n"
                    
    except Exception as e:
        print(f"Error processing PDF: {e}")

    return full_text.strip()

def select_pdf_and_extract_text():
    """Select a PDF and extract all text + table contents."""
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_path:
        print("No file selected.")
        return

    print(f"Extracting content from: {file_path}")
    text = extract_full_text_and_tables(file_path)
            # # ------------------ LLM Call ------------------
    try:
        parsed = Resume(text) # or Resume(**response) for older Pydantic versions
        print(f"parsed data::: {parsed}")
    except ValidationError as e:
        print(e.json(indent=2))


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
            "- Make sure to include all required fields, even if empty."
            "- Return the result in strict accordance with the JSON schema shown in {format_instructions}.\n\n"
            "Resume Text:\n{document}",
            # "Extract the following from the resume text:{format_instructions}Resume Text:\n{document}",
            input_variables=["document"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
    # llm_response = llm.invoke(text)
    # print(f"llm res::: {llm_response}")
    # print("Extracted Text:::", text[:500])  
    # formatted_prompt = prompt.format(document=text)
    # print("🚀 Step 4: Invoking LLM...")
    # llm_response = llm.invoke(formatted_prompt)
    # print("🧾 Raw LLM Output:", llm_response.content[:500])
    # response = parser.parse(llm_response.content)
    # print(f"llm response ::: {response}")
    # if response:
    #     # Define output directory
    #     script_dir = os.path.dirname(os.path.abspath(__file__))
    #     output_dir = os.path.join(script_dir, "outputfiles")
    #     os.makedirs(output_dir, exist_ok=True)

    #     # Define output file path
    #     base_name = os.path.splitext(os.path.basename(file_path))[0]
    #     output_path = os.path.join(output_dir, base_name + "_extracted.txt")

    #     with open(output_path, "w", encoding="utf-8") as f:
    #         f.write(llm_response)

    #     print(f"\n✅ Text and tables extracted to:\n{output_path}")
    # else:
    #     print("❌ No content extracted from the PDF.")

if __name__ == "__main__":
    unittest.main()
    select_pdf_and_extract_text()
