# scripts/fetch_laws.py
"""
Download automático das leis portuguesas mais recentes
Fontes oficiais:
- Diário da República Eletrónico (dre.pt)
- Procuradoria-Geral Distrital de Lisboa (pgl.pt)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
from typing import Dict, List, Optional
import re

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LawFetcher:
    """Classe para buscar leis de fontes oficiais online"""
    
    # URLs das fontes oficiais
    SOURCES = {
        "constituicao": {
            "name": "Constituição da República Portuguesa",
            "url": "https://dre.pt/legislacao-consolidada/lei/1976/constituicao-da-republica-portuguesa",
            "selector": "div.legislacao-consolidada",
            "diploma": "CRP"
        },
        "codigo_civil": {
            "name": "Código Civil",
            "url": "https://dre.pt/legislacao-consolidada/lei/1966/codigo-civil",
            "selector": "div.legislacao-consolidada",
            "diploma": "Código Civil"
        },
        "codigo_penal": {
            "name": "Código Penal",
            "url": "https://dre.pt/legislacao-consolidada/decreto-lei/1982/codigo-penal",
            "selector": "div.legislacao-consolidada",
            "diploma": "Código Penal"
        },
        "codigo_trabalho": {
            "name": "Código do Trabalho",
            "url": "https://dre.pt/legislacao-consolidada/lei/2009/codigo-do-trabalho",
            "selector": "div.legislacao-consolidada",
            "diploma": "Código do Trabalho"
        },
        "codigo_processo_penal": {
            "name": "Código de Processo Penal",
            "url": "https://dre.pt/legislacao-consolidada/decreto-lei/1987/codigo-de-processo-penal",
            "selector": "div.legislacao-consolidada",
            "diploma": "Código Processo Penal"
        }
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Dr.Jose-LegalBot/1.0 (https://github.com/F-i-Red/Dr.Jose)'
        })
        self.cache_file = config.DATA_DIR / "laws_cache.json"
        self.cache_duration_days = 7  # Atualizar a cada 7 dias
    
    def is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido"""
        if not self.cache_file.exists():
            return False
        
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        last_update = datetime.fromisoformat(cache.get('last_update', '2000-01-01'))
        days_old = (datetime.now() - last_update).days
        
        return days_old < self.cache_duration_days
    
    def fetch_from_dre(self, source_key: str) -> Optional[str]:
        """Busca texto da lei do Diário da República"""
        source = self.SOURCES[source_key]
        url = source['url']
        diploma = source['diploma']
        
        try:
            logger.info(f"A buscar {diploma} de {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tenta vários seletores possíveis
            content = None
            selectors = [
                source.get('selector', ''),
                'div.article-content',
                'div.texto-lei',
                'main article',
                '.content'
            ]
            
            for selector in selectors:
                if selector:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True)
                        break
            
            if not content:
                content = soup.get_text(strip=True)
            
            # Limpeza básica
            content = self._clean_text(content)
            
            # Guarda também como ficheiro local
            output_file = config.LEIS_DIR / f"{diploma.replace(' ', '_')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"FONTE: {url}\n")
                f.write(f"DATA DOWNLOAD: {datetime.now().isoformat()}\n")
                f.write(f"DIPLOMA: {diploma}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            logger.info(f"✅ {diploma} guardado com sucesso ({len(content)} caracteres)")
            return content
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar {diploma}: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Limpa o texto (remove linhas em branco excessivas, normaliza espaços)"""
        # Remove linhas com apenas números de página
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove linhas que são só números (páginas)
            if re.match(r'^\s*\d+\s*$', line):
                continue
            # Remove linhas com "DRE" isolado
            if re.match(r'^\s*DRE\s*$', line, re.IGNORECASE):
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        # Normaliza espaços em branco
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        return text.strip()
    
    def fetch_all(self, force_refresh: bool = False) -> bool:
        """Busca todas as leis das fontes configuradas"""
        
        if not force_refresh and self.is_cache_valid():
            logger.info(f"📦 Cache válido (última atualização há menos de {self.cache_duration_days} dias)")
            return True
        
        logger.info("🌐 A buscar versões mais recentes das leis online...")
        
        config.LEIS_DIR.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        results = {}
        
        for key in self.SOURCES:
            content = self.fetch_from_dre(key)
            if content:
                success_count += 1
                results[key] = {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "source": self.SOURCES[key]["url"]
                }
            else:
                results[key] = {"success": False}
            
            # Pequena pausa para não sobrecarregar o servidor
            time.sleep(2)
        
        # Guardar cache
        cache_data = {
            "last_update": datetime.now().isoformat(),
            "results": results,
            "laws_downloaded": success_count
        }
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Download concluído: {success_count}/{len(self.SOURCES)} diplomas obtidos")
        return success_count > 0
    
    def list_available_laws(self) -> List[str]:
        """Lista as leis disponíveis localmente"""
        if not config.LEIS_DIR.exists():
            return []
        
        return [f.stem for f in config.LEIS_DIR.glob("*.txt")]

def main():
    """Função principal - executa diretamente ou via ingest.py"""
    fetcher = LawFetcher()
    
    print("\n" + "="*60)
    print("📚 Download Automático de Legislação Portuguesa")
    print("="*60)
    print(f"Fontes: Diário da República Eletrónico (DRE)")
    print(f"Cache: {fetcher.cache_duration_days} dias")
    print("-"*60)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Força novo download ignorando cache")
    args = parser.parse_args()
    
    if fetcher.fetch_all(force_refresh=args.force):
        print("\n✅ Leis obtidas com sucesso!")
        print(f"📁 Local: {config.LEIS_DIR}")
        
        # Listar o que foi obtido
        laws = fetcher.list_available_laws()
        if laws:
            print("\n📖 Diplomas disponíveis:")
            for law in laws:
                print(f"   - {law}")
    else:
        print("\n⚠️ Algumas leis não foram obtidas. Verifica a ligação à internet.")
        print("   O bot vai usar as leis já existentes (se houver).")

if __name__ == "__main__":
    main()
