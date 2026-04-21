# scripts/ingest.py - Versão com suporte a PDF, HTML, DOCX, TXT
import sys
from pathlib import Path
import re
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.retriever import LegalRetriever
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

# Tentar importar bibliotecas opcionais com fallback
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 não instalado. PDFs ignorados. Instala com: pip install PyPDF2")

try:
    import docx2txt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("docx2txt não instalado. DOCX ignorados. Instala com: pip install docx2txt")


def extract_from_pdf(file_path: Path) -> str:
    """Extrai texto de um ficheiro PDF"""
    if not PDF_AVAILABLE:
        return ""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Erro ao ler PDF {file_path.name}: {e}")
        return ""


def extract_from_html(file_path: Path) -> str:
    """Extrai texto de um ficheiro HTML, removendo tags"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove scripts e styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text(separator="\n")
        # Limpa linhas vazias excessivas
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    except Exception as e:
        logger.error(f"Erro ao ler HTML {file_path.name}: {e}")
        return ""


def extract_from_docx(file_path: Path) -> str:
    """Extrai texto de um ficheiro DOCX"""
    if not DOCX_AVAILABLE:
        return ""
    try:
        text = docx2txt.process(str(file_path))
        return text
    except Exception as e:
        logger.error(f"Erro ao ler DOCX {file_path.name}: {e}")
        return ""


def extract_from_txt(file_path: Path) -> str:
    """Extrai texto de um ficheiro TXT"""
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Erro ao ler TXT {file_path.name}: {e}")
        return ""


def process_file(file_path: Path) -> tuple[str, str]:
    """
    Processa um ficheiro consoante a extensão
    Retorna (texto_extraido, tipo_ficheiro)
    """
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return extract_from_pdf(file_path), 'PDF'
    elif suffix == '.html' or suffix == '.htm':
        return extract_from_html(file_path), 'HTML'
    elif suffix == '.docx':
        return extract_from_docx(file_path), 'DOCX'
    elif suffix == '.txt':
        return extract_from_txt(file_path), 'TXT'
    else:
        logger.warning(f"Formato não suportado: {suffix} - {file_path.name}")
        return "", "DESCONHECIDO"


def main():
    print("\n" + "="*60)
    print("📚 Dr. José - Indexação da Base de Conhecimento (Multiformato)")
    print("="*60)
    print("Formatos suportados: .txt, .pdf, .html, .docx\n")

    retriever = LegalRetriever()

    # Procurar todos os ficheiros suportados
    supported_extensions = ['*.txt', '*.pdf', '*.html', '*.htm', '*.docx']
    all_files = []
    for ext in supported_extensions:
        all_files.extend(config.LEIS_DIR.glob(ext))

    if not all_files:
        print("❌ Nenhum ficheiro encontrado em data/leis/")
        print("   Formatos suportados: .txt, .pdf, .html, .docx")
        return

    print(f"📄 Encontrados {len(all_files)} ficheiros para processar.")

    all_texts = []
    files_processed = 0
    files_failed = 0

    for file_path in all_files:
        text, file_type = process_file(file_path)
        
        if text and len(text.strip()) > 100:
            all_texts.append(text)
            files_processed += 1
            logger.info(f"✅ Processado: {file_path.name} ({file_type}, {len(text):,} caracteres)")
        elif text:
            logger.warning(f"⚠️ Conteúdo muito curto: {file_path.name} ({len(text)} caracteres)")
            files_failed += 1
        else:
            logger.warning(f"❌ Falha ao processar: {file_path.name} ({file_type})")
            files_failed += 1

    if not all_texts:
        print("❌ Nenhum conteúdo válido encontrado nos ficheiros.")
        return

    # Indexar
    retriever.add_documents(all_texts)
    
    print("\n" + "="*60)
    print("✅ Indexação concluída!")
    print(f"   Ficheiros processados com sucesso: {files_processed}")
    print(f"   Ficheiros com falha: {files_failed}")
    print(f"   Total de documentos na base: {retriever._collection.count()}")
    print("\nAgora podes usar o bot:")
    print("   streamlit run app.py")
    print("   python -m bot.jose")

if __name__ == "__main__":
    main()
