# scripts/ingest.py
import sys
from pathlib import Path
import uuid
from typing import List, Tuple

# === IMPORTANTE: Adiciona a raiz do projeto ao sys.path ===
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.retriever import LegalRetriever, normalize_text
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

def load_text_files() -> List[Tuple[str, str, dict]]:
    """Carrega todos os ficheiros .txt da pasta data/leis/"""
    leis_dir = config.LEIS_DIR
    if not leis_dir.exists():
        logger.error(f"Pasta de leis não encontrada: {leis_dir}")
        print(f"❌ Erro: Pasta {leis_dir} não existe.")
        print("   Cria a pasta e coloca os ficheiros .txt das leis ou executa fetch_laws primeiro.")
        return []

    documents = []
    for txt_file in leis_dir.glob("*.txt"):
        try:
            content = txt_file.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue
                
            normalized = normalize_text(content)
            if len(normalized) < 50:  # ignora ficheiros quase vazios
                continue
                
            doc_id = f"doc_{uuid.uuid4().hex[:12]}"
            metadata = {
                "filename": txt_file.name,
                "source": "DRE" if "dre" in txt_file.name.lower() else "local",
                "path": str(txt_file)
            }
            
            documents.append((doc_id, normalized, metadata))
            
        except Exception as e:
            logger.warning(f"Erro ao ler {txt_file.name}: {e}")

    return documents


def main():
    print("\n" + "="*60)
    print("📚 Dr. José - Indexação da Base de Conhecimento Legal")
    print("="*60)
    
    # Carregar documentos
    docs = load_text_files()
    
    if not docs:
        print("⚠️  Nenhum documento válido encontrado em data/leis/")
        print("   Sugestão: Executa primeiro: python scripts/fetch_laws.py")
        return
    
    print(f"📄 Encontrados {len(docs)} documentos para indexar...")
    
    # Indexar
    try:
        retriever = LegalRetriever()
        doc_texts = [doc[1] for doc in docs]
        metadatas = [doc[2] for doc in docs]
        ids = [doc[0] for doc in docs]
        
        retriever.add_documents(documents=doc_texts, metadatas=metadatas, ids=ids)
        
        print("✅ Indexação concluída com sucesso!")
        print(f"   Total de documentos na base: {retriever._collection.count()}")
        print("\nAgora podes testar o bot com:")
        print("   python -m bot.jose")
        
    except Exception as e:
        logger.error(f"Erro durante indexação: {e}")
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
