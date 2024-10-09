from abc import ABC, abstractmethod
import numpy as np

# Vectorizer Interface
class IVectorizer(ABC):
    @abstractmethod
    def vectorize_text(self, text: str) -> np.ndarray:
        pass


