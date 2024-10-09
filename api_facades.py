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
    BASE_URL = 'http://export.arxiv.org/api/query?'
    
    def __init__(self, search_query):
        self.search_query = search_query

    def fetch(self, max_results=100, start=0, sort_by='submittedDate', sort_order='descending'):
        params = {
            'search_query': self.search_query,
            'start': start,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        url = self.BASE_URL + urllib.parse.urlencode(params)
        print(f"Fetching from URL: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        
        results = []
        for entry in feed.entries:
            result = {
                'id': entry.id.split('/abs/')[-1],
                'title': entry.title,
                'authors': [author.name for author in entry.authors],
                'published': datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ'),
                'updated': datetime.strptime(entry.updated, '%Y-%m-%dT%H:%M:%SZ'),
                'summary': entry.summary,
                'comment': entry.get('arxiv_comment', ''),
                'journal_ref': entry.get('arxiv_journal_ref', ''),
                'doi': entry.get('arxiv_doi', ''),
                'primary_category': entry.arxiv_primary_category.get('term', ''),
                'categories': [tag.term for tag in entry.tags if tag.scheme.endswith('/schemes/arXiv.org')],
                'pdf_url': next((link.href for link in entry.links if link.type == 'application/pdf'), None),
            }
            results.append(result)
        
        return results

class BioRxivAPIAdapter:
    def __init__(self, search_query):
        self.search_terms = self._parse_search_query(search_query)
        self.cache = BioRxivCache()

    def _parse_search_query(self, query):
        # Remove outer parentheses if present
        query = query.strip('()')
        # Split by AND
        and_terms = [term.strip() for term in query.split(' AND ')]
        parsed_terms = []
        for term in and_terms:
            if '(' in term:
                # This is an OR group
                or_terms = [t.strip().lower() for t in term.strip('()').split(' OR ')]
                parsed_terms.append(or_terms)
            else:
                # This is a single term
                parsed_terms.append([term.lower()])
        print(f"Parsed search terms: {parsed_terms}")
        return parsed_terms

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
        score = 0
        for term_group in self.search_terms:
            if any(term in text for term in term_group):
                score += 1
        return score

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
    user_interest = "I'm interested in genomics and disease"
    print(f"User interest: {user_interest}")

    # Generate queries
    arxiv_query = query_builder.build_arxiv_query(user_interest)
    biorxiv_query = query_builder.build_biorxiv_query(user_interest)

    print(f"arXiv query: {arxiv_query}")
    print(f"bioRxiv query: {biorxiv_query}")

    # Fetch from arXiv
    arxiv_adapter = ArXivAPIAdapter(search_query=arxiv_query)
    arxiv_articles = arxiv_adapter.fetch(max_results=10)
    
    # If no results, try fallback query
    if not arxiv_articles:
        fallback_query = query_builder.build_fallback_query(user_interest)
        print(f"Fallback arXiv query: {fallback_query}")
        arxiv_adapter = ArXivAPIAdapter(search_query=fallback_query)
        arxiv_articles = arxiv_adapter.fetch(max_results=10)

    print(f"\nTotal arXiv articles fetched: {len(arxiv_articles)}")
    for article in arxiv_articles[:3]:
        print(f"Title: {article['title']}")
        print(f"Authors: {', '.join(article['authors'])}")
        print(f"Published: {article['published']}")
        print(f"Summary: {article['summary'][:200]}...")
        print(f"PDF URL: {article['pdf_url']}")
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
        print(f"abstract: {article[3]}")
        print("---")

if __name__ == "__main__":
    main()