from llms import GeminiProvider, OpenAIProvider, AnthropicProvider

class QueryBuilder:
    def __init__(self, llm_provider: GeminiProvider):
        self.llm_provider = llm_provider

    def build_arxiv_query(self, user_interest: str) -> str:
        prompt = f"""
        Given the user's research interests: "{user_interest}"
        Generate an arXiv search query that:
        1. Uses arXiv's search syntax (e.g., AND, OR, parentheses for grouping)
        2. Covers all aspects of the user's interests
        3. Is specific enough to return relevant results
        4. Is formatted as: all:"query here"
        
        Return only the query string, without any additional text or explanations.
        """
        query = self.llm_provider.generate_query(prompt)
        return f'all:"{query.strip()}"'

    def build_biorxiv_query(self, user_interest: str) -> str:
        prompt = f"""
        Given the user's research interests: "{user_interest}"
        Generate a bioRxiv search query that:
        1. Consists of key terms and phrases related to the user's interests
        2. Is suitable for a simple keyword search (no complex operators)
        3. Covers all aspects of the user's interests
        4. Is specific enough to return relevant results
        
        Return only the query string, without any additional text or explanations.
        """
        return self.llm_provider.generate_query(prompt).strip()

# Example usage:
# api_key = "your_gemini_api_key_here"
# llm_provider = GeminiProvider(api_key)
# query_builder = QueryBuilder(llm_provider)
# 
# user_interest = "I'm interested in genomics, deep learning and the use of multi-omics to understand diseases"
# arxiv_query = query_builder.build_arxiv_query(user_interest)
# biorxiv_query = query_builder.build_biorxiv_query(user_interest)
# 
# print(f"arXiv query: {arxiv_query}")
# print(f"bioRxiv query: {biorxiv_query}")