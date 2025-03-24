import fitz  # PyMuPDF for PDF processing
from docx import Document  # DOCX processing
import spacy  # NLP for entity recognition
import re  # Regex for pattern extraction
import os
import pandas as pd
import json

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Predefined lists
TECHNOLOGIES_LIST = [
    "JavaScript", "jQuery", "MySQL", "Apex", "SOQL", "SOSL", "Visualforce", "LWC",
    "Aura", "Salesforce", "CPQ", "REST API", "SOAP API", "Bitbucket", "GitHub",
    "JIRA", "Data Loader", "Approval Process", "Lightning Web Components", "MuleSoft"
]

CERTIFICATION_KEYWORDS = [
    "Salesforce Certified", "AWS Certified", "Azure Certified", "Google Cloud Certified",
    "Microsoft Certified", "Trailhead", "PMP", "Scrum Master", "CISSP", "CCNA",
    "Google Analytics Certified", "CompTIA"
]

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}")
        return ""

def extract_projects(text):
    """Extract project names and URLs from text."""
    projects = []
    
    # Extract project names
    project_matches = re.findall(r"(?i)(?:(?:Projects|Project Title|Role)[:\-]?)\s*([^\n]+)", text)

    # Extract URLs (if available)
    url_matches = re.findall(r"https?://[^\s]+", text)

    # Process project names and URLs
    for i, project in enumerate(project_matches):
        project_name = project.strip()
        if len(project_name.split()) > 1:  # Ensure it's a valid project name
            project_url = url_matches[i] if i < len(url_matches) else "Not Available"
            projects.append({"Project Name": project_name, "Project URL": project_url})

    return projects

def extract_education(text):
    """Extract education details including degree, university, and CGPA/percentage."""
    education = []

    # Pattern to capture education details (Degree, University, CGPA)
    education_matches = re.findall(
        r"((?:Bachelor|Master|B\.Tech|M\.Tech|MBA|PhD|Graduate)[^,]*)[, ]*\s*(?:from|at)?\s*([\w\s]+University|Institute)[,\s]*(?:CGPA[:\-]?\s*(\d+\.\d+)|Percentage[:\-]?\s*(\d+%))?",
        text, re.IGNORECASE
    )

    for match in education_matches:
        degree, university, cgpa, percentage = match
        details = f"{degree} from {university}"
        if cgpa:
            details += f" (CGPA: {cgpa})"
        if percentage:
            details += f" (Percentage: {percentage})"
        education.append(details)

    return education

def extract_personal_details(text):
    """Extract personal details such as father's name, DOB, address, and languages."""
    personal_details = {}

    # Extract Father's Name
    father_match = re.search(r"Father(?:'s)? Name[:\-]?\s*(.*)", text, re.IGNORECASE)
    personal_details["Father Name"] = father_match.group(1).strip() if father_match else "Not Available"

    # Extract Date of Birth (DOB)
    dob_match = re.search(r"Date of Birth[:\-]?\s*(.*)", text, re.IGNORECASE)
    personal_details["Date of Birth"] = dob_match.group(1).strip() if dob_match else "Not Available"

    # Extract Address
    address_match = re.search(r"Current Address[:\-]?\s*(.*)", text, re.IGNORECASE)
    personal_details["Address"] = address_match.group(1).strip() if address_match else "Not Available"

    # Extract Languages
    languages_match = re.search(r"Languages[:\-]?\s*(.*)", text, re.IGNORECASE)
    personal_details["Languages"] = languages_match.group(1).strip() if languages_match else "Not Available"

    return personal_details

def extract_information(text):
    """Extract resume details including personal details, education, experience, and more."""
    doc = nlp(text)

    name, email, phone, linkedin = None, None, None, None
    experience, certifications, technologies, projects, objectives = [], [], [], [], []

    # Extract Name
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            break

    # Extract Email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group() if email_match else None

    # Extract Phone Number
    phone_match = re.search(r"\+?\d[\d\s\-()]{8,}\d", text)
    phone = phone_match.group() if phone_match else None

    # Extract LinkedIn Profile
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9-]+", text)
    linkedin = linkedin_match.group() if linkedin_match else None

    # Extract Objective
    objective_match = re.search(r"Objective[:\-]?\s*(.*?)(?:\n\n|\nExperience|Projects|Education)", text, re.IGNORECASE | re.DOTALL)
    if objective_match:
        objectives.append(objective_match.group(1).strip())

    # Extract Experience
    experience_matches = re.findall(r"(\w[\w\s,.-]+)\s(at|with|in)\s([\w\s]+)\s\(?(\d{4})?", text, re.IGNORECASE)
    if experience_matches:
        experience = [f"{role} at {company} ({year})" if year else f"{role} at {company}" for role, _, company, year in experience_matches]

    # Extract Education
    education = extract_education(text)

    # Extract Certifications
    found_certifications = re.findall(r"(?i)(Salesforce Certified|AWS Certified|Azure Certified|Google Cloud Certified|Microsoft Certified|Trailhead)", text)
    certifications = list(set(found_certifications))

    # Extract Technologies
    found_technologies = [tech for tech in TECHNOLOGIES_LIST if re.search(rf"\b{tech}\b", text, re.IGNORECASE)]
    technologies = list(set(found_technologies))

    # Extract Projects
    projects = extract_projects(text)

    # Extract Personal Details
    personal_details = extract_personal_details(text)

    return {
        "Name": name if name else "Unknown",
        "Email": email,
        "Phone": phone,
        "LinkedIn": linkedin,
        "Experience": json.dumps(experience),
        "Education": json.dumps(education),
        "Certifications": json.dumps(certifications),
        "Technologies": json.dumps(technologies),
        "Projects": json.dumps(projects),
        "Objectives": json.dumps(objectives),
        **personal_details  # Add personal details
    }

def process_resume(file_path):
    """Extract structured information from a resume file."""
    file_extension = file_path.split(".")[-1].lower()

    if file_extension == "pdf":
        resume_text = extract_text_from_pdf(file_path)
    elif file_extension == "docx":
        resume_text = extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file type: {file_extension}")
        return None

    extracted_info = extract_information(resume_text)
    extracted_info["Resume File"] = os.path.basename(file_path)

    return extracted_info

# Entry point
if __name__ == "__main__":
    file_path = "pdffiles/Annu_Resume_17Sep.pdf"  # Change this to the actual file path
    extracted_data = process_resume(file_path)

    if extracted_data:
        print(json.dumps(extracted_data, indent=4))