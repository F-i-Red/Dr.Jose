# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configuração centralizada da aplicação"""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LEIS_DIR = DATA_DIR / "leis"
    CHROMA_DB_DIR = DATA_DIR / "chroma_db"
    LOGS_DIR = BASE_DIR / "logs"
    
    # ChromaDB
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # RAG
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.6))
    
    # Validação
    @classmethod
    def validate(cls):
        """Valida configurações essenciais"""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY não definida no ficheiro .env")
        
        # Criar diretórios necessários
        for dir_path in [cls.LEIS_DIR, cls.CHROMA_DB_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return True

# Instância global
config = Config()
