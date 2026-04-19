# ⚖️ Dr. José — Assistente Jurídico Português

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Bot de IA especializado em direito português, com motor de busca semântica (RAG) e download automático de legislação.

## ✨ Funcionalidades

- 🔍 **Busca semântica** em legislação portuguesa
- 📚 **Download automático** das leis do Diário da República
- 🧠 **Chunking inteligente** que respeita artigos e secções
- 💬 **Interface conversacional** com contexto jurídico
- 📊 **Logging estruturado** para debug e monitorização
- 🔒 **Sanitização de input** contra prompt injection

## 📋 Legislação Suportada

| Diploma | Fonte |
|---------|-------|
| Constituição da República Portuguesa | DRE |
| Código Civil | DRE |
| Código Penal | DRE |
| Código do Trabalho | DRE |
| Código de Processo Penal | DRE |

> As leis são obtidas automaticamente do [Diário da República Eletrónico](https://dre.pt)

## 🚀 Instalação Rápida

### 1. Clonar o repositório

```bash
git clone https://github.com/F-i-Red/Dr.Jose.git
cd Dr.Jose
```
### 2. Criar ambiente virtual
```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
### 3. Instalar dependências
```
pip install -r requirements.txt
```
### 4. Configurar API Key
Copia o ficheiro de exemplo e adiciona a tua chave da OpenRouter:

```
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS
```
Edita o .env e adiciona:
```
OPENROUTER_API_KEY=sk-or-v1-tua-chave-aqui
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

### 5. Indexar a legislação
```
python scripts/ingest.py
```
Este comando:

✅ Busca as leis mais recentes online (se disponível)

✅ Processa e divide os documentos em chunks inteligentes

✅ Cria a base vetorial para busca semântica

### 6. No terminal:
```
pip install streamlit
streamlit run app.py
```

### 7. Iniciar o Dr. José
```
python bot/jose.py
```
Ou no Windows:
```
iniciar.bat
```
## 🎮 Comandos do Chat

| Comando |	Função |
|---|---|
| /ajuda |	Mostrar ajuda |
| /contexto	| Ver contexto jurídico da última pergunta |
| /historico |	Ver histórico da conversa |
| /limpar	| Limpar histórico |
| /sair	| Sair do programa |

## 📁 Estrutura do Projeto

dr-jose/

├── bot/

│    └── jose.py           # Chatbot principal

├── data/

│    ├── leis/             # Ficheiros das leis (.txt)

│    └── chroma_db/        # Base vetorial (criada automaticamente)

├── docs/                 # Documentação adicional

├── rag/

│    └── retriever.py      # Motor de busca semântica

├── scripts/

│    ├── ingest.py         # Indexação de documentos

│    └── fetch_laws.py     # Download automático de leis

├── utils/

│    ├── __init__.py

│    └── logger.py         # Configuração de logs

├── logs/                 # Ficheiros de log (criados automaticamente)

├── .env.example          # Exemplo de configuração

├── .gitignore

├── iniciar.bat           # Inicializador para Windows

├── requirements.txt      # Dependências Python

├── config.py             # Configuração centralizada

└── README.md

## 🔧 Configuração Avançada
No ficheiro .env podes ajustar:

```
# Processamento de documentos
CHUNK_SIZE=1500          # Tamanho de cada chunk
CHUNK_OVERLAP=200        # Sobreposição entre chunks

# Busca
TOP_K_RESULTS=5          # Número de resultados por busca
SIMILARITY_THRESHOLD=0.6 # Mínimo de similaridade (0-1)
```
⚠️ Aviso Legal
Este sistema fornece informação jurídica de caráter geral e educativo.

## 🛠️ Resolução de Problemas
"OPENROUTER_API_KEY não definida"
Verifica se o ficheiro .env existe na raiz do projeto

Confirma que a chave está correta (começa por sk-or-v1-)

"Nenhum documento encontrado"
Executa python scripts/fetch_laws.py para download manual

Ou adiciona ficheiros .txt ou .pdf em data/leis/

Erro ao instalar dependências
```
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

📄 Licença
MIT License - ver LICENSE

### 🙏 Agradecimentos
OpenRouter - API de modelos LLM

ChromaDB - Base vetorial

LangChain - Framework RAG

Desenvolvido com ❤️ para acesso à justiça em Portugal


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
