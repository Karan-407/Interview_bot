from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    # Create a PDF reader object
    reader = PdfReader(pdf_path)
    
    # Initialize empty text variable
    extracted_text = ""
    
    # Extract text from all pages
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        extracted_text += f"\n--- Page {page_num + 1} ---\n"
        extracted_text += text
    
    return extracted_text