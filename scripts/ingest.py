# scripts/ingest.py
import sys
from pathlib import Path
from typing import List, Dict, Any

# Adicionar raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import re

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LegalDocumentProcessor:
    """Processador especializado para documentos jurídicos portugueses"""
    
# scripts/ingest.py (versão atualizada - adicionar no início)
from fetch_laws import LawFetcher

def main():
    """Função principal com download automático"""
    logger.info("=== INICIANDO INDEXAÇÃO DE DOCUMENTOS LEGAIS ===")
    
    # 1. Buscar leis online primeiro
    fetcher = LawFetcher()
    print("\n📡 A verificar atualizações das leis...")
    
    if fetcher.fetch_all():
        print("✅ Leis atualizadas/download concluído")
    else:
        print("⚠️ Algumas leis não foram obtidas. Usando ficheiros existentes...")
    
    # 2. Continuar com o processamento normal...
    # (resto do código do ingest.py que já tens)
        
        def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        
    def chunk_by_legal_structure(self, text: str, metadata: Dict) -> List[Document]:
        """
        Chunking inteligente que respeita artigos e secções legais
        """
        documents = []
        
        # Padrões para legislação portuguesa
        article_pattern = r'(Art(?:igo)?[º°]?\s*\d+[º°]?\.?\s*-?\s*)([^A-Z][\s\S]*?)(?=Art(?:igo)?[º°]?\s*\d+|CAPÍTULO|SECÇÃO|LIVRO|TÍTULO|$|\n\n\n)'
        section_pattern = r'(CAPÍTULO\s+[IVXLCDM]+\s*-?\s*[^\n]+|SECÇÃO\s+[IVXLCDM]+\s*-?\s*[^\n]+|LIVRO\s+[IVXLCDM]+\s*-?\s*[^\n]+)'
        
        # Primeiro, tentar dividir por artigos
        articles = re.split(article_pattern, text, flags=re.IGNORECASE | re.DOTALL)
        
        if len(articles) > 1:
            # Tem estrutura de artigos
            for i in range(1, len(articles), 2):
                if i+1 < len(articles):
                    article_num = articles[i].strip()
                    article_content = articles[i+1].strip()
                    
                    if len(article_content) > 100:  # Ignorar muito pequeno
                        full_text = f"{article_num} {article_content}"
                        doc_metadata = metadata.copy()
                        doc_metadata['article'] = article_num
                        doc_metadata['chunk_type'] = 'article'
                        
                        documents.append(Document(
                            page_content=full_text[:config.CHUNK_SIZE],
                            metadata=doc_metadata
                        ))
        
        # Se não encontrou artigos, chunking normal mas com overlap
        if not documents:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP,
                separators=["\n\n", "\n", " ", ""],
                length_function=len
            )
            chunks = text_splitter.split_text(text)
            
            for chunk in chunks:
                doc_metadata = metadata.copy()
                doc_metadata['chunk_type'] = 'semantic'
                documents.append(Document(
                    page_content=chunk,
                    metadata=doc_metadata
                ))
        
        logger.info(f"Criados {len(documents)} chunks do documento {metadata.get('source', 'desconhecido')}")
        return documents
    
    def load_documents(self) -> List[Document]:
        """Carrega todos os documentos da pasta data/leis"""
        documents = []
        
        # Extensões suportadas
        extensions = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader
        }
        
        for file_path in config.LEIS_DIR.iterdir():
            if file_path.suffix.lower() in extensions:
                try:
                    logger.info(f"A processar: {file_path.name}")
                    
                    # Carregar conforme extensão
                    if file_path.suffix.lower() == '.txt':
                        loader = TextLoader(str(file_path), encoding='utf-8')
                        raw_docs = loader.load()
                    else:  # PDF
                        loader = PyPDFLoader(str(file_path))
                        raw_docs = loader.load()
                    
                    # Processar cada documento
                    for doc in raw_docs:
                        metadata = {
                            'source': file_path.name,
                            'file_type': file_path.suffix,
                            'diploma': file_path.stem
                        }
                        
                        # Chunking inteligente
                        chunks = self.chunk_by_legal_structure(doc.page_content, metadata)
                        documents.extend(chunks)
                        
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path.name}: {str(e)}")
            else:
                logger.warning(f"Extensão não suportada: {file_path.name}")
        
        logger.info(f"Total de documentos carregados: {len(documents)}")
        return documents
    
    def create_vectorstore(self, documents: List[Document], force_recreate: bool = False):
        """Cria ou atualiza a base vetorial"""
        try:
            if force_recreate and config.CHROMA_DB_DIR.exists():
                import shutil
                shutil.rmtree(config.CHROMA_DB_DIR)
                logger.info("Base vetorial removida (force_recreate=True)")
            
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(config.CHROMA_DB_DIR)
            )
            self.vectorstore.persist()
            logger.info(f"Base vetorial criada/atualizada com {len(documents)} documentos")
            
        except Exception as e:
            logger.error(f"Erro ao criar base vetorial: {str(e)}")
            raise

def main():
    """Função principal"""
    logger.info("=== INICIANDO INDEXAÇÃO DE DOCUMENTOS LEGAIS ===")
    
    try:
        # Validar configuração
        config.validate()
        
        # Processar documentos
        processor = LegalDocumentProcessor()
        documents = processor.load_documents()
        
        if not documents:
            logger.error("Nenhum documento encontrado ou processado!")
            logger.info(f"Por favor, adiciona ficheiros .txt ou .pdf em: {config.LEIS_DIR}")
            sys.exit(1)
        
        # Criar base vetorial
        processor.create_vectorstore(documents, force_recreate=True)
        
        logger.info("=== INDEXAÇÃO CONCLUÍDA COM SUCESSO ===")
        
        # Estatísticas
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"   - Documentos processados: {len(set([d.metadata.get('source') for d in documents]))}")
        logger.info(f"   - Total de chunks: {len(documents)}")
        logger.info(f"   - Base vetorial: {config.CHROMA_DB_DIR}")
        
    except Exception as e:
        logger.error(f"Falha na indexação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
