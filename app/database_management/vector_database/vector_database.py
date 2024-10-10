from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict, Any
import os
import pickle
import faiss

class VectorDatabase(ABC):
    @abstractmethod
    def add_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        pass

    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        pass

class FaissVectorDatabase(VectorDatabase):
    """
    A vector database implementation using FAISS for efficient similarity search.

    This class provides methods to add vectors, search for similar vectors,
    and save/load the database to/from disk.
    """

    def __init__(self, dimension: int, index_file: str = 'faiss_index.bin', metadata_file: str = 'metadata.pkl'):
        """
        Initialize the FaissVectorDatabase.

        Args:
            dimension (int): The dimensionality of the vectors.
            index_file (str): The file path to save/load the FAISS index.
            metadata_file (str): The file path to save/load the metadata.
        """
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = metadata_file
        
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.load()
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.id_to_metadata = {}

    def add_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        """
        Add a vector to the database with its associated metadata.

        Args:
            id (str): The unique identifier for the vector.
            vector (np.ndarray): The vector to be added.
            metadata (Dict[str, Any]): Additional information about the vector.
        """
        self.index.add(vector.reshape(1, -1))
        self.id_to_metadata[self.index.ntotal - 1] = {"id": id, **metadata}

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for the top-k most similar vectors to the query vector.

        Args:
            query_vector (np.ndarray): The query vector.
            top_k (int): The number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing search results.
        """
        distances, indices = self.index.search(query_vector.reshape(1, -1), top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # -1 indicates no match found
                result = self.id_to_metadata[idx].copy()
                result["distance"] = float(distances[0][i])
                results.append(result)
        return results

    def save(self):
        """
        Save the FAISS index and metadata to disk.
        """
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.id_to_metadata, f)

    def load(self):
        """
        Load the FAISS index and metadata from disk.
        """
        self.index = faiss.read_index(self.index_file)
        with open(self.metadata_file, 'rb') as f:
            self.id_to_metadata = pickle.load(f)

    def __len__(self):
        """
        Get the number of vectors in the database.

        Returns:
            int: The total number of vectors in the database.
        """
        return self.index.ntotal