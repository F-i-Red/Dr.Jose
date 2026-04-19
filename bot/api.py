import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from bot.jose import dr_jose

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY não encontrada. Preenche o ficheiro .env com a tua API key."
    )

app = FastAPI(
    title="Dr. José - Assistente Jurídico Português",
    description="API do Dr. José, um assistente jurídico baseado em RAG e LLM.",
    version="1.0.0",
)

# CORS para permitir que a interface web chame a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restringir ao domínio oficial
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    pergunta: str
    sessao_id: Optional[str] = None


class ChatResponse(BaseModel):
    resposta: str
    contexto_utilizado: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    pergunta = (req.pergunta or "").strip()
    if not pergunta:
        raise HTTPException(status_code=400, detail="Pergunta vazia.")

    try:
        result = dr_jose.answer(pergunta, session_id=req.sessao_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        resposta=result["answer"],
        contexto_utilizado=result["context_used"],
    )


@app.get("/stats")
def stats():
    # Placeholder — aqui poderias expor nº de pedidos, etc.
    return {"versao": "1.0.0", "nome": "Dr. José"}
