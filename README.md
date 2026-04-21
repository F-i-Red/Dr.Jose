# ⚖️ Dr. José — Assistente Jurídico Português

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

Bot de IA especializado em direito português, com motor de busca semântica (RAG), interface web moderna (Streamlit) e suporte a múltiplos modelos LLM via OpenRouter.

## ✨ Funcionalidades

- 🌐 **Interface Web moderna** com Streamlit (acessível no browser)
- 💬 **Interface de linha de comando** (CLI) para utilizadores avançados
- 🔍 **Busca semântica** em legislação portuguesa via ChromaDB
- 🧠 **Chunking inteligente** que respeita artigos e secções
- 🔄 **Fallback automático** entre vários modelos gratuitos do OpenRouter
- 📊 **Logging estruturado** para debug e monitorização
- 🔒 **Sanitização de input** contra prompt injection

## 📋 Legislação Suportada

| Diploma | Fonte |
| :--- | :--- |
| Constituição da República Portuguesa | Ficheiros `.txt` em `data/leis/` |
| Código Civil | Ficheiros `.txt` em `data/leis/` |
| Código Penal | Ficheiros `.txt` em `data/leis/` |
| Código do Trabalho | Ficheiros `.txt` em `data/leis/` |
| Código de Processo Penal | Ficheiros `.txt` em `data/leis/` |

> As leis devem ser colocadas manualmente na pasta `data/leis/` como ficheiros `.txt` (UTF-8).

## 🚀 Instalação Rápida

### 1. Clonar o repositório

```bash
git clone https://github.com/F-i-Red/Dr.Jose.git
cd Dr.Jose
2. Criar ambiente virtual
bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
3. Instalar dependências
bash
pip install -r requirements.txt
4. Configurar API Key
Copia o ficheiro de exemplo e adiciona a tua chave da OpenRouter:

bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS
Edita o .env e adiciona:

ini
OPENROUTER_API_KEY=sk-or-v1-tua-chave-aqui
OPENROUTER_MODEL=openrouter/free   # Router automático (recomendado)
Obtém a tua chave gratuita em OpenRouter Keys

5. Preparar a base de conhecimento
Coloca os ficheiros .txt das leis na pasta data/leis/ (criada automaticamente).

Podes usar o script auxiliar para criar ficheiros de exemplo:

bash
python scripts/fetch_laws.py
6. Indexar a legislação
bash
python scripts/ingest.py
Este comando:

✅ Lê todos os ficheiros .txt em data/leis/

✅ Processa e divide os documentos em chunks

✅ Cria a base vetorial ChromaDB em data/chroma/

7. Iniciar o Dr. José
Interface Web (recomendada):

bash
streamlit run app.py
O browser abrirá automaticamente em http://localhost:8501

Interface de Linha de Comando (alternativa):

bash
python -m bot.jose
Windows (atalho):

batch
iniciar.bat
🎮 Comandos do Chat (apenas no modo CLI)
Comando	Função
/ajuda	Mostrar ajuda
/historico	Ver histórico da conversa
/limpar	Limpar histórico
/sair	Sair do programa
No modo Streamlit, a interface é gráfica e não necessita de comandos especiais.

📁 Estrutura do Projeto
text
dr-jose/
├── app.py                  # Interface web (Streamlit)
├── bot/
│   ├── __init__.py
│   └── jose.py             # Chatbot principal (CLI)
├── config.py               # Configuração centralizada
├── data/
│   ├── leis/               # Ficheiros das leis (.txt)
│   └── chroma/             # Base vetorial ChromaDB
├── docs/                   # Documentação adicional
├── rag/
│   └── retriever.py        # Motor de busca semântica
├── scripts/
│   ├── ingest.py           # Indexação de documentos
│   └── fetch_laws.py       # Utilitário para gestão de leis
├── utils/
│   └── logger.py           # Configuração de logs
├── logs/                   # Ficheiros de log (criados automaticamente)
├── .env.example            # Exemplo de configuração
├── .gitignore
├── iniciar.bat             # Inicializador para Windows
├── requirements.txt        # Dependências Python
└── README.md
🔧 Configuração Avançada
No ficheiro .env podes ajustar:

ini
# Modelo a utilizar (fallback automático no jose.py)
OPENROUTER_MODEL=openrouter/free

# Opções alternativas (descomenta uma):
# OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
# OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
🛠️ Resolução de Problemas
"OPENROUTER_API_KEY não definida"
Verifica se o ficheiro .env existe na raiz do projeto

Confirma que a chave começa por sk-or-v1-

"Nenhum documento encontrado" / Base vazia
Executa python scripts/fetch_laws.py para criar ficheiros de exemplo

Ou adiciona os teus próprios ficheiros .txt em data/leis/

Depois executa python scripts/ingest.py

Erro 404 / "No endpoints found"
Os modelos gratuitos do OpenRouter mudam frequentemente

Usa openrouter/free (router automático) ou atualiza o modelo no .env

Aguarda alguns minutos se estiver em rate limit

Erro ao instalar dependências
bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
⚠️ Aviso Legal
Este sistema fornece informação jurídica de caráter geral e educativo.

Não substitui aconselhamento jurídico profissional.

Para situações específicas, consulte um advogado licenciado pela Ordem dos Advogados.

📄 Licença
MIT License - ver LICENSE

🙏 Agradecimentos
OpenRouter - API de modelos LLM

ChromaDB - Base vetorial

Streamlit - Interface web

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
