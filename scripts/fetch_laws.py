# scripts/fetch_laws.py
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
    SOURCES = {
        "constituicao": {
            "name": "Constituição da República Portuguesa",
            "url": "https://dre.pt/legislacao-consolidada/lei/1976/constituicao-da-republica-portuguesa",
            "diploma": "Constituicao_Republica_Portuguesa"
        },
        "codigo_civil": {
            "name": "Código Civil",
            "url": "https://dre.pt/legislacao-consolidada/lei/1966/codigo-civil",
            "diploma": "Codigo_Civil"
        },
        "codigo_penal": {
            "name": "Código Penal",
            "url": "https://dre.pt/legislacao-consolidada/decreto-lei/1982/codigo-penal",
            "diploma": "Codigo_Penal"
        },
        "codigo_trabalho": {
            "name": "Código do Trabalho",
            "url": "https://dre.pt/legislacao-consolidada/lei/2009/codigo-do-trabalho",
            "diploma": "Codigo_Trabalho"
        },
        "codigo_processo_penal": {
            "name": "Código de Processo Penal",
            "url": "https://dre.pt/legislacao-consolidada/decreto-lei/1987/codigo-de-processo-penal",
            "diploma": "Codigo_Processo_Penal"
        },
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Dr.Jose-LegalBot/1.0 (github.com/F-i-Red/Dr.Jose)'})
        config.LEIS_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_file = config.DATA_DIR / "laws_cache.json"
        self.cache_duration_days = 7

    def is_cache_valid(self) -> bool:
        if not self.cache_file.exists():
            return False
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            last_update = datetime.fromisoformat(cache.get('last_update', '2000-01-01'))
            return (datetime.now() - last_update).days < self.cache_duration_days
        except Exception:
            return False

    def fetch_from_dre(self, source_key: str) -> Optional[str]:
        source = self.SOURCES[source_key]
        try:
            logger.info(f"A buscar {source['name']}...")
            response = self.session.get(source['url'], timeout=45)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remover scripts, estilos e navegação
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            content = soup.get_text(separator="\n", strip=True)
            content = self._clean_text(content)

            output_file = config.LEIS_DIR / f"{source['diploma']}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"FONTE: {source['url']}\n")
                f.write(f"DATA: {datetime.now().isoformat()}\n")
                f.write(f"DIPLOMA: {source['name']}\n")
                f.write("=" * 80 + "\n\n")
                f.write(content)

            logger.info(f"✅ {source['name']} guardado ({len(content):,} caracteres)")
            return content

        except Exception as e:
            logger.error(f"❌ Erro ao buscar {source['name']}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        lines = [
            line for line in text.split('\n')
            if not re.match(r'^\s*\d+\s*$', line)
            and not re.match(r'^\s*DRE\s*$', line, re.I)
            and len(line.strip()) > 2
        ]
        text = '\n'.join(lines)
        return re.sub(r'\n\s*\n\s*\n', '\n\n', text).strip()

    def fetch_all(self, force_refresh: bool = False) -> bool:
        if not force_refresh and self.is_cache_valid():
            logger.info("📦 Usando cache válido (menos de 7 dias)")
            return True

        success_count = 0
        for key in self.SOURCES:
            if self.fetch_from_dre(key):
                success_count += 1
            time.sleep(2)  # Não sobrecarregar o DRE

        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                "last_update": datetime.now().isoformat(),
                "laws_downloaded": success_count
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 {success_count}/{len(self.SOURCES)} diplomas obtidos")
        return success_count > 0

    def list_available_laws(self) -> List[str]:
        if not config.LEIS_DIR.exists():
            return []
        return [f.stem for f in config.LEIS_DIR.glob("*.txt")]


def main():
    fetcher = LawFetcher()
    print("\n" + "=" * 60)
    print("📚 Dr. José - Download de Legislação Portuguesa")
    print("=" * 60)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Força novo download")
    args = parser.parse_args()

    if fetcher.fetch_all(force_refresh=args.force):
        print("\n✅ Leis obtidas com sucesso!")
        print(f"   Guardadas em: {config.LEIS_DIR}")
        print("\nAgora executa: python scripts/ingest.py")
    else:
        print("\n⚠️  Erro durante o download. Verifica a tua ligação.")


if __name__ == "__main__":
    main()
