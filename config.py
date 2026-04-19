# config.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Diretórios do projeto
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LEIS_DIR = DATA_DIR / "leis"
    CHROMA_DIR = DATA_DIR / "chroma"

    # Configuração OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # === MODELOS RECOMENDADOS (escolhe um) ===
    
    # Opção 1: Claude 3.5 Sonnet (melhor qualidade jurídica)
    OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"
    
    # Opção 2: Versão mais estável (se a de cima falhar)
    # OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet-20240620"
    
    # Opção 3: Modelo gratuito / barato (recomendado para testes)
    # OPENROUTER_MODEL = "google/gemini-flash-1.5"
    
    # Opção 4: DeepSeek gratuito (muito bom e rápido)
    # OPENROUTER_MODEL = "deepseek/deepseek-chat:free"

    def validate(self):
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY não encontrada no ficheiro .env")
        if not self.OPENROUTER_API_KEY.startswith("sk-or-"):
            raise ValueError("A chave parece inválida. Deve começar com 'sk-or-'")
        
        # Cria pastas necessárias
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LEIS_DIR.mkdir(exist_ok=True)
        self.CHROMA_DIR.mkdir(exist_ok=True)

# Instância global
config = Config()
