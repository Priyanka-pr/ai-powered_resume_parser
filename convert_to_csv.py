import pandas as pd
from config import Config
import tkinter as tk
from tkinter import filedialog
import pdfplumber
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
import json
import re

# Save to CSV
def save_to_csv(data, output_file):
    print(f"data by llm:: {data}")

    # 1. Extract JSON from within triple backticks (if present)
    if isinstance(data, str):
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', data, re.DOTALL)
        json_text = match.group(1) if match else data.strip()
        try:
            parsed_json = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return
    elif isinstance(data, dict):
        parsed_json = data
    else:
        print("Invalid data format for CSV saving")
        return

    # 2. Convert to DataFrame and save as CSV
    df = pd.json_normalize(parsed_json)
    df.to_csv(output_file, index=False)
    print(f"✅ Saved output to: {output_file}")

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

def build_prompt(resume_text: str, json_structure: dict) -> str:
    return f"""
You are an intelligent invoice parser. Extract relevant information from the invoice text below and populate it in the given JSON structure.

Resume Text:
\"\"\"
{resume_text}
\"\"\"

Return the filled JSON structure in proper format:
{json.dumps(json_structure, indent=2)}

Only return a valid JSON object as output. Do not include any explanations or commentary.
"""

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

    json_csv={
    "INVOICE_NO": "",
    "IRN": "",
    "PO_NO": "",
    "DATE": "",
    "VEHICLE_NO": "",
    "TRANSPORTER": "",
    "ITEM_CODE": "",
    "TOTAL_AMOUNT": 0.0,
    "CGST": 0.0,
    "SGST": 0.0,
    "IGST": 0.0,
    "GROSS_INVOICE_VALUE": 0.0,
    "GRAND_TOTAL": 0.0
    }

    llm = ChatOllama(
            model=Config.MODEL,
            temperature=0.5,
            base_url=Config.LOCALHOST,
            streaming=True
        )
    prompt = build_prompt(text, json_csv)


    prompt2 = PromptTemplate(
            template=
            "You are an intelligent invoice oarser. Your task is to extract and return a structured JSON object based on the schema below from the provided invoice text.\n\n"
            "- Return the result in strict accordance with the JSON schema shown in {json_csv}.\n\n"
            "Resume Text:\n{document}",
            # "Extract the following from the resume text:{format_instructions}Resume Text:\n{document}",
            input_variables=["document", "json_csv"],
        )
    formatted_prompt = prompt2.format(document=text, json_csv=json_csv)
    llm_response = llm.invoke(formatted_prompt)
    print(f"llm response ::: {llm_response.content}")
    if llm_response.content:
        # 1. Clean and parse the response
        content = llm_response.content.strip()
        if content.startswith("```"):
            content = content.strip("`").strip("json").strip()
        try:
            parsed_data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            parsed_data = None
        save_to_csv(parsed_data, "outputfiles/csv_files/invoice.csv")
    else:
        print("❌ No content extracted from the PDF.")


if __name__ == "__main__":
    select_pdf_and_extract_text()