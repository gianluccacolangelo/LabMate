import feedparser
import urllib.parse
import time
import requests
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from datetime import datetime, timedelta, timezone
import re
from pdf_reader import PDFHandler
from biorxiv_updater import BioRxivCache
import os
from dotenv import load_dotenv
from query_builder import QueryBuilder
from llms import GeminiProvider

class ArXivAPIAdapter:
    BASE_URL = 'https://export.arxiv.org/api/query?'
    
    def __init__(self, search_query, sort_by='submittedDate', sort_order='descending'):
        self.search_query = search_query
        self.sort_by = sort_by
        self.sort_order = sort_order

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry=retry_if_exception_type(ConnectionResetError))
    def _make_request(self, url):
        response = requests.get(url, headers={'User-Agent': 'YourAppName/1.0 (contact@example.com)'}, timeout=10)
        response.raise_for_status()
        return response

    def fetch(self, time_window='week', max_results=None):
        results = []
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        start_date = end_date - timedelta(weeks=1)
        
        start = 0
        batch_size = 100  # ArXiv API allows max 100 results per request

        while True:
            params = {
                'search_query': self.search_query,
                'start': start,
                'max_results': batch_size,
                'sortBy': self.sort_by,
                'sortOrder': self.sort_order
            }
            url = self.BASE_URL + urllib.parse.urlencode(params)
            print(f"Fetching results {start} to {start + batch_size - 1}...")
            
            try:
                response = self._make_request(url)
                feed = feedparser.parse(response.content)
                
                if not feed.entries:
                    break
                
                for entry in feed.entries:
                    published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    if published_date < start_date:
                        return results  # We've gone past the relevant date range
                    if published_date <= end_date:
                        # Extract arXiv ID using regex
                        arxiv_id_match = re.search(r'arxiv.org/abs/(.*?)v?$', entry.id)
                        arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else 'No ID found'
                        
                        # Generate URLs
                        view_url = f"https://arxiv.org/abs/{arxiv_id}"
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                        
                        # Extract author information
                        authors = []
                        for author in entry.get('authors', []):
                            name = author.get('name', 'Unknown')
                            email = author.get('email', 'Not provided')
                            authors.append((name, email))
                        
                        results.append((arxiv_id, entry.title, entry.summary, view_url, pdf_url, authors))
                
                if max_results and len(results) >= max_results:
                    return results[:max_results]
                
                if len(feed.entries) < batch_size:
                    break  # No more results to fetch
                
                start += batch_size
                time.sleep(3)  # Respect API rate limits
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data: {e}")
                break

        return results

class BioRxivAPIAdapter:
    def __init__(self, search_query):
        self.search_terms = self._parse_search_query(search_query)
        self.cache = BioRxivCache()

    def _parse_search_query(self, query):
        # Split by OR first, then by AND
        or_terms = [term.strip() for term in query.split('OR')]
        return [term.lower().split('AND') for term in or_terms]

    def fetch(self, max_results=None):
        all_articles = self.cache.get_articles()
        results = []

        for entry in all_articles:
            score = self._calculate_score(entry)
            if score > 0:
                result = self._format_article(entry, score)
                results.append(result)

        results.sort(key=lambda x: x[0], reverse=True)
        return results[:max_results] if max_results else results

    def _calculate_score(self, entry):
        text = f"{entry['title']} {entry['abstract']}".lower()
        
        def check_and_terms(and_terms):
            return all(term in text for term in and_terms)
        
        return sum(check_and_terms(and_terms) for and_terms in self.search_terms)

    def _format_article(self, entry, score):
        arxiv_id = entry['doi'].split('/')[-1]
        view_url = f"https://www.biorxiv.org/content/{entry['doi']}v{entry['version']}"
        pdf_url = f"{view_url}.full.pdf"
        authors = [(author, 'Not provided') for author in entry['authors'].split('; ')]
        return (score, arxiv_id, entry['title'], entry['abstract'], view_url, pdf_url, authors)

def main():
    # Load environment variables
    load_dotenv()

    # Get the API key from the environment variable
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in environment variables")

    # Initialize the LLM provider and QueryBuilder
    llm_provider = GeminiProvider(api_key)
    query_builder = QueryBuilder(llm_provider)

    # User's research interest
    user_interest = "I'm interested in BCI, deep learning and neuroscience"
    print(f"User interest: {user_interest}")

    # Generate queries
    arxiv_query = query_builder.build_arxiv_query(user_interest)
    biorxiv_query = query_builder.build_biorxiv_query(user_interest)

    print(f"arXiv query: {arxiv_query}")
    print(f"bioRxiv query: {biorxiv_query}")

    # Fetch from arXiv
    arxiv_adapter = ArXivAPIAdapter(search_query=arxiv_query)
    arxiv_articles = arxiv_adapter.fetch(time_window='week', max_results=None)
    
    # If no results, try fallback query
    if not arxiv_articles:
        fallback_query = query_builder.build_fallback_query(user_interest)
        print(f"Fallback arXiv query: {fallback_query}")
        arxiv_adapter = ArXivAPIAdapter(search_query=fallback_query)
        arxiv_articles = arxiv_adapter.fetch(time_window='week', max_results=None)

    print(f"\nTotal arXiv articles fetched: {len(arxiv_articles)}")
    for article in arxiv_articles[:3]:
        print(f"Title: {article[1]}")
        print(f"URL: {article[3]}")
        print("---")

    # Fetch from bioRxiv
    biorxiv_adapter = BioRxivAPIAdapter(search_query=biorxiv_query)
    biorxiv_articles = biorxiv_adapter.fetch(max_results=None)
    
    # If no results, try fallback query
    if not biorxiv_articles:
        fallback_query = query_builder.build_fallback_query(user_interest)
        print(f"Fallback bioRxiv query: {fallback_query}")
        biorxiv_adapter = BioRxivAPIAdapter(search_query=fallback_query)
        biorxiv_articles = biorxiv_adapter.fetch(max_results=None)

    print(f"\nTotal bioRxiv articles fetched: {len(biorxiv_articles)}")
    for article in biorxiv_articles[:3]:
        print(f"Title: {article[2]}")
        print(f"Score: {article[0]}")
        print(f"URL: {article[4]}")
        print("---")

if __name__ == "__main__":
    main()