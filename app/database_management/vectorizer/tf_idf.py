from sklearn.feature_extraction.text import TfidfVectorizer
from app.database_management.vectorizer.vectorizer_interface import IVectorizer
import numpy as np

class TfidfVectorizerWrapper(IVectorizer):
    def __init__(self, max_features=5000):
        self.vectorizer = TfidfVectorizer(max_features=max_features)
        self.is_fitted = False

    def fit(self, texts):
        self.vectorizer.fit(texts)
        self.is_fitted = True

    def vectorize_text(self, text: str) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Vectorizer must be fitted before vectorizing text")
        return self.vectorizer.transform([text]).toarray()[0]
