# config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LEIS_DIR = DATA_DIR / "leis"
    CHROMA_DIR = DATA_DIR / "chroma"
    LOGS_DIR = BASE_DIR / "logs"

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Modelos gratuitos mais estáveis em abril 2026
    OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

    def validate(self):
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY não encontrada no ficheiro .env")
        
        if not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            raise ValueError("Chave OpenRouter inválida. Deve começar com 'sk-or-'")

        # Criar pastas
        for d in [self.DATA_DIR, self.LEIS_DIR, self.CHROMA_DIR, self.LOGS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

config = Config()
