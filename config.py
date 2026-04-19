# config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Diretórios
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LEIS_DIR = DATA_DIR / "leis"
    CHROMA_DIR = DATA_DIR / "chroma"

    # OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Modelo estável e disponível (Google Gemini Flash 1.5 - gratuito e rápido)
    OPENROUTER_MODEL = "google/gemini-flash-1.5"

    def validate(self):
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY não encontrada no ficheiro .env")
        
        if not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            raise ValueError("Chave OpenRouter inválida. Deve começar com 'sk-or-'")
        
        # Cria pastas
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LEIS_DIR.mkdir(exist_ok=True)
        self.CHROMA_DIR.mkdir(exist_ok=True)

# Instância global
config = Config()
