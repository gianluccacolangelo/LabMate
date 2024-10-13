import os
from app.database_management.vectorizer.bert import BertVectorizer
from app.database_management.vectorizer.bert import HuggingFaceVectorizer
from app.database_management.vector_database.vector_database import FaissVectorDatabase
from app.database_management.vector_database.abstract_processing import AbstractProcessingService

def main():
    # Define paths
    data_dir = 'data'
    index_file = os.path.join(data_dir, 'bge_vector_database_faiss_index.bin')
    metadata_file = os.path.join(data_dir, 'bge_vector_database_metadata.pkl')

    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)

    # We choose a vectorizer, in this case we use BERT
    vectorizer = HuggingFaceVectorizer(model_name='BAAI/bge-base-en-v1.5')
    vector_dimension = 768 # BERT base model output dimension

    # We choose a vector database admin, in this case we use Faiss
    vector_database = FaissVectorDatabase(dimension=vector_dimension, index_file=index_file, metadata_file=metadata_file)
    processing_service = AbstractProcessingService(vectorizer, vector_database)

    # Process and store abstracts
    processing_service.process_and_store_abstracts('database/weekly_articles_20241009.json')

    print(f"\nTotal vectors in database: {len(vector_database)}")

    # Example search
    #query = "machine learning in biology"
    #query_vector = vectorizer.vectorize_text(query)
    #results = vector_database.search(query_vector, top_k=5)
#
    #print(f"\nTop 5 results for query '{query}':")
    #for result in results:
    #    print(f"Title: {result['title']}")
    #    print(f"Distance: {result['distance']}")
    #    print(f"Source: {result['source']}")
    #    print("---")

if __name__ == "__main__":
    main()