# ⚖️ Dr. José — Assistente Jurídico Português

Bot de IA especializado em direito português, com base de conhecimento sobre:
- Constituição da República Portuguesa (CRP)
- Código Penal Português (CP)
- Código Civil
- Código do Trabalho
- Código de Processo Penal
- E outros diplomas legais

## Estrutura do Projeto

```
dr-jose/
├── data/leis/          # Ficheiros de texto das leis (.txt ou .pdf)
├── scripts/
│   └── ingest.py       # Indexa os documentos legais na base vetorial
├── rag/
│   └── retriever.py    # Motor de pesquisa semântica (RAG)
├── bot/
│   └── jose.py         # Chatbot Dr. José (interface de linha de comandos)
├── docs/               # Documentação técnica
├── .env.example        # Variáveis de ambiente (copiar para .env)
├── requirements.txt    # Dependências Python
└── README.md
```

## Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_UTILIZADOR/dr-jose.git
cd dr-jose
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
copy .env.example .env
# Editar .env e preencher a OPENROUTER_API_KEY
```

### 5. Adicionar documentos legais
Colocar ficheiros `.txt` com o texto das leis na pasta `data/leis/`.
Ver `docs/fontes_legais.md` para saber onde obter os textos oficiais.

### 6. Indexar os documentos
```bash
python scripts/ingest.py
```

### 7. Iniciar o Dr. José
```bash
python bot/jose.py
```

## Fontes Legais Oficiais

- [Diário da República Eletrónico](https://dre.pt)
- [Procuradoria-Geral Distrital de Lisboa](http://www.pgdlisboa.pt/leis/lei_main.php)
- [Autoridade Tributária e Aduaneira](https://info.portaldasfinancas.gov.pt)

## Aviso Legal

Este sistema fornece informação jurídica de caráter geral e educativo.
**Não substitui** aconselhamento jurídico profissional.
Para situações específicas, consulte um advogado licenciado pela [Ordem dos Advogados](https://www.oa.pt).

---
Desenvolvido com Python · ChromaDB · OpenRouter API
