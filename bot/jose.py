import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

from rag.retriever import LegalRetriever

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY não encontrada. Preenche o ficheiro .env com a tua API key."
    )


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "anthropic/claude-3.5-sonnet"  # ajusta se quiseres outro


SYSTEM_PROMPT = """
És o Dr. José, um assistente jurídico português.

Regras fundamentais:
- Especialista em direito português (Constituição, Código Penal, Código Civil, Código do Trabalho, etc.).
- Usa sempre linguagem clara e acessível ao cidadão comum.
- Sempre que possível, cita artigos concretos (ex.: "artigo 32.º da CRP").
- NUNCA inventes artigos, números ou leis. Se não tiveres contexto suficiente, diz claramente que não podes garantir exatidão.
- Se o contexto não contiver artigos relevantes, responde de forma geral e sugere consulta a um advogado ou à Ordem dos Advogados.
- Não dês conselhos ilegais ou que incentivem a violação da lei.
- Termina sempre com um pequeno aviso: "Esta resposta é informativa e não substitui consulta jurídica profissional."
""".strip()


class DrJose:
    def __init__(self) -> None:
        self.retriever = LegalRetriever()

    def _build_context(self, question: str) -> str:
        excertos: List[str] = self.retriever.query(question, k=5)

        # Se só vier o fallback, não fingimos que há contexto
        if (
            len(excertos) == 1
            and "Nenhum artigo relevante foi encontrado" in excertos[0]
        ):
            return ""

        joined = "\n\n".join(f"- {e}" for e in excertos)
        return f"Excerto(s) de legislação potencialmente relevante:\n\n{joined}"

    def answer(self, question: str, session_id: Optional[str] = None) -> dict:
        context = self._build_context(question)

        if not context:
            user_prompt = f"""
Pergunta do utilizador:
{question}

Não foi encontrado nenhum artigo específico na base de conhecimento para esta questão.
Responde de forma geral, com base em princípios jurídicos portugueses, e recomenda consulta profissional.
""".strip()
        else:
            user_prompt = f"""
Pergunta do utilizador:
{question}

Contexto jurídico encontrado (excerto de legislação portuguesa):
{context}

Usa APENAS este contexto para fundamentar a resposta. Se o contexto não for suficiente, diz isso explicitamente.
""".strip()

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        return {
            "answer": content,
            "context_used": bool(context),
        }


# Interface simples para outros módulos (ex.: API)
dr_jose = DrJose()
