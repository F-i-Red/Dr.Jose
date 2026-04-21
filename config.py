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

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Modelo estável recomendado neste momento (Llama 3.3 70B free)
    OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

    def validate(self):
        if not self.OPENROUTER_API_KEY or not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            raise ValueError(
                "OPENROUTER_API_KEY inválida ou não encontrada.\n"
                "1. Copia .env.example → .env\n"
                "2. Coloca a tua chave de https://openrouter.ai/keys"
            )

        for directory in [self.DATA_DIR, self.LEIS_DIR, self.CHROMA_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

config = Config()
