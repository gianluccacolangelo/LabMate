import json
from datetime import datetime, timedelta, timezone
import requests
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
import os

class BioRxivCacheUpdater:
    BASE_URL = 'https://api.biorxiv.org/details/biorxiv/'

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(3), retry=retry_if_exception_type(ConnectionResetError))
    def _make_request(self, url):
        response = requests.get(url, headers={'User-Agent': 'YourAppName/1.0 (contact@example.com)'}, timeout=10)
        response.raise_for_status()
        return response

    def update(self):
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        start_date = end_date - timedelta(weeks=1)
        
        articles = []
        cursor = 0
        while True:
            url = f"{self.BASE_URL}{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/{cursor}"
            
            try:
                response = self._make_request(url)
                data = response.json()
                
                if not data['collection']:
                    break
                
                articles.extend(data['collection'])
                
                cursor += len(data['collection'])
                total_results = int(data['messages'][0]['total'])
                if cursor >= total_results:
                    break
                
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data: {e}")
                break

        return {
            'date': datetime.now(timezone.utc).isoformat(),
            'articles': articles
        }

class BioRxivCache:
    CACHE_FILE = 'biorxiv_cache.json'

    def __init__(self):
        self.updater = BioRxivCacheUpdater()
        self.cache = self.load()

    def load(self):
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, 'r') as f:
                cache = json.load(f)
            if self.is_cache_valid(cache):
                return cache
        return self.update()

    def is_cache_valid(self, cache):
        cache_date = datetime.fromisoformat(cache['date'])
        return (datetime.now(timezone.utc) - cache_date).days < 7

    def update(self):
        cache = self.updater.update()
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        return cache

    def get_articles(self):
        return self.cache['articles']