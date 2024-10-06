import fitz  # PyMuPDF
import requests
import io
import re

class PDFHandler:
    def __init__(self, pdf_url):
        self.pdf_url = pdf_url
        self.doc = self._download_and_open_pdf()

    def _download_and_open_pdf(self):
        response = requests.get(self.pdf_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        pdf_stream = io.BytesIO(response.content)
        return fitz.open(stream=pdf_stream, filetype="pdf")

    def extract_full_text(self):
        full_text = ""
        for page in self.doc:
            full_text += page.get_text()
        return full_text

    def get_text_by_pages(self, start_page, end_page):
        text = ""
        for page_num in range(start_page, min(end_page + 1, len(self.doc))):
            text += self.doc[page_num].get_text()
        return text

class PDFCleaner:
    @staticmethod
    def clean(text):
        # Remove acknowledgements section
        text = re.split(r'\nACKNOWLEDGEMENTS\n', text, flags=re.IGNORECASE)[0]
        
        # Remove author contributions section
        text = re.split(r'\nAUTHOR CONTRIBUTIONS\n', text, flags=re.IGNORECASE)[0]
        
        
        # Remove references section
        text = re.split(r'\nReferences\n', text, flags=re.IGNORECASE)[0]
        
        # Remove numbered references
        text = re.sub(r'\[\d+\].*?\n', '', text)
        
        # Remove page numbers
        text = re.sub(r'\n\d+\n', '\n', text)
        
        # Remove excessive newlines while preserving paragraph structure
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove headers and footers (this might need adjustment based on the specific PDF format)
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line.strip()) > 30 or line.strip().istitle()]
        text = '\n'.join(cleaned_lines)
        
        return text.strip()

    @staticmethod
    def remove_latex_artifacts(text):
        # Remove LaTeX equation environments
        text = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', text, flags=re.DOTALL)
        
        # Remove inline LaTeX math expressions
        text = re.sub(r'\$.*?\$', '', text)
        
        # Remove LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+(\{.*?\})?', '', text)
        
        return text

    @staticmethod
    def clean_for_llm(text):
        # Apply basic cleaning
        text = PDFCleaner.clean(text)
        
        # Remove LaTeX artifacts
        text = PDFCleaner.remove_latex_artifacts(text)
        
        # Additional cleaning steps specific for LLM input
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        
        # Remove special characters except periods, preserving paragraph breaks
        text = re.sub(r'[^a-zA-Z\s.\n]', '', text)
        
        # Convert multiple spaces to single space, preserving newlines
        text = re.sub(r' +', ' ', text)
        
        # Ensure single blank line between paragraphs
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

def main():
    pdf_url = "https://arxiv.org/pdf/2410.01533v1.pdf"
    pdf_handler = PDFHandler(pdf_url)
    
    # Extract full text
    full_text = pdf_handler.extract_full_text()
    
    # Clean the extracted text
    cleaned_text = PDFCleaner.clean(full_text)
    
    # Clean for LLM input
    llm_ready_text = PDFCleaner.clean_for_llm(full_text)
    
    print(f"Cleaned Text (first 1000 characters):\n{cleaned_text[:1000]}...")
    print(f"\nLLM-Ready Text (first 1000 characters):\n{llm_ready_text[:1000]}...")

if __name__ == "__main__":
    main()
