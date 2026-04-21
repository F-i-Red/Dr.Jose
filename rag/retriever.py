# rag/retriever.py

import unicodedata
from pathlib import Path
from typing import List

import chromadb
from sentence_transformers import SentenceTransformer


def normalize_text(text: str) -> str:
    """Limpeza e normalização de texto."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Divide um texto longo em fragmentos (chunks) com sobreposição.
    Tenta dividir em pontos naturais (fim de frase/artigo).
    """
    if not text:
        return []

    # Tentar dividir por artigos (padrão "Artigo X.º")
    import re
    artigo_pattern = re.compile(r'(Artigo\s+\d+\.º)', re.IGNORECASE)
    partes = artigo_pattern.split(text)

    chunks = []
    buffer = ""

    for parte in partes:
        if len(buffer) + len(parte) < chunk_size:
            buffer += parte
        else:
            if buffer.strip():
                chunks.append(buffer.strip())
            buffer = parte

    if buffer.strip():
        chunks.append(buffer.strip())

    # Se não conseguiu dividir por artigos, divide por tamanho
    if len(chunks) <= 1:
        chunks = []
        words = text.split()
        current = []
        current_len = 0

        for word in words:
            current.append(word)
            current_len += len(word) + 1
            if current_len >= chunk_size:
                chunks.append(" ".join(current))
                # Overlap: manter últimas palavras
                overlap_words = current[-overlap // 5:] if overlap > 0 else []
                current = overlap_words
                current_len = sum(len(w) + 1 for w in current)

        if current:
            chunks.append(" ".join(current))

    return [c for c in chunks if len(c.strip()) > 50]


class LegalRetriever:
    def __init__(
        self,
        collection_name: str = "leis_portuguesas",
        persist_directory: str = "data/chroma",
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        # CORREÇÃO: usar PersistentClient (chromadb >= 0.4)
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        texts = [normalize_text(t) for t in texts]
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def add_documents(self, texts: List[str], source_names: List[str] = None):
        """Adiciona documentos à coleção, dividindo em chunks primeiro."""
        if not texts:
            return

        all_chunks = []
        all_ids = []
        all_metadatas = []

        chunk_index = 0
        for doc_idx, text in enumerate(texts):
            source = source_names[doc_idx] if source_names else f"doc_{doc_idx}"
            chunks = chunk_text(text)
            print(f"  '{source}': {len(chunks)} fragmentos")

            for chunk in chunks:
                all_chunks.append(chunk)
                all_ids.append(f"chunk_{chunk_index}")
                all_metadatas.append({"source": source, "doc_index": doc_idx})
                chunk_index += 1

        if not all_chunks:
            print("Nenhum fragmento gerado.")
            return

        # Processar em lotes para não sobrecarregar memória
        batch_size = 50
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_ids = all_ids[i:i + batch_size]
            batch_metas = all_metadatas[i:i + batch_size]
            batch_embeddings = self.embed(batch_chunks)

            # Verificar quais IDs já existem para evitar duplicados
            existing = self.collection.get(ids=batch_ids)
            existing_ids = set(existing["ids"])
            
            new_chunks = [(c, id_, m, e) for c, id_, m, e in 
                         zip(batch_chunks, batch_ids, batch_metas, batch_embeddings)
                         if id_ not in existing_ids]
            
            if new_chunks:
                chunks_to_add, ids_to_add, metas_to_add, embs_to_add = zip(*new_chunks)
                self.collection.add(
                    ids=list(ids_to_add),
                    documents=list(chunks_to_add),
                    embeddings=list(embs_to_add),
                    metadatas=list(metas_to_add),
                )

        print(f"✅ Total indexado: {len(all_chunks)} fragmentos")

    def get_context(self, query: str, k: int = 5) -> str:
        """Pesquisa os fragmentos mais relevantes para a query."""
        query = normalize_text(query)
        if not query:
            return ""

        count = self.collection.count()
        if count == 0:
            return ""

        k = min(k, count)
        embedding = self.embed([query])[0]

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas"]
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        if not docs:
            return ""

        # Formatar com fonte
        parts = []
        for doc, meta in zip(docs, metas):
            source = meta.get("source", "desconhecida") if meta else "desconhecida"
            parts.append(f"[{source}]\n{doc}")

        return "\n\n---\n\n".join(parts)
