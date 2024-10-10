import json
from typing import Dict, Any, List, Tuple
import numpy as np
from tqdm import tqdm
from app.database_management.vectorizer.vectorizer_interface import IVectorizer
from app.database_management.vector_database.vector_database import VectorDatabase

class AbstractProcessingService:
    """
    A service for processing and storing abstracts in a vector database.

    This class provides functionality to process abstracts from a JSON file,
    vectorize them, and store them in a vector database. Here we use a strategy
    pattern to allow for different vectorizers like tfidf, bert, word2vec, etc.
    And different 'vector_databases' like faiss, annoy, etc. to perform the search,
    and store of the vectors.
    """

    def __init__(self, vectorizer: IVectorizer, vector_database: VectorDatabase):
        """
        Initialize the AbstractProcessingService.

        Args:
            vectorizer (IVectorizer): An instance of a vectorizer to convert text to vectors.
            vector_database (VectorDatabase): An instance of a vector database to store the vectors.
        """
        self.vectorizer = vectorizer
        self.vector_database = vector_database

    def process_and_store_abstracts(self, json_file_path: str, batch_size: int = 100):
        """
        Process abstracts from a JSON file and store them in the vector database.

        This method reads a JSON file containing article data, processes each abstract,
        vectorizes it, and stores it in the vector database in batches.

        Args:
            json_file_path (str): The path to the JSON file containing the article data.
            batch_size (int, optional): The number of articles to process in each batch. Defaults to 100.
        """
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
                        "pdf_url": article['pdf_url'],
                        "source": source,
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
        """
        Store a batch of processed articles in the vector database.

        Args:
            batch (List[Tuple[str, np.ndarray, Dict[str, Any]]]): A list of tuples containing
                the article ID, vector representation, and metadata for each article.
        """
        for id, vector, metadata in batch:
            self.vector_database.add_vector(id, vector, metadata)