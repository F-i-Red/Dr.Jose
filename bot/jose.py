# bot/jose.py
import os
import requests
from dotenv import load_dotenv

from rag.retriever import LegalRetriever
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY não encontrada. Preenche o ficheiro .env.")

# ── Modelos gratuitos disponíveis no OpenRouter (atualizado abril 2026) ───────
# Os modelos :free têm rate limits — o fallback percorre a lista automaticamente
MODELS = [
    "deepseek/deepseek-chat-v3-0324:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-4-scout:free",
    "meta-llama/llama-4-maverick:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "google/gemini-2.0-flash-exp:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "microsoft/phi-4-reasoning:free",
    "qwen/qwen3-30b-a3b:free",
]

SYSTEM_PROMPT = """
És o Dr. José, um assistente jurídico português especializado em direito português.

Regras absolutas:
- Responde SEMPRE em português europeu (Portugal), nunca em português do Brasil
- Especialista em: Constituição da República Portuguesa, Código Penal, Código Civil, Código do Trabalho, Código de Processo Penal, NRAU (arrendamento), e demais legislação portuguesa
- Usa linguagem clara e acessível ao cidadão comum, sem jargão desnecessário
- Cita SEMPRE os artigos concretos quando disponíveis (ex: "nos termos do Art. 53.º do Código do Trabalho...")
- NUNCA inventes leis, artigos ou jurisprudência — usa apenas o que está no contexto fornecido
- Se não tiveres informação suficiente, diz claramente: "Não tenho dados suficientes sobre este tema específico. Recomendo consultar um advogado."
- Estrutura as respostas em 3 partes: 1) Enquadramento legal, 2) O que podes fazer, 3) Passos práticos
- Termina SEMPRE com: "⚠️ Esta resposta é informativa e não substitui consulta jurídica profissional com um advogado."
""".strip()


class DrJoseBot:
    def __init__(self):
        logger.info("Inicializando Dr. José...")
        self.retriever = LegalRetriever()

    def _call_llm(self, messages: list) -> str:
        """Chama o LLM via OpenRouter com fallback automático entre modelos."""
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
                        "max_tokens": 2000,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    logger.info(f"✅ Sucesso com modelo: {model}")
                    return answer
                else:
                    logger.warning(f"Modelo {model} falhou: {response.status_code} — {response.text[:150]}")
                    last_error = response.text

            except Exception as e:
                logger.warning(f"Erro no modelo {model}: {e}")
                last_error = str(e)

        logger.error("Todos os modelos falharam")
        return (
            "❌ Não foi possível obter resposta de nenhum modelo de momento.\n\n"
            "Possíveis causas:\n"
            "• Os modelos gratuitos atingiram o rate limit — aguarda 1 minuto e tenta novamente\n"
            "• Verifica a tua chave OpenRouter no ficheiro .env\n\n"
            f"Último erro: {last_error}"
        )

    def get_response(self, question: str) -> str:
        """Obtém resposta do Dr. José para uma pergunta jurídica."""
        context = self.retriever.get_context(question)

        if context:
            user_message = f"""Contexto legal relevante (extraído de legislação portuguesa oficial):
---
{context}
---

Pergunta do cidadão: {question}

Com base no contexto legal acima, responde à pergunta de forma clara, prática e estruturada."""
        else:
            user_message = f"""Pergunta do cidadão: {question}

Nota: Não encontrei artigos específicos na base de dados local para esta pergunta.
Responde com base no teu conhecimento geral do direito português, indicando claramente
que o cidadão deve verificar a legislação actualizada ou consultar um advogado."""

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
    print("Escreve a tua pergunta. Usa /sair para terminar.\n")

    while True:
        user_input = input("Você: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["/sair", "sair", "exit", "quit"]:
            print("Dr. José: Até breve. ⚖️")
            break
        print("Dr. José: A consultar a legislação...")
        print(f"\nDr. José:\n{bot.get_response(user_input)}\n")
        print("-" * 70)
