import json
from datetime import datetime, timedelta
from typing import List, Dict, Union
from app.fetchers.fetchers import ArXivRetriever, BioRxivRetriever

class WeeklyArticleFetcher:
    def __init__(self):
        self.arxiv_retriever = ArXivRetriever()
        self.biorxiv_retriever = BioRxivRetriever()

    def fetch_last_week_articles(self) -> Dict[str, List[Dict[str, Union[str, datetime]]]]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        print(f"Fetching articles from {start_date} to {end_date}")

        arxiv_articles = self.arxiv_retriever.fetch_articles(start_date, end_date)
        biorxiv_articles = self.biorxiv_retriever.fetch_articles(start_date, end_date)

        return {
            "arxiv": arxiv_articles,
            "biorxiv": biorxiv_articles
        }

    def save_articles_to_json(self, articles: Dict[str, List[Dict[str, Union[str, datetime]]]], filename: str):
        # Convert datetime objects to ISO format strings for JSON serialization
        for source, article_list in articles.items():
            for article in article_list:
                article['updated'] = article['updated'].isoformat()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

    def fetch_and_save_weekly_articles(self):
        articles = self.fetch_last_week_articles()
        
        total_articles = sum(len(article_list) for article_list in articles.values())
        print(f"\nFetched a total of {total_articles} articles")
        
        filename = f"database/weekly_articles_{datetime.now().strftime('%Y%m%d')}.json"
        self.save_articles_to_json(articles, filename)
        print(f"Articles saved to {filename}")

def main():
    fetcher = WeeklyArticleFetcher()
    fetcher.fetch_and_save_weekly_articles()

if __name__ == "__main__":
    main()
