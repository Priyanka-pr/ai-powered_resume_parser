import pdfplumber
import docx2txt
from docx import Document
# with pdfplumber.open("/home/priyankarana/Desktop/PriyankaRanaCodeFiles/react_native_practice/cv_project/pdffiles/Bhavya_Gupta_Fresher.pdf") as pdf:
#     for page in pdf.pages:
#         text = page.extract_text()
#         print(text)

# text = docx2txt.process("pdffiles/Avinash_Bhatnagar.docx")
# print(text)

doc = Document("pdffiles/Avinash_Bhatnagar.docx")
for para in doc.paragraphs:
    print(para.text)