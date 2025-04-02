
# Main execution
if __name__ == "__main__":
    file_path = "/home/abhishek/Downloads/cv_project/Annu_Resume_17Sep.pdf"
    with open(file_path, 'rb') as file:
        file_content = file.read()
    
    extracted_data = analyze_cv_from_content(file_content)

    if extracted_data:
        extract_and_save_json(extracted_data, "cv_output.json")

