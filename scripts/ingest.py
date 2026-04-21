# scripts/ingest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.retriever import LegalRetriever
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

def main():
    print("\n" + "="*60)
    print("📚 Dr. José - Indexação da Base de Conhecimento")
    print("="*60)

    retriever = LegalRetriever()

    # Carregar todos os ficheiros .txt
    files = list(config.LEIS_DIR.glob("*.txt"))
    if not files:
        print("❌ Nenhum ficheiro encontrado em data/leis/")
        return

    print(f"📄 Encontrados {len(files)} ficheiros de leis.")

    all_texts = []
    for file in files:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
            if len(text.strip()) > 100:
                all_texts.append(text)
                logger.info(f"Carregado: {file.name} ({len(text)} caracteres)")
        except Exception as e:
            logger.warning(f"Erro ao ler {file.name}: {e}")

    if not all_texts:
        print("❌ Nenhum conteúdo válido encontrado.")
        return

    # Indexar
    retriever.add_documents(all_texts)
    print(f"✅ Indexação concluída! Total de documentos: {len(all_texts)}")
    print("Podes agora usar o bot: python -m bot.jose")

if __name__ == "__main__":
    main()
