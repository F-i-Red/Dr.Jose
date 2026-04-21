# scripts/fetch_laws.py - Versão com scraping funcional para PGDL
"""
Descarrega legislação portuguesa de fontes oficiais com seleção interativa
"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Lista de diplomas principais com URLs corretas
DIPLOMAS = {
    "1": {
        "nome": "Constituição da República Portuguesa",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=4&tabela=leis",
        "filename": "Constituicao_da_Republica_Portuguesa.txt"
    },
    "2": {
        "nome": "Código Civil",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=5&tabela=leis",
        "filename": "Codigo_Civil.txt"
    },
    "3": {
        "nome": "Código Penal",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=7&tabela=leis",
        "filename": "Codigo_Penal.txt"
    },
    "4": {
        "nome": "Código do Trabalho",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=13&tabela=leis",
        "filename": "Codigo_do_Trabalho.txt"
    },
    "5": {
        "nome": "Código de Processo Penal",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=8&tabela=leis",
        "filename": "Codigo_de_Processo_Penal.txt"
    },
    "6": {
        "nome": "Código da Estrada",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=15&tabela=leis",
        "filename": "Codigo_da_Estrada.txt"
    },
    "7": {
        "nome": "Código do Procedimento Administrativo",
        "url": "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=9&tabela=leis",
        "filename": "Codigo_Procedimento_Administrativo.txt"
    }
}


def scrape_pgdl_robust(url: str) -> str:
    """
    Extrai o texto de uma página da PGDL usando múltiplas estratégias
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-PT,pt;q=0.8,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estratégia 1: Procurar div com conteúdo da lei
        content = None
        possible_selectors = [
            'div.texto-lei',
            'div#conteudo',
            'div.conteudo',
            'div.article-content',
            'main',
            'article',
            'div[class*="lei"]',
            'div[class*="texto"]',
            'div[class*="conteudo"]'
        ]
        
        for selector in possible_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0]
                break
        
        # Estratégia 2: Se não encontrou, procura por <p> dentro de <body>
        if not content:
            body = soup.find('body')
            if body:
                content = body
        
        if content:
            # Remove elementos indesejados
            for tag in content(['script', 'style', 'nav', 'footer', 'header', 'a[name]', 'form', 'input', 'button']):
                tag.decompose()
            
            # Remove elementos com classes que indicam navegação
            for tag in content.find_all(class_=re.compile(r'(menu|nav|header|footer|sidebar|toolbar)')):
                tag.decompose()
            
            # Extrai texto
            text = content.get_text(separator='\n')
            
            # Limpeza do texto
            lines = []
            for line in text.split('\n'):
                line = line.strip()
                # Filtra linhas muito curtas ou que parecem navegação
                if len(line) > 10 and not line.startswith('[') and not line.startswith('<<'):
                    lines.append(line)
            
            text = '\n'.join(lines)
            
            # Remove linhas duplicadas consecutivas
            final_lines = []
            last_line = None
            for line in text.split('\n'):
                if line != last_line:
                    final_lines.append(line)
                    last_line = line
            
            return '\n'.join(final_lines)
        
        return ""
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede ao aceder a {url}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Erro ao processar {url}: {e}")
        return ""


def download_diploma(diploma: dict) -> bool:
    """Descarrega e guarda um diploma"""
    print(f"   A descarregar {diploma['nome']}...")
    print(f"   URL: {diploma['url']}")
    
    content = scrape_pgdl_robust(diploma['url'])
    
    if content and len(content) > 1000:
        filepath = config.LEIS_DIR / diploma['filename']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Fonte: {diploma['url']}\n")
            f.write(f"Diploma: {diploma['nome']}\n")
            f.write(f"Data de download: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(content)
        
        logger.info(f"✅ {diploma['nome']} guardado ({len(content):,} caracteres)")
        print(f"   ✅ Guardado: {len(content):,} caracteres")
        return True
    else:
        logger.warning(f"⚠️ Conteúdo insuficiente para {diploma['nome']} ({len(content)} caracteres)")
        print(f"   ⚠️ Conteúdo insuficiente (apenas {len(content)} caracteres)")
        
        # Fallback: criar ficheiro com conteúdo mínimo para teste
        fallback_path = config.LEIS_DIR / diploma['filename']
        if not fallback_path.exists():
            fallback_content = f"""Fonte: {diploma['url']}
Diploma: {diploma['nome']}
AVISO: Não foi possível descarregar o conteúdo completo automaticamente.

Por favor, visita o site oficial em:
{diploma['url']}

e copia o conteúdo manualmente para este ficheiro.
"""
            fallback_path.write_text(fallback_content, encoding='utf-8')
            print(f"   📝 Criado ficheiro placeholder: {diploma['filename']}")
        return False


def show_menu():
    """Mostra menu interativo para selecionar diplomas"""
    print("\n" + "="*70)
    print("📚 Dr. José - Download de Legislação Portuguesa")
    print("="*70)
    print("\nDiplomas disponíveis para download:\n")
    
    for key, diploma in DIPLOMAS.items():
        # Verificar se já existe
        filepath = config.LEIS_DIR / diploma['filename']
        status = "✅" if filepath.exists() else "⬜"
        print(f"  [{key}] {status} {diploma['nome']}")
    
    print("\n  [a] Descarregar TODOS os diplomas principais")
    print("  [s] Sair sem descarregar")
    print("-"*70)


def check_existing_files():
    """Mostra quais diplomas já existem"""
    existing = []
    for key, diploma in DIPLOMAS.items():
        if (config.LEIS_DIR / diploma['filename']).exists():
            existing.append(diploma['nome'])
    
    if existing:
        print("\n📁 Diplomas já existentes:")
        for nome in existing:
            print(f"   ✅ {nome}")
        return True
    return False


def main():
    config.LEIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Mostrar ficheiros existentes
    check_existing_files()
    
    show_menu()
    
    escolha = input("\nEscolhe uma opção: ").strip().lower()
    
    if escolha == 's':
        print("Operação cancelada.")
        return
    
    if escolha == 'a':
        selecionados = list(DIPLOMAS.keys())
        print(f"\n📥 A descarregar {len(selecionados)} diplomas...")
    else:
        # Permite seleções múltiplas tipo "1,3,5"
        selecionados = [c.strip() for c in escolha.split(',') if c.strip() in DIPLOMAS]
        if not selecionados:
            print("❌ Opção inválida. Nenhum diploma selecionado.")
            return
    
    success_count = 0
    for i, key in enumerate(selecionados, 1):
        diploma = DIPLOMAS[key]
        print(f"\n[{i}/{len(selecionados)}] {diploma['nome']}")
        
        if download_diploma(diploma):
            success_count += 1
        time.sleep(2)  # Pausa para não sobrecarregar o servidor
    
    print(f"\n" + "="*70)
    print(f"📊 Resumo: {success_count}/{len(selecionados)} diplomas descarregados com sucesso")
    print(f"   Pasta: {config.LEIS_DIR}")
    
    if success_count > 0:
        print("\n▶️ Próximo passo: python scripts/ingest.py")
    else:
        print("\n⚠️ Nenhum diploma foi descarregado.")
        print("   Possíveis causas:")
        print("   • O site da PGDL pode estar temporariamente indisponível")
        print("   • Podes precisar de descarregar manualmente os ficheiros")
        print("   • Como alternativa, coloca os teus próprios ficheiros .txt em data/leis/")


if __name__ == "__main__":
    main()
