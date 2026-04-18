"""
Dr. José — Assistente Jurídico
================================
Classe principal que combina o RAG (base de conhecimento)
com o modelo de linguagem via OpenRouter para gerar
respostas jurídicas fundamentadas em lei portuguesa.

Pode ser usado:
  - Pela API (bot/api.py)
  - Diretamente na linha de comandos
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Configuração ──────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL   = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
RAG_TOP_K          = int(os.getenv("RAG_TOP_K", "5"))
CHROMA_DIR         = Path(os.getenv("CHROMA_DIR", "data/chroma_db"))

SYSTEM_PROMPT = """És o Dr. José, um assistente jurídico especializado exclusivamente em direito português.
O teu objetivo é ajudar cidadãos e profissionais a compreender a lei portuguesa de forma clara e acessível.

Conheces profundamente:
- A Constituição da República Portuguesa (CRP)
- O Código Penal Português (CP)
- O Código Civil
- O Código do Trabalho
- O Código de Processo Penal (CPP)
- O Código de Processo Civil (CPC)
- A Lei do Arrendamento Urbano (NRAU)
- E restante legislação portuguesa em vigor

Regras obrigatórias:
1. Responde SEMPRE em português de Portugal (nunca brasileiro)
2. Cita artigos específicos quando relevante (ex: "Art.º 203.º do CP")
3. Quando tens contexto de legislação fornecido, baseia a resposta nesse contexto
4. Explica de forma clara, evitando jargão excessivo desnecessário
5. Menciona prazos legais quando aplicável
6. Termina SEMPRE com: "⚠️ Esta informação é de caráter geral. Para o seu caso específico, consulte um advogado."
7. Para situações urgentes (detenção, acusação criminal), aconselha contactar imediatamente a Ordem dos Advogados: 213 241 300
8. Podes referenciar entidades: Ordem dos Advogados, DGAJ, Provedoria de Justiça, Ministério Público
9. Se a pergunta não for de âmbito jurídico, explica que só respondes a questões legais
10. Nunca inventes artigos ou leis — se não souberes, diz que não tens informação suficiente"""


class DrJose:
    """Assistente jurídico Dr. José."""

    def __init__(self):
        self._retriever = None
        self._cliente_llm = None
        self._inicializar()

    def _inicializar(self):
        """Inicializa o cliente LLM e tenta carregar o RAG."""
        # Cliente OpenRouter (compatível com API OpenAI)
        if OPENROUTER_API_KEY:
            self._cliente_llm = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
        else:
            print("⚠️  OPENROUTER_API_KEY não configurada. Respostas sem LLM.")

        # Tentar carregar RAG (pode não existir ainda)
        if CHROMA_DIR.exists():
            try:
                from rag.retriever import Retriever
                self._retriever = Retriever()
            except Exception as e:
                print(f"⚠️  RAG não disponível: {e}")
                print("   Execute primeiro: python scripts/ingest.py")
        else:
            print("⚠️  Base vetorial não encontrada. A funcionar sem RAG.")
            print("   Execute: python scripts/ingest.py")

    def base_disponivel(self) -> bool:
        """Verifica se a base de conhecimento RAG está disponível."""
        return self._retriever is not None

    def total_fragmentos(self) -> int:
        """Devolve o número de fragmentos indexados."""
        if self._retriever:
            return self._retriever.colecao.count()
        return 0

    def responder(self, pergunta: str, historico: list[dict] = None) -> dict:
        """
        Gera uma resposta jurídica para a pergunta.

        Args:
            pergunta:  Questão do utilizador.
            historico: Lista de mensagens anteriores [{role, content}, ...]

        Returns:
            {"resposta": str, "fontes": list[str]}
        """
        if historico is None:
            historico = []

        # 1. Pesquisar legislação relevante (RAG)
        contexto_legal = ""
        fontes = []

        if self._retriever:
            try:
                fragmentos = self._retriever.pesquisar(pergunta, k=RAG_TOP_K)
                fontes = list({f["fonte"] for f in fragmentos})

                if fragmentos:
                    linhas = ["## Legislação Relevante\n"]
                    for i, f in enumerate(fragmentos, 1):
                        linhas.append(f"### [{i}] {f['fonte']} (relevância: {f['score']:.0%})")
                        linhas.append(f["texto"])
                        linhas.append("")
                    contexto_legal = "\n".join(linhas)
            except Exception as e:
                print(f"Aviso: Erro no RAG: {e}")

        # 2. Construir prompt com contexto legal
        if contexto_legal:
            pergunta_aumentada = (
                f"{contexto_legal}\n"
                f"---\n"
                f"Com base na legislação acima, responde à seguinte questão:\n\n"
                f"{pergunta}"
            )
        else:
            pergunta_aumentada = (
                f"Responde à seguinte questão jurídica com base no teu conhecimento "
                f"do direito português:\n\n{pergunta}\n\n"
                f"(Nota: a base de conhecimento local não está disponível neste momento)"
            )

        # 3. Construir mensagens para o LLM
        mensagens = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Adicionar histórico (sem o contexto RAG, apenas perguntas/respostas limpas)
        for msg in historico[-10:]:  # Últimas 5 trocas
            mensagens.append(msg)

        mensagens.append({"role": "user", "content": pergunta_aumentada})

        # 4. Chamar o LLM
        if not self._cliente_llm:
            return {
                "resposta": "⚠️ O serviço de IA não está configurado. Adicione a OPENROUTER_API_KEY no ficheiro .env",
                "fontes": [],
            }

        try:
            completion = self._cliente_llm.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=mensagens,
                max_tokens=1500,
                temperature=0.3,  # Baixo para mais precisão jurídica
            )
            resposta = completion.choices[0].message.content
        except Exception as e:
            resposta = f"Erro ao gerar resposta: {str(e)}"

        return {
            "resposta": resposta,
            "fontes": fontes,
        }


# ── Interface de linha de comandos ────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  ⚖️  Dr. José — Assistente Jurídico Português")
    print("=" * 60)
    print("  Escreva a sua questão jurídica.")
    print("  Comandos: 'sair' para terminar, 'limpar' para nova conversa")
    print("=" * 60 + "\n")

    jose = DrJose()
    historico = []

    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAté logo!")
            break

        if not pergunta:
            continue

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Até logo!")
            break

        if pergunta.lower() == "limpar":
            historico = []
            print("(Conversa reiniciada)\n")
            continue

        print("\nDr. José: A consultar legislação...\n")

        resultado = jose.responder(pergunta, historico)

        print(f"Dr. José: {resultado['resposta']}")

        if resultado["fontes"]:
            print(f"\n📚 Fontes consultadas: {', '.join(resultado['fontes'])}")

        print()

        historico.append({"role": "user", "content": pergunta})
        historico.append({"role": "assistant", "content": resultado["resposta"]})


if __name__ == "__main__":
    main()
