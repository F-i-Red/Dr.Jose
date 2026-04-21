# bot/jose.py
import os
import requests
from dotenv import load_dotenv

from rag.retriever import LegalRetriever
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY não encontrada. Preenche o ficheiro .env.")

# Lista de modelos com fallback automático
MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-7b-instruct:free",
]

SYSTEM_PROMPT = """
És o Dr. José, um assistente jurídico português especializado em direito português.

Regras:
- Responde sempre em português europeu (não brasileiro)
- Especialista em direito português: Constituição, Código Penal, Código Civil, Código do Trabalho, etc.
- Usa linguagem clara e acessível ao cidadão comum
- Cita sempre os artigos concretos quando possível (ex: "nos termos do Art. 25.º da CRP...")
- Nunca inventes leis ou artigos — usa apenas o contexto fornecido
- Se não souberes, diz claramente: "Não tenho informação suficiente sobre este tema."
- Estrutura a resposta: 1) Enquadramento legal, 2) O que podes fazer, 3) Passos práticos
- Termina sempre com: "⚠️ Esta resposta é informativa e não substitui consulta jurídica profissional."
""".strip()


class DrJoseBot:
    def __init__(self):
        logger.info("Inicializando Dr. José...")
        self.retriever = LegalRetriever()
        self.conversation_history = []

    def _call_llm(self, messages: list) -> str:
        """Chama o LLM via OpenRouter com fallback entre modelos."""
        last_error = None

        for model in MODELS:
            try:
                logger.info(f"Tentando modelo: {model}")

                response = requests.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/F-i-Red/Dr.Jose",
                        "X-Title": "Dr. José - Assistente Jurídico Português",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 1500,
                    },
                    timeout=45,
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"Sucesso com modelo: {model}")
                    return answer
                else:
                    logger.warning(f"Modelo falhou ({model}): {response.status_code} - {response.text[:200]}")
                    last_error = response.text

            except Exception as e:
                logger.warning(f"Erro no modelo ({model}): {e}")
                last_error = str(e)

        logger.error("Todos os modelos falharam")
        return f"❌ Erro: Nenhum modelo disponível de momento.\nÚltimo erro: {last_error}"

    def get_response(self, question: str) -> str:
        """Obtém resposta do Dr. José para uma pergunta jurídica."""
        # Pesquisa contexto legal relevante no RAG
        context = self.retriever.get_context(question)

        if context:
            user_message = f"""Contexto legal relevante (extraído da legislação portuguesa):
---
{context}
---

Pergunta do cidadão: {question}

Com base no contexto legal acima, responde à pergunta de forma clara e prática."""
        else:
            user_message = f"""Pergunta do cidadão: {question}

Nota: Não encontrei artigos específicos na base de dados local para esta pergunta.
Responde com base no teu conhecimento geral do direito português, mas indica claramente
que o cidadão deve verificar a legislação atualizada."""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        return self._call_llm(messages)


# Execução direta (modo CLI)
if __name__ == "__main__":
    bot = DrJoseBot()

    print("\n" + "=" * 70)
    print("⚖️  Dr. José - Assistente Jurídico Português")
    print("=" * 70)
    print("Comandos: /sair para terminar\n")

    while True:
        user_input = input("Você: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["/sair", "sair", "exit", "quit"]:
            print("Dr. José: Até breve. Boas consultas! ⚖️")
            break

        print("Dr. José: A consultar a legislação...")
        resposta = bot.get_response(user_input)
        print(f"\nDr. José:\n{resposta}\n")
        print("-" * 70)
