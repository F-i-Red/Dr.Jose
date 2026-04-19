import os
import unicodedata
from typing import List, Tuple

from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


def normalize_text(text: str) -> str:
    """
    Normaliza texto para reduzir ruído:
    - Unicode NFKC
    - remove quebras de linha redundantes
    - trim espaços
    """
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
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self._client = Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory,
            )
        )
        self._collection = self._client.get_or_create_collection(collection_name)
        self._embedder = SentenceTransformer(model_name)

    def _embed(self, texts: List[str]):
        texts_norm = [normalize_text(t) for t in texts]
        return self._embedder.encode(texts_norm, show_progress_bar=False).tolist()

    def add_documents(
        self,
        docs: List[Tuple[str, str, str]],
    ) -> None:
        """
        docs: lista de tuplos (id, texto, metadata_json_str)
        """
        if not docs:
            return

        ids = [d[0] for d in docs]
        texts = [normalize_text(d[1]) for d in docs]
        metadatas = [{"raw": d[2]} for d in docs]

        embeddings = self._embed(texts)

        self._collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(self, question: str, k: int = 5) -> List[str]:
        """
        Devolve até k excertos de lei relevantes.
        Se nada for encontrado, devolve um fallback explícito.
        """
        question_norm = normalize_text(question)
        if not question_norm:
            return ["Pergunta vazia. Reformula a tua questão."]

        query_emb = self._embed([question_norm])[0]

        results = self._collection.query(
            query_embeddings=[query_emb],
            n_results=k,
        )

        docs = results.get("documents", [[]])[0] if results else []

        if not docs:
            return [
                "Nenhum artigo relevante foi encontrado na base de conhecimento para esta questão."
            ]

        return [normalize_text(d) for d in docs]
