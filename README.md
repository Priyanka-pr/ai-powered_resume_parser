# ai-powered_resume_parser
This project is an AI-powered resume parser that extracts structured information from PDF and DOCX files using GPT-3.5 Turbo / GPT-4o, OCR, and text processing libraries. It automates the extraction of key details such as personal information, education, work experience, skills, projects, and certifications from resumes.

Key Features:
🔹 File Handling: Supports PDF and DOCX file formats for resume parsing.
🔹 Text Extraction:

PDF Processing: Uses PyMuPDF (fitz) for extracting text from native PDFs.

OCR-based Extraction: Converts scanned PDFs to images using pdf2image and extracts text using pytesseract.

DOCX Parsing: Uses docx2txt to extract text from DOCX resumes.
🔹 AI-Powered Information Extraction:

Sends the extracted text to OpenAI’s GPT model to structure the data in JSON format.

Ensures that the output strictly adheres to a pre-defined structured format.
🔹 Automated JSON Output: Saves the extracted details in a structured JSON file for further use.

Tech Stack:
✅ Python (Primary language)
✅ PyMuPDF (fitz) - PDF text extraction
✅ pdf2image & pytesseract - OCR for scanned PDFs
✅ docx2txt - DOCX text extraction
✅ OpenAI API (GPT-3.5/GPT-4o) - AI-powered text analysis
✅ dotenv - Securely manages API keys
✅ JSON & Regex - Data structuring and validation

How It Works:
The user uploads a PDF/DOCX resume.

The script extracts text using either native parsing (fitz, docx2txt) or OCR for scanned PDFs.

The extracted text is analyzed by GPT using a well-structured JSON prompt.

The AI returns structured data, including name, contact details, education, work experience, skills, etc.

The extracted JSON data is saved for further processing or integration with a job portal.
