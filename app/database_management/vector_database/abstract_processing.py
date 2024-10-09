import json
from typing import Dict, Any, List, Tuple
import numpy as np
from tqdm import tqdm
from app.database_management.vectorizer.vectorizer_interface import IVectorizer
from app.database_management.vector_database.vector_database import VectorDatabase

class AbstractProcessingService:
    def __init__(self, vectorizer: IVectorizer, vector_database: VectorDatabase):
        self.vectorizer = vectorizer
        self.vector_database = vector_database

    def process_and_store_abstracts(self, json_file_path: str, batch_size: int = 100):
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        total_articles = sum(len(articles) for articles in data.values())
        processed_articles = 0

        batch = []
        with tqdm(total=total_articles, desc="Processing abstracts") as pbar:
            for source, articles in data.items():
                for article in articles:
                    abstract = article['abstract']
                    vector = self.vectorizer.vectorize_text(abstract)
                    metadata = {
                        "title": article['title'],
                        "id": article['id'],
                        "updated": article['updated'],
                        "source": source
                    }
                    batch.append((article['id'], vector, metadata))

                    if len(batch) >= batch_size:
                        self._store_batch(batch)
                        batch = []

                    processed_articles += 1
                    pbar.update(1)
                    pbar.set_postfix({"Completion": f"{processed_articles/total_articles:.2%}"})

            if batch:  # Store any remaining items
                self._store_batch(batch)

        # Save the database after processing all abstracts
        self.vector_database.save()

    def _store_batch(self, batch: List[Tuple[str, np.ndarray, Dict[str, Any]]]):
        for id, vector, metadata in batch:
            self.vector_database.add_vector(id, vector, metadata)
