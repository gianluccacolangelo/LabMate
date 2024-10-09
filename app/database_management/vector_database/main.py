import os
from app.database_management.vectorizer.bert import BertVectorizer
from app.database_management.vector_database.vector_database import FaissVectorDatabase
from app.database_management.vector_database.abstract_processing import AbstractProcessingService

def main():
    # Define paths
    data_dir = 'data'
    index_file = os.path.join(data_dir, 'faiss_index.bin')
    metadata_file = os.path.join(data_dir, 'metadata.pkl')

    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Initialize components
    vectorizer = BertVectorizer(model_name='bert-base-uncased')
    vector_dimension = 768  # BERT base model output dimension
    vector_database = FaissVectorDatabase(dimension=vector_dimension, index_file=index_file, metadata_file=metadata_file)
    processing_service = AbstractProcessingService(vectorizer, vector_database)

    # Process and store abstracts
    json_file_path = 'database/weekly_articles_20241009.json'
    processing_service.process_and_store_abstracts(json_file_path)

    print(f"\nTotal vectors in database: {len(vector_database)}")

    # Example search
    query = "machine learning in biology"
    query_vector = vectorizer.vectorize_text(query)
    results = vector_database.search(query_vector, top_k=5)

    print(f"\nTop 5 results for query '{query}':")
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Distance: {result['distance']}")
        print(f"Source: {result['source']}")
        print("---")

if __name__ == "__main__":
    main()