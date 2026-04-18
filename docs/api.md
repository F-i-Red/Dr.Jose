# API do Dr. José — Documentação Técnica

## Visão Geral

A API REST do Dr. José expõe o assistente jurídico como serviço web,
permitindo integração com qualquer interface (web, mobile, quiosques, etc.).

**URL base:** `http://localhost:8000`  
**Documentação interativa:** `http://localhost:8000/docs`

---

## Endpoints

### `POST /chat` — Fazer uma pergunta

**Body (JSON):**
```json
{
  "pergunta": "O que é um crime de furto em Portugal?",
  "session_id": null
}
```

- `session_id`: opcional. Se omitido, cria nova sessão. Reutilizar para manter contexto da conversa.

**Resposta:**
```json
{
  "resposta": "De acordo com o Art.º 203.º do Código Penal...",
  "session_id": "abc-123-def",
  "fontes": ["codigo_penal", "constituicao"],
  "timestamp": "2025-04-18T10:00:00"
}
```

---

### `GET /health` — Estado do servidor

```json
{
  "status": "operacional",
  "versao": "1.0.0",
  "base_carregada": true,
  "timestamp": "2025-04-18T10:00:00"
}
```

---

### `GET /stats` — Estatísticas

```json
{
  "total_fragmentos": 8432,
  "colecao": "legislacao_portuguesa",
  "modelo_llm": "anthropic/claude-3.5-sonnet",
  "sessoes_ativas": 12
}
```

---

### `DELETE /chat/{session_id}` — Limpar sessão

Elimina o histórico de conversa de uma sessão.

---

## Testar com curl (Windows PowerShell)

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET

# Fazer pergunta
$body = '{"pergunta": "O que e um crime de furto?", "session_id": null}'
Invoke-WebRequest -Uri "http://localhost:8000/chat" -Method POST `
  -ContentType "application/json" -Body $body
```

---

## Arranque do servidor

```bash
# Instalar dependências (primeira vez)
pip install -r requirements.txt

# Iniciar servidor
python -m uvicorn bot.api:app --reload --host 0.0.0.0 --port 8000

# Ou usar o script Windows:
iniciar.bat
```

---

## Arquitectura

```
Utilizador
    │
    ▼
[Interface Web / App]
    │  HTTP POST /chat
    ▼
[API FastAPI — bot/api.py]
    │
    ├──► [RAG — rag/retriever.py]
    │         │
    │         ▼
    │    [ChromaDB — data/chroma_db/]
    │    (fragmentos de lei indexados)
    │
    └──► [LLM — OpenRouter API]
              │
              ▼
         [Resposta jurídica fundamentada]
```
