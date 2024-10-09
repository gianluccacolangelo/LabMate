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
    def __init__(self, dimension: int, index_file: str = 'faiss_index.bin', metadata_file: str = 'metadata.pkl'):
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = metadata_file
        
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.load()
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.id_to_metadata = {}

    def add_vector(self, id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        self.index.add(vector.reshape(1, -1))
        self.id_to_metadata[self.index.ntotal - 1] = {"id": id, **metadata}

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        distances, indices = self.index.search(query_vector.reshape(1, -1), top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # -1 indicates no match found
                result = self.id_to_metadata[idx].copy()
                result["distance"] = float(distances[0][i])
                results.append(result)
        return results

    def save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.id_to_metadata, f)

    def load(self):
        self.index = faiss.read_index(self.index_file)
        with open(self.metadata_file, 'rb') as f:
            self.id_to_metadata = pickle.load(f)

    def __len__(self):
        return self.index.ntotal
