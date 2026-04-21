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

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Não define modelo fixo aqui — o jose.py já tem fallback automático
    OPENROUTER_MODEL = None

    def validate(self):
        if not self.OPENROUTER_API_KEY or not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            raise ValueError("OPENROUTER_API_KEY inválida ou não encontrada no .env")

        for d in [self.DATA_DIR, self.LEIS_DIR, self.CHROMA_DIR]:
            d.mkdir(parents=True, exist_ok=True)

config = Config()
