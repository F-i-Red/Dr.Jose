import os
from typing import List

from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from utils.logger import setup_logger

logger = setup_logger(__name__)


class LegalRetriever:
    def __init__(
        self,
        collection_name: str = "leis_portuguesas",
        persist_directory: str = "data/chroma",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        self.client = Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        self.embedder = SentenceTransformer(model_name)

        logger.info(f"✅ Coleção '{collection_name}' carregada com sucesso.")

    def _embed(self, texts: List[str]):
        return self.embedder.encode(texts).tolist()

    def add_documents(self, texts: List[str]):
        if not texts:
            return

        ids = [str(i) for i in range(len(texts))]
        embeddings = self._embed(texts)

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
        )

        logger.info(f"✅ Adicionados {len(texts)} documentos à base.")

    def query(self, question: str, k: int = 5) -> List[str]:
        if not question.strip():
            return ["Pergunta vazia."]

        query_embedding = self._embed([question])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
        )

        docs = results.get("documents", [[]])[0]

        if not docs:
            return ["Nenhum artigo relevante encontrado."]

        return docs
