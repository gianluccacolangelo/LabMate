from transformers import BertTokenizer, BertModel
import torch
from app.database_management.vectorizer.vectorizer_interface import IVectorizer
import numpy as np

class BertVectorizer(IVectorizer):
    def __init__(self, model_name='bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()

    def vectorize_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
