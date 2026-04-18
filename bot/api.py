"""
Dr. José — API Backend
======================
Servidor FastAPI que expõe o Dr. José como serviço web.

Endpoints:
    POST /chat          — envia uma pergunta e recebe resposta jurídica
    GET  /health        — verifica se o servidor está operacional
    GET  /stats         — estatísticas da base de conhecimento
    DELETE /chat/{id}   — limpa histórico de uma sessão

Utilização:
    uvicorn bot.api:app --reload --host 0.0.0.0 --port 8000
"""

import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from bot.jose import DrJose

load_dotenv()

# ── Aplicação FastAPI ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Dr. José — API Jurídica Portuguesa",
    description="Assistente jurídico inteligente baseado em legislação portuguesa.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir ao domínio da interface
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Instância do Dr. José e memória de sessões ────────────────────────────────

dr_jose = DrJose()
sessoes: dict[str, list[dict]] = {}  # session_id -> histórico de mensagens

# ── Modelos de dados (Pydantic) ───────────────────────────────────────────────

class PerguntaRequest(BaseModel):
    pergunta: str
    session_id: Optional[str] = None  # se None, cria nova sessão

    model_config = {
        "json_schema_extra": {
            "example": {
                "pergunta": "O que é um crime de furto em Portugal?",
                "session_id": None
            }
        }
    }


class RespostaResponse(BaseModel):
    resposta: str
    session_id: str
    fontes: list[str]
    timestamp: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "resposta": "De acordo com o Art.º 203.º do Código Penal...",
                "session_id": "abc-123",
                "fontes": ["codigo_penal"],
                "timestamp": "2025-04-18T10:00:00"
            }
        }
    }


class HealthResponse(BaseModel):
    status: str
    versao: str
    base_carregada: bool
    timestamp: str


class StatsResponse(BaseModel):
    total_fragmentos: int
    colecao: str
    modelo_llm: str
    sessoes_ativas: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verifica se o servidor está operacional."""
    return HealthResponse(
        status="operacional",
        versao="1.0.0",
        base_carregada=dr_jose.base_disponivel(),
        timestamp=datetime.now().isoformat(),
    )


@app.get("/stats", response_model=StatsResponse, tags=["Sistema"])
async def estatisticas():
    """Devolve estatísticas sobre a base de conhecimento."""
    return StatsResponse(
        total_fragmentos=dr_jose.total_fragmentos(),
        colecao=os.getenv("CHROMA_COLLECTION", "legislacao_portuguesa"),
        modelo_llm=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        sessoes_ativas=len(sessoes),
    )


@app.post("/chat", response_model=RespostaResponse, tags=["Chat"])
async def chat(body: PerguntaRequest):
    """
    Envia uma pergunta ao Dr. José e recebe uma resposta jurídica fundamentada.

    - Se `session_id` for nulo, cria uma nova sessão.
    - Sessões mantêm o histórico da conversa para contexto.
    """
    if not body.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    if len(body.pergunta) > 2000:
        raise HTTPException(status_code=400, detail="Pergunta demasiado longa (máx. 2000 caracteres).")

    # Gerir sessão
    session_id = body.session_id or str(uuid.uuid4())
    if session_id not in sessoes:
        sessoes[session_id] = []

    historico = sessoes[session_id]

    try:
        resultado = dr_jose.responder(
            pergunta=body.pergunta,
            historico=historico,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a pergunta: {str(e)}")

    # Guardar mensagens no histórico da sessão
    sessoes[session_id].append({"role": "user", "content": body.pergunta})
    sessoes[session_id].append({"role": "assistant", "content": resultado["resposta"]})

    # Limitar histórico a 20 mensagens (10 turnos) para não exceder contexto
    if len(sessoes[session_id]) > 20:
        sessoes[session_id] = sessoes[session_id][-20:]

    return RespostaResponse(
        resposta=resultado["resposta"],
        session_id=session_id,
        fontes=resultado["fontes"],
        timestamp=datetime.now().isoformat(),
    )


@app.delete("/chat/{session_id}", tags=["Chat"])
async def limpar_sessao(session_id: str):
    """Limpa o histórico de uma sessão de conversa."""
    if session_id in sessoes:
        del sessoes[session_id]
        return {"mensagem": f"Sessão {session_id} eliminada com sucesso."}
    raise HTTPException(status_code=404, detail="Sessão não encontrada.")


# ── Arranque direto ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.api:app", host="0.0.0.0", port=8000, reload=True)
