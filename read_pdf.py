import pdfplumber

with pdfplumber.open("/home/priyankarana/Desktop/PriyankaRanaCodeFiles/react_native_practice/cv_project/pdffiles/Bhavya_Gupta_Fresher.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
