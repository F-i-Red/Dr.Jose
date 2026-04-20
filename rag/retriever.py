# rag/retriever.py

import os
import unicodedata
from typing import List

from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


def normalize_text(text: str) -> str:
    """Limpeza e normalização de texto"""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())


class LegalRetriever:
    def __init__(
        self,
        collection_name: str = "leis_portuguesas",
        persist_directory: str = "data/chroma",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        self.client = Client(
            Settings(
                persist_directory=persist_directory
            )
        )

        self.collection = self.client.get_or_create_collection(collection_name)
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]):
        texts = [normalize_text(t) for t in texts]
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def add_documents(self, texts: List[str]):
        if not texts:
            return

        embeddings = self.embed(texts)

        ids = [f"doc_{i}" for i in range(len(texts))]

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings
        )

    def get_context(self, query: str, k: int = 5) -> str:
        query = normalize_text(query)
        if not query:
            return ""

        embedding = self.embed([query])[0]

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )

        docs = results.get("documents", [[]])[0]

        if not docs:
            return ""

        return "\n\n".join(docs)
