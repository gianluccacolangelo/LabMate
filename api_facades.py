import feedparser
import urllib.parse
import time
import requests
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from datetime import datetime, timedelta, timezone
import re
from pdf_reader import PDFHandler
from biorxiv_updater import BioRxivCache

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
        self.search_query = search_query.lower()
        self.cache = BioRxivCache()

    def fetch(self, time_window='week', max_results=None):
        results = []
        for entry in self.cache.get_articles():
            if self.search_query in entry['title'].lower() or self.search_query in entry['abstract'].lower():
                arxiv_id = entry['doi'].split('/')[-1]
                title = entry['title']
                abstract = entry['abstract']
                view_url = f"https://www.biorxiv.org/content/{entry['doi']}v{entry['version']}"
                pdf_url = f"{view_url}.full.pdf"
                authors = [(author, 'Not provided') for author in entry['authors'].split('; ')]
                
                results.append((arxiv_id, title, abstract, view_url, pdf_url, authors))
                
                if max_results and len(results) >= max_results:
                    break

        print(f"Total bioRxiv articles fetched: {len(results)}")
        return results

def main():
    search_query = 'genomics'
    current_date = datetime.now(timezone.utc)
    print(f"Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"Query end date (yesterday): {(current_date - timedelta(days=1)).strftime('%Y-%m-%d')}")
    print(f"Query start date (1 week ago): {(current_date - timedelta(weeks=1)).strftime('%Y-%m-%d')}")
    
    # Fetch from arXiv
    arxiv_adapter = ArXivAPIAdapter(search_query=f'all:"{search_query}"')
    arxiv_articles = arxiv_adapter.fetch(time_window='week', max_results=None)
    print(f"\nTotal arXiv articles within the last week: {len(arxiv_articles)}")
    
    # Fetch from bioRxiv
    biorxiv_adapter = BioRxivAPIAdapter(search_query=search_query)
    biorxiv_articles = biorxiv_adapter.fetch(time_window='week', max_results=None)
    print(f"\nTotal bioRxiv articles within the last week: {len(biorxiv_articles)}")
    
if __name__ == "__main__":
    main()