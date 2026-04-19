# rag/retriever.py
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LegalRetriever:
    """Motor de busca semântica para legislação portuguesa"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Inicializa a base vetorial se existir"""
        try:
            if config.CHROMA_DB_DIR.exists() and any(config.CHROMA_DB_DIR.iterdir()):
                self.vectorstore = Chroma(
                    persist_directory=str(config.CHROMA_DB_DIR),
                    embedding_function=self.embeddings
                )
                logger.info("Base vetorial carregada com sucesso")
            else:
                logger.warning(f"Base vetorial não encontrada em {config.CHROMA_DB_DIR}")
                logger.info("Executa 'python scripts/ingest.py' primeiro")
        except Exception as e:
            logger.error(f"Erro ao carregar base vetorial: {str(e)}")
            self.vectorstore = None
    
    def retrieve(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """
        Recupera documentos relevantes para a query
        
        Args:
            query: Pergunta do utilizador
            k: Número de resultados (default do config)
        
        Returns:
            Lista de dicionários com conteúdo e metadados
        """
        if not self.vectorstore:
            logger.error("Base vetorial não disponível")
            return []
        
        k = k or config.TOP_K_RESULTS
        
        try:
            # Busca por similaridade
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Filtrar por threshold de similaridade
            filtered_results = []
            for doc, score in results:
                if score >= config.SIMILARITY_THRESHOLD:
                    filtered_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'similarity_score': score
                    })
            
            logger.info(f"Query: '{query[:50]}...' -> {len(filtered_results)} resultados (threshold: {config.SIMILARITY_THRESHOLD})")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Erro na recuperação: {str(e)}")
            return []
    
    def get_context(self, query: str, max_chars: int = 3000) -> str:
        """
        Formata os resultados recuperados como contexto para a LLM
        
        Args:
            query: Pergunta do utilizador
            max_chars: Máximo de caracteres do contexto
        
        Returns:
            String formatada com o contexto
        """
        results = self.retrieve(query)
        
        if not results:
            return "Nenhum documento relevante encontrado na base de conhecimento."
        
        context_parts = []
        total_chars = 0
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            content = result['content']
            score = result['similarity_score']
            
            # Formatar metadados
            source = metadata.get('source', 'documento')
            article = metadata.get('article', '')
            
            header = f"[Documento {i}] Fonte: {source}"
            if article:
                header += f" | {article}"
            header += f" (relevância: {score:.2f})\n"
            
            entry = header + content.strip() + "\n"
            
            if total_chars + len(entry) > max_chars:
                # Cortar se exceder
                remaining = max_chars - total_chars
                if remaining > 200:  # Só adiciona se sobrar espaço útil
                    entry = entry[:remaining] + "...\n"
                else:
                    break
            
            context_parts.append(entry)
            total_chars += len(entry)
        
        return "\n---\n".join(context_parts)
    
    def is_ready(self) -> bool:
        """Verifica se o retriever está pronto para uso"""
        return self.vectorstore is not None
