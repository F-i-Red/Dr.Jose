"""
Dr. José — Script de Ingestão de Documentos Legais
====================================================
Este script lê todos os ficheiros de lei em data/leis/,
divide-os em fragmentos e indexa-os na base vetorial ChromaDB.

Utilização:
    python scripts/ingest.py

Formatos suportados:
    - .txt  (texto simples)
    - .pdf  (PDF com texto extraível)
"""

import os
import sys
import time
from pathlib import Path

# Adicionar a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

load_dotenv()

# ── Configuração ─────────────────────────────────────────────────────────────

DATA_DIR     = Path(os.getenv("DATA_DIR", "data/leis"))
CHROMA_DIR   = Path(os.getenv("CHROMA_DIR", "data/chroma_db"))
COLLECTION   = os.getenv("CHROMA_COLLECTION", "legislacao_portuguesa")

# Tamanho e sobreposição dos fragmentos de texto (em caracteres)
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150

# Modelo de embeddings (corre localmente, sem custos de API)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ── Funções de leitura ────────────────────────────────────────────────────────

def ler_txt(caminho: Path) -> str:
    """Lê um ficheiro de texto simples."""
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def ler_pdf(caminho: Path) -> str:
    """Extrai texto de um PDF."""
    leitor = PdfReader(str(caminho))
    paginas = []
    for pagina in leitor.pages:
        texto = pagina.extract_text()
        if texto:
            paginas.append(texto)
    return "\n".join(paginas)


def ler_documento(caminho: Path) -> str | None:
    """Lê um documento consoante a extensão."""
    ext = caminho.suffix.lower()
    if ext == ".txt":
        return ler_txt(caminho)
    elif ext == ".pdf":
        return ler_pdf(caminho)
    else:
        print(f"  ⚠️  Formato não suportado: {caminho.name} — ignorado")
        return None


# ── Divisão em fragmentos ─────────────────────────────────────────────────────

def dividir_em_fragmentos(texto: str, nome_ficheiro: str) -> list[dict]:
    """
    Divide o texto em fragmentos sobrepostos.
    Retorna lista de dicionários com 'texto', 'id' e 'metadados'.
    """
    fragmentos = []
    inicio = 0
    indice = 0

    while inicio < len(texto):
        fim = min(inicio + CHUNK_SIZE, len(texto))

        # Tentar terminar o fragmento numa frase ou parágrafo
        if fim < len(texto):
            for separador in ["\n\n", "\n", ". ", " "]:
                pos = texto.rfind(separador, inicio, fim)
                if pos > inicio + CHUNK_SIZE // 2:
                    fim = pos + len(separador)
                    break

        fragmento_texto = texto[inicio:fim].strip()

        if fragmento_texto:
            fragmentos.append({
                "id":       f"{nome_ficheiro}__chunk_{indice}",
                "texto":    fragmento_texto,
                "metadados": {
                    "fonte":    nome_ficheiro,
                    "chunk":    indice,
                    "inicio":   inicio,
                    "fim":      fim,
                }
            })
            indice += 1

        inicio = fim - CHUNK_OVERLAP

    return fragmentos


# ── Indexação na base vetorial ────────────────────────────────────────────────

def indexar(fragmentos: list[dict], colecao) -> int:
    """Indexa os fragmentos na coleção ChromaDB. Retorna nº de fragmentos adicionados."""
    if not fragmentos:
        return 0

    # Verificar quais IDs já existem para evitar duplicados
    ids_existentes = set()
    try:
        resultado = colecao.get(ids=[f["id"] for f in fragmentos])
        ids_existentes = set(resultado["ids"])
    except Exception:
        pass

    novos = [f for f in fragmentos if f["id"] not in ids_existentes]

    if not novos:
        return 0

    colecao.add(
        ids       = [f["id"]      for f in novos],
        documents = [f["texto"]   for f in novos],
        metadatas = [f["metadados"] for f in novos],
    )

    return len(novos)


# ── Programa principal ────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Dr. José — Indexação de Documentos Legais")
    print("=" * 60)

    # Verificar pasta de dados
    if not DATA_DIR.exists():
        print(f"\n❌ Pasta '{DATA_DIR}' não encontrada.")
        print("   Cria a pasta e coloca lá os ficheiros .txt ou .pdf das leis.")
        sys.exit(1)

    ficheiros = list(DATA_DIR.glob("*.txt")) + list(DATA_DIR.glob("*.pdf"))

    if not ficheiros:
        print(f"\n⚠️  Nenhum ficheiro .txt ou .pdf encontrado em '{DATA_DIR}'.")
        print("   Consulta docs/fontes_legais.md para saber onde obter as leis.")
        sys.exit(0)

    print(f"\n📁 Pasta: {DATA_DIR}")
    print(f"📄 Ficheiros encontrados: {len(ficheiros)}")

    # Inicializar ChromaDB
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    cliente = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Função de embeddings multilingue (suporta português)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    colecao = cliente.get_or_create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"\n🔧 Modelo de embeddings: {EMBEDDING_MODEL}")
    print(f"💾 Base vetorial: {CHROMA_DIR}")
    print(f"📦 Coleção: {COLLECTION}\n")

    total_fragmentos = 0
    total_novos = 0

    for i, caminho in enumerate(sorted(ficheiros), 1):
        print(f"[{i}/{len(ficheiros)}] A processar: {caminho.name}")

        texto = ler_documento(caminho)
        if not texto:
            continue

        texto = texto.strip()
        if len(texto) < 50:
            print(f"  ⚠️  Ficheiro muito curto, ignorado.")
            continue

        fragmentos = dividir_em_fragmentos(texto, caminho.stem)
        novos = indexar(fragmentos, colecao)

        total_fragmentos += len(fragmentos)
        total_novos += novos

        status = f"✅ {len(fragmentos)} fragmentos"
        if novos < len(fragmentos):
            status += f" ({len(fragmentos) - novos} já existiam)"
        print(f"  {status}")

        time.sleep(0.1)  # Pequena pausa para não sobrecarregar

    print("\n" + "=" * 60)
    print(f"  ✅ Indexação concluída!")
    print(f"  📊 Total de fragmentos processados : {total_fragmentos}")
    print(f"  🆕 Novos fragmentos adicionados    : {total_novos}")
    print(f"  📦 Total na base vetorial          : {colecao.count()}")
    print("=" * 60)
    print("\nPode agora executar: python bot/jose.py")


if __name__ == "__main__":
    main()
