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
    SYSTEM_PROMPT = """Tu és o Dr. José, um advogado português especializado em direito português.

REGRAS:
- Responde de forma clara, direta e profissional.
- Baseia-te APENAS no contexto jurídico fornecido.
- Se não tiveres informação suficiente, diz: "Não encontrei informação específica sobre este tema."
- Cita sempre os artigos legais relevantes (ex.: Artigo 368.º do Código Penal).
- Termina sempre com: "Nota: Esta é uma resposta informativa. Não substitui aconselhamento jurídico profissional."
- NÃO faças raciocínio em voz alta. Vai direto à resposta.
- Responde em português de Portugal.

Estrutura recomendada (mas não obrigatória):
1. Resposta direta
2. Fundamentação legal
3. Nota final"""

    def __init__(self):
        logger.info("Inicializando Dr. José...")
        config.validate()
        self.retriever = LegalRetriever()
        self.conversation_history: List[Dict[str, Any]] = []
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
        )

    def get_response(self, user_input: str) -> str:
        context = self.retriever.get_context(user_input)

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if context and len(context.strip()) > 50:
            messages.append({
                "role": "user",
                "content": f"Contexto jurídico:\n{context}\n\nPergunta do utilizador: {user_input}"
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Pergunta: {user_input}"
            })

        # Histórico (últimas 3 interações)
        for turn in self.conversation_history[-3:]:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})

        # Modelos com fallback
        models_to_try = [
            "openrouter/free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
        ]

        for model in models_to_try:
            logger.info(f"Tentando modelo: {model}")
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024,   # ← VALOR CORRIGIDO (era 350-500)
                    timeout=45
                )
                answer = response.choices[0].message.content.strip()
                
                # Guardar no histórico
                self.conversation_history.append({
                    "user": user_input,
                    "assistant": answer,
                    "timestamp": datetime.now().isoformat()
                })
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
                
                return answer
            except Exception as e:
                logger.warning(f"Modelo {model} falhou: {str(e)[:80]}")
                continue

        return """❌ Não foi possível obter resposta neste momento.

Os modelos gratuitos podem estar temporariamente sobrecarregados.
Aguarda 1-2 minutos e tenta novamente."""

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
                if user_input.lower() in ['/sair', 'sair', 'exit']:
                    print("Dr. José: Até breve!")
                    break
                if user_input.lower() == '/ajuda':
                    print("Pergunta sobre qualquer tema de direito português.")
                    print("Exemplos: direitos do arrendatário, penas do Código Penal, etc.")
                    continue

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
