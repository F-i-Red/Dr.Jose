import os
import uuid
from pathlib import Path
from typing import List, Tuple

from rag.retriever import LegalRetriever, normalize_text


BASE_DIR = Path(__file__).resolve().parent.parent
LEIS_DIR = BASE_DIR / "data" / "leis"


def load_text_files() -> List[Tuple[str, str, str]]:
    docs: List[Tuple[str, str, str]] = []

    for path in LEIS_DIR.rglob("*.txt"):
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        text = normalize_text(raw)
        if not text:
            continue

        doc_id = str(uuid.uuid4())
        metadata = f"ficheiro={path.name}; caminho={path}"

        docs.append((doc_id, text, metadata))

    return docs


def main():
    if not LEIS_DIR.exists():
        raise RuntimeError(f"Pasta de leis não encontrada: {LEIS_DIR}")

    retriever = LegalRetriever()
    docs = load_text_files()

    if not docs:
        print("⚠️ Nenhum ficheiro .txt encontrado em data/leis/.")
        return

    print(f"📚 A indexar {len(docs)} documentos...")
    retriever.add_documents(docs)
    print("✅ Indexação concluída.")


if __name__ == "__main__":
    main()
