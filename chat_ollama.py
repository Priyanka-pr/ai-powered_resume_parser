import logging
from config import Config
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from langchain_community.chat_models import ChatOllama

# ---------- Step 1: Define your output schema ----------
class WorkExperience(BaseModel):
    company: str
    job_title: str = Field(alias="jobTitle")
    start_date: str
    end_date: str
    description: str

    class Config:
        populate_by_name = True  # ✅ Allow using alias like jobTitle

class ResumeData(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email_address: str = Field(alias="emailAddress")
    work_experience: List[WorkExperience] = Field(alias="workExperience")

    class Config:
        populate_by_name = True  # ✅ Allow using alias like firstName

# ---------- Step 2: Create the parser ----------
parser = PydanticOutputParser(pydantic_object=ResumeData)

# ---------- Step 5: Your sample input ----------
resume_text = """
My name is Yash Dive. You can reach me at yashdive190@gmail.com. 
I worked at Tata Consultancy Services as a Developer from 2021 to 2024.
I was responsible for full-stack development, mainly Angular and Spring Boot.
"""

# ---------- Step 3: Create a clean prompt ----------
prompt = PromptTemplate(
    template=(
        "You are a helpful resume parser.\n"
        "Extract structured data from the resume text below.\n\n"
        "Resume Text:\n{resume_text}\n\n"
        "{format_instructions}"
    ),
    input_variables=["resume_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# ---------- Step 4: Create the LLM ----------
llm = ChatOllama(model=Config.MODEL, temperature=0.5, base_url=Config.LOCALHOST)

# ---------- Step 6: Run the chain ----------
chain = prompt | llm | parser

# Execute and print the result
parsed_response = chain.invoke({"resume_text": resume_text})
print(f"parsed_response::: {parsed_response}")
