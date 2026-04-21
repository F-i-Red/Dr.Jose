import os
import requests
from dotenv import load_dotenv

from rag.retriever import LegalRetriever
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
)

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY não encontrada. Preenche o ficheiro .env."
    )

# 🔁 Lista de modelos (fallback automático)
MODELS = [
    "openai/gpt-3.5-turbo",
    "anthropic/claude-3-haiku",
    "meta-llama/llama-3.3-70b-instruct:free",
]

SYSTEM_PROMPT = """
És o Dr. José, um assistente jurídico português.

Regras:
- Especialista em direito português
- Usa linguagem clara
- Cita artigos quando possível
- Nunca inventes leis
- Se não souberes, diz claramente
- Termina com: "Esta resposta é informativa e não substitui consulta jurídica profissional."
""".strip()


class DrJoseBot:
    def __init__(self):
        logger.info("Inicializando Dr. José...")
        self.retriever = LegalRetriever()

    def _call_llm(self, messages):
        last_error = None

        for model in MODELS:
            try:
                logger.info(f"Tentando modelo: {model}")

                response = requests.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 1000,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()

                    logger.info(f"Sucesso com modelo: {model}")
                    return answer

                else:
                    logger.warning(
                        f"Modelo falhou ({model}): {response.status_code} - {response.text}"
                    )
                    last_error = response.text

            except Exception as e:
                logger.warning(f"Erro no modelo ({model}): {e}")
                last_error = str(e)

        logger.error("Todos os modelos falharam")
        return f"Erro: Nenhum modelo disponível.\nÚltimo erro: {last_error}"

    def get_response(self, question: str) -> str:
        logger.info("A processar pergunta do utilizador...")

        context = self.retriever.get_context(question)
        context = "\n\n".join(context_chunks)

        if not context.strip():
            context = "Nenhum artigo relevante encontrado."

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Contexto legal:\n{context}\n\nPergunta:\n{question}",
            },
        ]

        answer = self._call_llm(messages)
        return answer


# Execução direta (modo CLI)
if __name__ == "__main__":
    bot = DrJoseBot()

    print("\n" + "=" * 70)
    print("⚖️  Dr. José - Assistente Jurídico Português")
    print("=" * 70)
    print("Comandos: /ajuda | /historico | /limpar | /sair\n")

    while True:
        user_input = input("Você: ")

        if user_input.lower() in ["/sair", "sair"]:
            print("Dr. José: Até breve.")
            break

        print("Dr. José: A pensar...")

        resposta = bot.get_response(user_input)
        print(f"\nDr. José: {resposta}\n")
