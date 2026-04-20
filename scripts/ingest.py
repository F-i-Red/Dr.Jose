# scripts/ingest.py

from pathlib import Path
from rag.retriever import LegalRetriever, normalize_text


BASE_DIR = Path(__file__).resolve().parent.parent
LEIS_DIR = BASE_DIR / "data" / "leis"


def load_documents():
    texts = []

    for file in LEIS_DIR.glob("*.txt"):
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            content = normalize_text(content)

            if content:
                texts.append(content)

        except Exception as e:
            print(f"Erro ao ler {file}: {e}")

    return texts


def main():
    if not LEIS_DIR.exists():
        print(f"Pasta não encontrada: {LEIS_DIR}")
        return

    retriever = LegalRetriever()

    docs = load_documents()

    if not docs:
        print("Nenhum ficheiro encontrado em data/leis/")
        return

    print(f"A indexar {len(docs)} documentos...")

    retriever.add_documents(docs)

    print("Indexação concluída com sucesso.")


if __name__ == "__main__":
    main()
