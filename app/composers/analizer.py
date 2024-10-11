"""
here we should use pdf_handling to get the text from the top 20 abstracts more
similar to the user interests, which is the output of vector_database.search(vectorized_user_interests,top_k=20)

We should use the llm to choose between 1 and 3 papers, it should be extremely conservative 
in choosing them, it's better to have less than more. 
"""

from typing import List, Dict, Any
from app.fetchers.pdf_handling import PdfReader
from app.database_management.vector_database.vector_database import FaissVectorDatabase
from app.llms import GeminiProvider
import numpy as np

class PaperAnalyzer:
    def __init__(self, vector_db: FaissVectorDatabase, pdf_reader: PdfReader, llm_provider: GeminiProvider):
        self.vector_db = vector_db
        self.pdf_reader = pdf_reader
        self.llm_provider = llm_provider

    def analyze_papers(self, vectorized_user_interests: np.ndarray) -> List[Dict[str, Any]]:
        # Get top 20 similar papers
        similar_papers = self.vector_db.search(vectorized_user_interests, top_k=20)

        # Extract abstracts from PDFs
        abstracts = []
        for paper in similar_papers:
            abstract = self.pdf_reader.read(paper['pdf_url'])
            abstracts.append({"id": paper['id'], "abstract": abstract})

        # Use LLM to choose 1-3 papers
        chosen_papers = self._choose_papers(abstracts)

        return chosen_papers

    def _choose_papers(self, abstracts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        prompt = self._create_paper_selection_prompt(abstracts)
        llm_response = self.llm_provider.generate_query(prompt)
        chosen_paper_ids = self._parse_llm_response(llm_response)

        chosen_papers = [paper for paper in abstracts if paper['id'] in chosen_paper_ids]
        return chosen_papers

    def _create_paper_selection_prompt(self, abstracts: List[Dict[str, str]]) -> str:
        prompt = (
            "You are a highly selective research assistant. Your task is to choose between 1 and 3 papers from the "
            "following abstracts, based on their relevance and potential impact. Be extremely conservative in your "
            "selection; it's better to choose fewer papers than more. If no papers seem truly exceptional, it's okay "
            "to select none. Here are the abstracts:\n\n"
        )
        for i, paper in enumerate(abstracts, 1):
            prompt += f"Paper {i} (ID: {paper['id']}):\n{paper['abstract']}\n\n"
        prompt += (
            "Please provide your selection in the following format:\n"
            "Selected Paper IDs: [list of selected paper IDs, or 'None' if no papers are selected]\n"
            "Reasoning: [brief explanation for your choices]"
        )
        return prompt

    def _parse_llm_response(self, llm_response: str) -> List[str]:
        # Extract the selected paper IDs from the LLM response
        # This is a simple implementation and might need to be adjusted based on the actual LLM output format
        lines = llm_response.split('\n')
        for line in lines:
            if line.startswith("Selected Paper IDs:"):
                ids = line.split(":")[1].strip()
                if ids.lower() == 'none':
                    return []
                return [id.strip() for id in ids.split(',')]
        return []

# Usage example:
# vector_db = FaissVectorDatabase(dimension=768)  # Adjust dimension as needed
# pdf_reader = PdfReader()
# llm_provider = GeminiProvider(api_key="your_api_key_here")
# analyzer = PaperAnalyzer(vector_db, pdf_reader, llm_provider)
# vectorized_user_interests = np.random.rand(768)  # Replace with actual user interests vector
# chosen_papers = analyzer.analyze_papers(vectorized_user_interests)
