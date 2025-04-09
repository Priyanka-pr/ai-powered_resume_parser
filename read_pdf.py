import pdfplumber

pdf_path= "pdffiles/Bhavya_Gupta_Fresher.pdf"
docx_path="pdffiles/Avinash_Bhatnagar.docx"

# with pdfplumber.open(pdf_path) as pdf:
#     print("Number of pages:", len(pdf.pages))
#     for i, page in enumerate(pdf.pages):
#         text = page.extract_text()
#         print(f"\n--- Page {i+1} ---\n{text}")

# with pdfplumber.open(pdf_path) as pdf:
#     for i, page in enumerate(pdf.pages):
#         print(f"\n--- Page {i + 1} ---")

#         if i == 0:  # Handle only the first page as double column
#             width = page.width
#             height = page.height

#             # Define bounding boxes for columns
#             left_bbox = (0, 0, width / 2, height)
#             right_bbox = (width / 2, 0, width, height)

#             left_text = page.within_bbox(left_bbox).extract_text() or ""
#             right_text = page.within_bbox(right_bbox).extract_text() or ""

#             print("Left Column:\n", left_text)
#             print("Right Column:\n", right_text)

#         else:  # All other pages treated normally
#             text = page.extract_text() or ""
#             print(text)




# with pdfplumber.open("/home/priyankarana/Desktop/PriyankaRanaCodeFiles/react_native_practice/cv_project/pdffiles/Bhavya_Gupta_Fresher.pdf") as pdf:
#     for page in pdf.pages:
#         text = page.extract_text()
#         print(text)

# text = docx2txt.process("pdffiles/Avinash_Bhatnagar.docx")
# print(text)

# doc = Document("pdffiles/Avinash_Bhatnagar.docx")
# for para in doc.paragraphs:
#     print(para.text)

# import fitz

# doc = fitz.open("pdffiles/Bhavya_Gupta_Fresher.pdf")
# for page in doc:
#     pix = page.get_pixmap()
#     pix.save("page.png")

# import easyocr

# reader = easyocr.Reader(['en'])
# result = reader.readtext('page.png')
# for bbox, text, prob in result:
#     print(f"Detected: {text} (Confidence: {prob:.2f})")


# from PyPDF2 import PdfReader

# # Load your PDF file
# reader = PdfReader("pdffiles/Bhavya_Gupta_Fresher.pdf")

# # Get number of pages
# print("Number of pages:", len(reader.pages))

# # Extract text from each page
# for i, page in enumerate(reader.pages):
#     text = page.extract_text()
#     print(f"\n--- Page {i+1} ---\n{text}")

# import PyPDF4

# with open(pdf, "rb") as file:
#     reader = PyPDF4.PdfFileReader(file)
#     print("Number of pages:", reader.numPages)

#     for i in range(reader.numPages):
#         page = reader.getPage(i)
#         text = page.extractText()  # Correct method for PyPDF4
#         print(f"\n--- Page {i+1} ---\n{text}")

# from pdfminer.high_level import extract_text

# # Path to your PDF
# file_path = pdf_path

# # Extract text from the entire PDF
# text = extract_text(file_path)

# print(text)

# from pypdf import PdfReader

# # Load your PDF file
# reader = PdfReader(pdf_path)

# print(f"Number of pages: {len(reader.pages)}")

# # Loop through each page and extract text
# for i, page in enumerate(reader.pages, start=1):
#     text = page.extract_text()
#     print(f"\n--- Page {i} ---\n")
#     print(text)

# import fitz  # PyMuPDF

# # Open the PDF
# doc = fitz.open(pdf_path)

# print(f"Number of pages: {len(doc)}")

# # Loop through pages and extract text
# for page_num in range(len(doc)):
#     page = doc[page_num]
#     text = page.get_text()
#     print(f"\n--- Page {page_num + 1} ---\n")
#     print(text)

def is_table_like(line):
    # Detect multiple commas or many evenly spaced words
    return line.count(",") >= 2 or len(re.split(r'\s{2,}', line)) > 2

def is_two_column_line(line, page_width):
    # Approximate: if text is split far apart across page width
    parts = re.split(r'\s{5,}', line)  # 5+ spaces
    if len(parts) == 2:
        # Heuristics: both parts should have real content
        return len(parts[0].strip()) > 10 and len(parts[1].strip()) > 10
    return False

def extract_columns(page):
    """Extract text from two columns."""
    width = page.width
    height = page.height

    left_box = (0, 0, width / 2, height)
    right_box = (width / 2, 0, width, height)

    left_text = page.within_bbox(left_box).extract_text() or ""
    right_text = page.within_bbox(right_box).extract_text() or ""

    return left_text + "\n" + right_text


with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"\n--- Page {i + 1} ---")
        text = page.extract_text()
        lines = text.split("\n") if text else []
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            table_like = is_table_like(line)
            two_column = is_two_column_line(line, page.width)

            if table_like:
                print(f"[Table] Line {idx+1}: {line}")
            elif two_column:
                print(f"[Two Columns] Line {idx+1}: {line}")
                extract_columns()
            else:
                print(f"[Single Line] Line {idx+1}: {line}")