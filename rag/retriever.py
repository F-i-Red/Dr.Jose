# rag/retriever.py
import os
from pathlib import Path
from typing import List, Optional
import unicodedata

import chromadb
from sentence_transformers import SentenceTransformer

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())


class LegalRetriever:
    def __init__(self, collection_name: str = "leis_portuguesas"):
        self.collection_name = collection_name
        self.persist_directory = config.CHROMA_DIR

        self._client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        self._embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"✅ Coleção '{collection_name}' carregada com sucesso.")

    def is_ready(self) -> bool:
        try:
            return self._collection.count() > 0
        except:
            return False

    def add_documents(self, documents: List[str], metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None):
        if not documents:
            return

        if metadatas is None:
            metadatas = [{"source": "lei_portuguesa", "filename": f"doc_{i}"} for i in range(len(documents))]
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        texts_norm = [normalize_text(doc) for doc in documents]
        embeddings = self._embedder.encode(texts_norm, show_progress_bar=False).tolist()

        self._collection.add(
            documents=texts_norm,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"✅ Adicionados {len(documents)} documentos à base.")

    def get_context(self, query: str, k: int = 6) -> str:
        if not query or not query.strip():
            return "Nenhum artigo relevante encontrado."

        query_norm = normalize_text(query)
        query_embedding = self._embedder.encode([query_norm], show_progress_bar=False).tolist()

        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["documents", "metadatas"]
        )

        docs = results.get("documents", [[]])[0]
        if not docs:
            return "Nenhum artigo relevante foi encontrado na base de conhecimento para esta questão."

        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"--- Documento {i} ---\n{doc.strip()}\n")

        return "\n".join(context_parts)


# Compatibilidade
Retriever = LegalRetriever
