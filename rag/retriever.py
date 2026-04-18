"""
Dr. José — Motor de Pesquisa Semântica (RAG)
=============================================
Pesquisa os fragmentos de lei mais relevantes para
uma dada pergunta, usando similaridade semântica.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

CHROMA_DIR      = Path(os.getenv("CHROMA_DIR", "data/chroma_db"))
COLLECTION      = os.getenv("CHROMA_COLLECTION", "legislacao_portuguesa")
RAG_TOP_K       = int(os.getenv("RAG_TOP_K", "5"))
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class Retriever:
    """Pesquisa semântica na base de conhecimento jurídico."""

    def __init__(self):
        if not CHROMA_DIR.exists():
            raise FileNotFoundError(
                f"Base vetorial não encontrada em '{CHROMA_DIR}'.\n"
                "Executa primeiro: python scripts/ingest.py"
            )

        cliente = chromadb.PersistentClient(path=str(CHROMA_DIR))

        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

        self.colecao = cliente.get_collection(
            name=COLLECTION,
            embedding_function=ef,
        )

        print(f"✅ Base jurídica carregada — {self.colecao.count()} fragmentos indexados.")

    def pesquisar(self, pergunta: str, k: int = RAG_TOP_K) -> list[dict]:
        """
        Pesquisa os k fragmentos mais relevantes para a pergunta.

        Retorna lista de dicionários:
            [{"texto": "...", "fonte": "...", "score": 0.92}, ...]
        """
        resultados = self.colecao.query(
            query_texts=[pergunta],
            n_results=min(k, self.colecao.count()),
            include=["documents", "metadatas", "distances"],
        )

        fragmentos = []
        docs      = resultados["documents"][0]
        metadados = resultados["metadatas"][0]
        distancias = resultados["distances"][0]

        for doc, meta, dist in zip(docs, metadados, distancias):
            score = 1 - dist  # converter distância cosine em similaridade
            fragmentos.append({
                "texto":  doc,
                "fonte":  meta.get("fonte", "desconhecida"),
                "chunk":  meta.get("chunk", 0),
                "score":  round(score, 4),
            })

        # Ordenar por relevância decrescente
        fragmentos.sort(key=lambda x: x["score"], reverse=True)
        return fragmentos

    def formatar_contexto(self, pergunta: str, k: int = RAG_TOP_K) -> str:
        """
        Devolve um bloco de texto formatado com os fragmentos mais relevantes,
        pronto a inserir no prompt do Dr. José.
        """
        fragmentos = self.pesquisar(pergunta, k)

        if not fragmentos:
            return "Não foram encontrados documentos relevantes na base de conhecimento."

        linhas = ["## Legislação Relevante Encontrada\n"]

        for i, f in enumerate(fragmentos, 1):
            linhas.append(f"### [{i}] Fonte: {f['fonte']} (relevância: {f['score']:.0%})")
            linhas.append(f["texto"])
            linhas.append("")

        return "\n".join(linhas)


# ── Teste rápido ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Teste do Retriever RAG\n" + "=" * 40)

    retriever = Retriever()

    perguntas_teste = [
        "O que é um crime de furto?",
        "Quais são os direitos fundamentais dos cidadãos?",
        "O que diz a lei sobre violência doméstica?",
    ]

    for pergunta in perguntas_teste:
        print(f"\n🔍 Pergunta: {pergunta}")
        resultados = retriever.pesquisar(pergunta, k=2)
        for r in resultados:
            print(f"  📄 {r['fonte']} — score: {r['score']:.2f}")
            print(f"     {r['texto'][:120]}...")
