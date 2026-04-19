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
    OPENROUTER_MODEL = "deepseek/deepseek-chat:free"   # estável e gratuito

    def validate(self):
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY não encontrada no .env")
        if not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            raise ValueError("Chave OpenRouter inválida (deve começar com sk-or-)")

        # Criar pastas
        for directory in [self.DATA_DIR, self.LEIS_DIR, self.CHROMA_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

config = Config()
