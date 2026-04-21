# bot/jose.py
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from rag.retriever import LegalRetriever
from utils.logger import setup_logger
from openai import OpenAI

logger = setup_logger(__name__)

class DrJoseBot:
    SYSTEM_PROMPT = """Tu és o Dr. José, advogado português. Responde sempre de forma curta, clara e direta.

Formato obrigatório (não acrescentes nada fora disto):

Resposta direta: [resposta em 1 ou 2 frases]

Fundamentação: Artigo XXX.º do [Nome do Diploma] - [resumo curto]

Nota: Esta é uma resposta informativa. Não substitui aconselhamento jurídico profissional."""

    def __init__(self):
        logger.info("Inicializando Dr. José...")
        config.validate()
        self.retriever = LegalRetriever()
        self.conversation_history: List[Dict[str, Any]] = []
        self.client = OpenAI(base_url=config.OPENROUTER_BASE_URL, api_key=config.OPENROUTER_API_KEY)

    def get_response(self, user_input: str) -> str:
        context = self.retriever.get_context(user_input)

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if context and len(context.strip()) > 50:
            messages.append({"role": "user", "content": f"Contexto:\n{context}\nPergunta: {user_input}"})
        else:
            messages.append({"role": "user", "content": f"Pergunta: {user_input}"})

        models_to_try = [
            "openrouter/free",                       # router automático
            "nvidia/nemotron-3-super-120b-a12b:free",
            "meta-llama/llama-3.3-70b-instruct:free",
        ]

        for model in models_to_try:
            logger.info(f"Tentando: {model}")
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=350,        # limite baixo para forçar concisão
                    timeout=40
                )
                answer = response.choices[0].message.content.strip()
                return answer
            except Exception as e:
                logger.warning(f"Modelo {model} falhou")
                continue

        return "Não foi possível obter resposta neste momento. Tenta novamente dentro de alguns minutos."

    def run(self):
        print("\n" + "="*75)
        print("⚖️  Dr. José - Assistente Jurídico Português")
        print("="*75)
        print("Escreve a tua pergunta. Usa /sair para terminar.\n")

        while True:
            try:
                user_input = input("Você: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['/sair', 'sair']:
                    print("Dr. José: Até breve!")
                    break

                print("Dr. José: A consultar a legislação...")
                answer = self.get_response(user_input)
                print(f"\nDr. José: {answer}\n")

            except KeyboardInterrupt:
                print("\nAté breve!")
                break
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    bot = DrJoseBot()
    bot.run()
