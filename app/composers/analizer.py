"""
here we should use pdf_handling to get the text from the top 20 abstracts more
similar to the user interests, which is the output of vector_database.search(vectorized_user_interests,top_k=20)

We should use the llm to choose between 1 and 3 papers, it should be extremely conservative 
in choosing them, it's better to have less than more. 
"""

from typing import List, Dict, Any
from app.fetchers.pdf_handling import PdfReader
from app.database_management.vector_database.vector_database import FaissVectorDatabase
from app.database_management.vectorizer.bert import BertVectorizer
from app.llms import GeminiProvider
import numpy as np
import os

class PaperAnalyzer:
    def __init__(self, vector_db: FaissVectorDatabase, pdf_reader: PdfReader, llm_provider: GeminiProvider):
        self.vector_db = vector_db
        self.pdf_reader = pdf_reader
        self.llm_provider = llm_provider

    def analyze_papers(self, vectorized_user_interests: np.ndarray, user_interests: str) -> List[Dict[str, Any]]:
        # Get top 20 similar papers
        similar_papers = self.vector_db.search(vectorized_user_interests, top_k=40)
        print(f'similar papers: {similar_papers}')

        # Extract abstracts from PDFs
        abstracts = []
        for paper in similar_papers:
            print(f"Fetching abstract for paper {paper}")
            try:
                abstract = self.pdf_reader.read(paper['pdf_url'])
                abstracts.append({"id": paper['id'], "abstract": abstract})
            except Exception as e:
                print(f"Error fetching abstract for paper {paper}: {e}")

        # Use LLM to choose 1-3 papers
        chosen_papers = self._choose_papers(abstracts, user_interests)

        return chosen_papers

    def _choose_papers(self, abstracts: List[Dict[str, str]], user_interests: str) -> List[Dict[str, Any]]:
        prompt = self._create_paper_selection_prompt(abstracts, user_interests)
        llm_response = self.llm_provider.generate_query(prompt)
        print(f'llm response: {llm_response}')
        chosen_paper_ids = self._parse_llm_response(llm_response)
        chosen_papers = [paper for paper in abstracts if paper['id'] in chosen_paper_ids]
        return chosen_papers

    def _create_paper_selection_prompt(self, abstracts: List[Dict[str, str]], user_interests: str) -> str:
        prompt = (
            f"You are a highly selective research assistant. Your task is to choose between 1 and 3 papers from the "
            f"following abstracts, based on their relevance to the user's interests and potential impact. "
            f"The user's interests are: '''{user_interests}'''\n\n"
            f"Be extremely conservative in your selection; it's better to choose fewer papers than more. "
            f"If no papers seem truly exceptional or closely related to the user's interests, select at least one."
            f"Here are the abstracts:\n\n ''' \n"
        )
        for i, paper in enumerate(abstracts, 1):
            prompt += f"Paper (ID: {paper['id']}):\n{paper['abstract']}\n\n"
        prompt += (
            "''' \nPlease provide your selection in the following format:\n"
            "Selected Paper IDs: [list of selected paper IDs, or 'None' if no papers are selected]\n"
            "Reasoning: [brief explanation for your choices, relating them to the user's interests]"
        )
        print(f'prompt: {prompt}')
        return prompt

    def _parse_llm_response(self, llm_response: str) -> List[str]:
        import re

        pattern = r'Selected Paper IDs:\s*(.*)'
        match = re.search(pattern, llm_response, re.IGNORECASE)
        
        if not match:
            return []
        
        id_string = match.group(1).strip()
        if id_string.lower() == 'none':
            return []
        
        id_pattern = r'\b\d+\.\d+/[a-zA-Z0-9.]+\b'
        return re.findall(id_pattern, id_string)

class PaperAnalyzerFactory:
    def __init__(self, config: Dict[str,Any]):
        self.config = config

    def analyzer(self) -> PaperAnalyzer:
        vector_db = self._create_vector_db()
        pdf_reader = self._create_pdf_reader()
        llm_provider = self._create_llm_provider()
        return PaperAnalyzer(vector_db, pdf_reader, llm_provider)
    
    def _create_vector_db(self) -> FaissVectorDatabase:
        data_dir = self.config['data_dir']
        index_file = os.path.join(data_dir, 'faiss_index.bin')
        metadata_file = os.path.join(data_dir, 'metadata.pkl')
        vector_db  = FaissVectorDatabase(
            dimension=self.config['vector_dimension'],
            index_file=index_file,
            metadata_file=metadata_file)
        vector_db.load()
        return vector_db
    
    def _create_pdf_reader(self) -> PdfReader:
        return PdfReader()
    
    def _create_llm_provider(self) -> GeminiProvider:
        return GeminiProvider(api_key=self.config['gemini_api_key'])

    def create_vectorizer(self) -> BertVectorizer:
        return BertVectorizer(model_name=self.config['bert_model_name'])




# Usage example:
# config