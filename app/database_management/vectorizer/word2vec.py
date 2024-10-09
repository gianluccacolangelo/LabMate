from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from app.database_management.vectorizer.vectorizer_interface import IVectorizer
import numpy as np

class Word2VecVectorizer(IVectorizer):
    def __init__(self, vector_size=100, window=5, min_count=1):
        self.model = Word2Vec(vector_size=vector_size, window=window, min_count=min_count)
        self.is_fitted = False

    def fit(self, texts):
        processed_texts = [simple_preprocess(text) for text in texts]
        self.model.build_vocab(processed_texts)
        self.model.train(processed_texts, total_examples=len(processed_texts), epochs=10)
        self.is_fitted = True

    def vectorize_text(self, text: str) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Vectorizer must be fitted before vectorizing text")
        words = simple_preprocess(text)
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        if not word_vectors:
            return np.zeros(self.model.vector_size)
        return np.mean(word_vectors, axis=0)
