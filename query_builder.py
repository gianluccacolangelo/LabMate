import os
from dotenv import load_dotenv
from llms import GeminiProvider, OpenAIProvider, AnthropicProvider

# Load environment variables from .env file
load_dotenv()

class QueryBuilder:
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider

    def build_arxiv_query(self, user_interest: str) -> str:
        prompt = f"""
        Given the user's research interests: "{user_interest}"
        Generate a simple arXiv search query that:
        1. Identify one main concept
        2. Identify 2-3 key concepts connected by OR
        3. Is broad enough to capture relevant papers
        4. Does not use complex syntax
        5. Is formatted as: all:"main concept ADN (ohter OR other)"
        
        Return only the query string, without any additional text or explanations.
        """
        query = self.llm_provider.generate_query(prompt)
        return f'all:"{query.strip()}"'

    def build_biorxiv_query(self, user_interest: str) -> str:
        prompt = f"""
        Given the user's research interests: "{user_interest}"
        Generate a simple bioRxiv search query that:
        1. Identify one main concept
        2. Identify 2-3 key concepts connected by OR
        3. Is broad enough to capture relevant papers
        4. Does not use complex syntax
        5. Follows this format: "main concept AND (other OR other)"
        
        Return only the query string, without any additional text or explanations.
        """
        return self.llm_provider.generate_query(prompt).strip()

    def build_fallback_query(self, user_interest: str) -> str:
        prompt = f"""
        Given the user's research interests: "{user_interest}"
        Generate a very broad, single-term search query that captures the main theme.
        Return only the query string, without any additional text or explanations.
        """
        return self.llm_provider.generate_query(prompt).strip()

def main():
    # Get the API key from the environment variable
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in environment variables")

    llm_provider = GeminiProvider(api_key)
    query_builder = QueryBuilder(llm_provider)

    user_interest = "I'm interested in genomics, deep learning and the use of multi-omics to understand diseases"
    
    arxiv_query = query_builder.build_arxiv_query(user_interest)
    biorxiv_query = query_builder.build_biorxiv_query(user_interest)

    print(f"User interest: {user_interest}")
    print(f"arXiv query: {arxiv_query}")
    print(f"bioRxiv query: {biorxiv_query}")

if __name__ == "__main__":
    main()