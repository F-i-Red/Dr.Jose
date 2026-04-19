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
    SYSTEM_PROMPT = """Tu és o Dr. José, um assistente jurídico português especializado em direito português.

Regras obrigatórias:
- Responde sempre com base no contexto jurídico fornecido.
- Se não houver contexto suficiente, diz claramente que não tens informação específica.
- Cita os artigos e diplomas legais sempre que possível.
- Usa linguagem clara e acessível ao cidadão comum.
- Nunca inventes leis ou artigos.
- Termina sempre com esta nota: "Nota: Esta é uma resposta informativa. Não substitui aconselhamento jurídico profissional. Consulta um advogado ou fontes oficiais."

Responde de forma estruturada: resposta direta → fundamentação legal → nota final."""

    def __init__(self):
        logger.info("Inicializando Dr. José...")
        config.validate()

        self.retriever = LegalRetriever()
        self.conversation_history: List[Dict[str, Any]] = []
        self.client = OpenAI(base_url=config.OPENROUTER_BASE_URL, api_key=config.OPENROUTER_API_KEY)

        if not self.retriever.is_ready():
            logger.warning("Base de conhecimento vazia. Executa python scripts/ingest.py")

    def get_response(self, user_input: str) -> str:
        context = self.retriever.get_context(user_input)

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if context and "nenhum artigo relevante" not in context.lower():
            messages.append({"role": "user", "content": f"Contexto:\n{context}\n\nPergunta: {user_input}"})
        else:
            messages.append({"role": "user", "content": f"Pergunta: {user_input}\nNão encontrei contexto específico na base de leis."})

        # Histórico limitado
        for turn in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})

        try:
            response = self.client.chat.completions.create(
                model=config.OPENROUTER_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            answer = response.choices[0].message.content.strip()

            self.conversation_history.append({"user": user_input, "assistant": answer, "timestamp": datetime.now().isoformat()})
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return answer

        except Exception as e:
            logger.error(f"Erro API: {e}")
            return f"Erro ao contactar o modelo: {str(e)}\nVerifica a chave API e a ligação à internet."

    def run(self):
        print("\n" + "="*70)
        print("⚖️  Dr. José - Assistente Jurídico Português")
        print("="*70)
        print("Comandos: /ajuda | /historico | /limpar | /sair\n")

        while True:
            try:
                user_input = input("Você: ").strip()
                if not user_input:
                    continue
                if user_input.lower() == '/sair':
                    print("Dr. José: Até breve!")
                    break
                if user_input.lower() == '/ajuda':
                    print("Pergunte sobre qualquer tema de direito português.")
                    continue
                if user_input.lower() == '/limpar':
                    self.conversation_history.clear()
                    print("Histórico limpo.")
                    continue
                if user_input.lower() == '/historico':
                    print(f"Histórico ({len(self.conversation_history)} interações)")
                    continue

                print("Dr. José: A pensar...")
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
