
from abc import ABC, abstractmethod
import requests
import io
import PyPDF2
import pdfplumber

#create both strategies, pyPDF2 and pdfplumber for a pdf reader

class PdfReaderStrategy(ABC):
    @abstractmethod
    def read(self,url:str):
        pass

class PyPDF2Reader(PdfReaderStrategy):
    def read(self, url: str):
        response = requests.get(url)

        if response.status_code == 200:
            pdf_content = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_content)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()  # Extract text from each page
            return self._clean_text(text)
        else:
            return f"Failed to download PDF: {response.status_code}"

    def _clean_text(self, text: str) -> str:
        # Remove extra spaces while preserving paragraphs
        text = '\n'.join(' '.join(line.split()) for line in text.split('\n'))
        
        # Remove references and everything that follows
        import re
        keywords = r'references|bibliography|works cited|literature cited'
        text = re.split(f'(?i){keywords}', text)[0]
        
        # Remove references pattern [X], [X,Y], [X-Y]
        text = re.sub(r'\[\d+(?:[-,]\d+)*\]', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove author names (assuming they are in Title Case)
        text = re.sub(r'\b(?:[A-Z][a-z]+ ){2,}[A-Z][a-z]+\b', '', text)
        
        # Remove any remaining special characters except periods and commas
        text = re.sub(r'[^\w\s.,]', '', text)
        
        return text.strip()
class PdfPlumberReader(PdfReaderStrategy):
    def read(self,url:str):
        response = requests.get(url)
        if response.status_code == 200:
            pdf_content = io.BytesIO(response.content)
            with pdfplumber.open(pdf_content) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                return self._clean_text(text)
        else:
            return f"Failed to download PDF: {response.status_code}"
    
    def _clean_text(self, text: str) -> str:
        # Remove extra spaces while preserving paragraphs
        text = '\n'.join(' '.join(line.split()) for line in text.split('\n'))
        
        # Remove references and everything that follows
        import re
        keywords = r'references|bibliography|works cited|literature cited'
        text = re.split(f'(?i){keywords}', text)[0]
        
        # Remove references pattern [X], [X,Y], [X-Y]
        text = re.sub(r'\[\d+(?:[-,]\d+)*\]', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        
        # Remove author names (assuming they are in Title Case)
        text = re.sub(r'\b(?:[A-Z][a-z]+ ){2,}[A-Z][a-z]+\b', '', text)
        
        # Remove any remaining special characters except periods and commas
        text = re.sub(r'[^\w\s.,]', '', text)
        
        return text.strip()
class PdfReader:
    def __init__(self,reader:PdfReaderStrategy = PyPDF2Reader()):
        self.reader = reader

    def read(self,url:str):
        return self.reader.read(url)

def main():
    pdfreader = PyPDF2Reader()
    pdf_reader = PdfReader(pdfreader)
    print(pdf_reader.read("https://arxiv.org/pdf/2302.07459.pdf"))

if __name__ == "__main__":
    main()