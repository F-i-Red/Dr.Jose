# Interface Web — Como Usar

## Abrir localmente

A interface está em `interface/index.html`.

**Opção 1 — diretamente no browser (mais simples):**
```
Abrir o ficheiro interface/index.html no Chrome ou Edge
```

> Nota: Para que a interface comunique com a API local,
> o browser tem de ter CORS permissivo. Recomenda-se a Opção 2.

**Opção 2 — servir com Python (recomendado):**
```bash
# Na raiz do projeto
python -m http.server 3000

# Abrir no browser:
# http://localhost:3000/interface/index.html
```

**Opção 3 — com a API a correr (produção):**
```bash
# Terminal 1 — API
python -m uvicorn bot.api:app --port 8000

# Terminal 2 — Interface
python -m http.server 3000
```

---

## Configurar URL da API

Se a API correr noutra porta ou servidor, editar a linha no `index.html`:

```javascript
const API_URL = 'http://localhost:8000';  // ← alterar aqui
```

---

## Funcionalidades da Interface

- **Sidebar** com sugestões de perguntas por categoria
- **Indicador de estado** da API (verde = online, vermelho = offline)
- **Histórico de sessão** — mantém contexto ao longo da conversa
- **Fontes citadas** — mostra quais diplomas legais foram consultados
- **Aviso legal** — destaca automaticamente o aviso no final de cada resposta
- **Nova conversa** — reinicia a sessão
- **Responsivo** — funciona em mobile (sidebar oculta em ecrãs pequenos)
