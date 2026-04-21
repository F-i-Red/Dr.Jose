# scripts/ingest.py
"""
Indexa os ficheiros de legislação portuguesa na base vetorial ChromaDB.
Executa DEPOIS de fetch_laws.py (ou com ficheiros .txt já em data/leis/).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.retriever import LegalRetriever, normalize_text

BASE_DIR = Path(__file__).resolve().parent.parent
LEIS_DIR = BASE_DIR / "data" / "leis"


def load_documents():
    """Carrega todos os .txt e .pdf da pasta data/leis/"""
    texts = []
    names = []

    # Ficheiros .txt
    for file in sorted(LEIS_DIR.glob("*.txt")):
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            content = normalize_text(content)
            if content and len(content) > 100:
                texts.append(content)
                names.append(file.stem)
                print(f"  📄 {file.name} ({len(content):,} caracteres)")
        except Exception as e:
            print(f"  ❌ Erro ao ler {file.name}: {e}")

    # Ficheiros .pdf (se existirem)
    try:
        import fitz  # PyMuPDF
        for file in sorted(LEIS_DIR.glob("*.pdf")):
            try:
                doc = fitz.open(str(file))
                content = ""
                for page in doc:
                    content += page.get_text()
                doc.close()
                content = normalize_text(content)
                if content and len(content) > 100:
                    texts.append(content)
                    names.append(file.stem)
                    print(f"  📄 {file.name} ({len(content):,} caracteres)")
            except Exception as e:
                print(f"  ❌ Erro ao ler {file.name}: {e}")
    except ImportError:
        pass  # PyMuPDF opcional

    return texts, names


def main():
    print("\n" + "=" * 60)
    print("📚 Dr. José - Indexação de Legislação Portuguesa")
    print("=" * 60)

    if not LEIS_DIR.exists():
        print(f"\n❌ Pasta não encontrada: {LEIS_DIR}")
        print("   Executa primeiro: python scripts/fetch_laws.py")
        return

    print(f"\n📂 A carregar ficheiros de: {LEIS_DIR}")
    texts, names = load_documents()

    if not texts:
        print("\n⚠️  Nenhum ficheiro encontrado em data/leis/")
        print("   Executa primeiro: python scripts/fetch_laws.py")
        return

    print(f"\n⚙️  A indexar {len(texts)} documento(s)...")
    retriever = LegalRetriever()
    retriever.add_documents(texts, source_names=names)

    total = retriever.collection.count()
    print(f"\n✅ Indexação concluída! Total de fragmentos na base: {total}")
    print("\nAgora podes iniciar o Dr. José:")
    print("   streamlit run app.py")


if __name__ == "__main__":
    main()
