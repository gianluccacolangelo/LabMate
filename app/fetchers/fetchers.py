import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Union
from abc import ABC, abstractmethod

class ArticleRetriever(ABC):
    @abstractmethod
    def fetch_articles(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Union[str, datetime]]]:
        pass

class ArXivRetriever(ArticleRetriever):
    BASE_URL = 'http://export.arxiv.org/api/query?'

    def fetch_articles(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Union[str, datetime]]]:
        articles = []
        start = 0
        batch_size = 1000  # arXiv API allows up to 1000 results per request

        while True:
            params = {
                'search_query': f'lastUpdatedDate:[{start_date.strftime("%Y%m%d")}0000 TO {end_date.strftime("%Y%m%d")}2359]',
                'start': start,
                'max_results': batch_size,
                'sortBy': 'lastUpdatedDate',
                'sortOrder': 'ascending'
            }
            url = self.BASE_URL + '&'.join([f'{k}={v}' for k, v in params.items()])
            
            response = requests.get(url)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            batch_articles = [
                {
                    'title': entry.title,
                    'abstract': entry.summary,
                    'id': entry.id.split('/abs/')[-1],
                    'pdf_url': next((link.href for link in entry.links if link.type == 'application/pdf'), None),
                    'updated': datetime.strptime(entry.updated, '%Y-%m-%dT%H:%M:%SZ')
                }
                for entry in feed.entries
            ]
            
            articles.extend(batch_articles)
            
            
            if len(batch_articles) < batch_size:
                break
            
            start += batch_size

        return articles

class BioRxivRetriever(ArticleRetriever):
    BASE_URL = 'https://api.biorxiv.org/details/biorxiv/'

    def fetch_articles(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Union[str, datetime]]]:
        articles = []
        cursor = 0
        
        while True:
            url = f"{self.BASE_URL}{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/{cursor}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            batch_articles = [
                {
                    'title': article['title'],
                    'abstract': article['abstract'],
                    'id': article['doi'],
                    'pdf_url': f"https://www.biorxiv.org/content/{article['doi']}v{article['version']}.full.pdf",
                    'updated': datetime.strptime(article['date'], '%Y-%m-%d')
                }
                for article in data['collection']
            ]
            
            articles.extend(batch_articles)
            
            
            total_count = int(data['messages'][0]['total'])
            if len(batch_articles) < 100 or total_count <= cursor + len(batch_articles):
                break
            
            cursor += 100

        return articles

def main():
    # Example usage
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()

    print(f"Fetching articles from {start_date} to {end_date}")

    arxiv_retriever = ArXivRetriever()
    biorxiv_retriever = BioRxivRetriever()

    arxiv_articles = arxiv_retriever.fetch_articles(start_date, end_date)
    biorxiv_articles = biorxiv_retriever.fetch_articles(start_date, end_date)

    print(f"\nFinal count:")
    print(f"Retrieved {len(arxiv_articles)} arXiv articles")
    print(f"Retrieved {len(biorxiv_articles)} bioRxiv articles")

if __name__ == "__main__":
    main()