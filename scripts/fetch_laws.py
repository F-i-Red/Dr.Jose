# scripts/fetch_laws.py
"""
Utilitário para gestão de leis do Dr. José
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LawFetcher:
    """Classe compatível com app.py - gere as leis na pasta data/leis/"""
    
    SOURCES = {
        "crp": "Constituicao_da_Republica_Portuguesa.txt",
        "codigo_penal": "Codigo_Penal.txt",
        "codigo_civil": "Codigo_Civil.txt",
        "codigo_trabalho": "Codigo_do_Trabalho.txt",
        "codigo_processo_penal": "Codigo_de_Processo_Penal.txt",
    }
    
    def __init__(self):
        self.leis_dir = config.LEIS_DIR
        self.leis_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_all(self, force_refresh: bool = False) -> bool:
        """Verifica se as leis existem (não faz download automático)"""
        existing_files = list(self.leis_dir.glob("*.txt"))
        
        if not existing_files:
            logger.warning("Nenhum ficheiro de lei encontrado!")
            print("\n⚠️  Nenhuma lei encontrada em data/leis/")
            print("   Coloca os ficheiros .txt das leis nessa pasta")
            return False
        
        logger.info(f"✅ Encontrados {len(existing_files)} ficheiros de leis")
        return True


def create_sample_laws():
    """Cria ficheiros de exemplo com conteúdo real (para teste rápido)"""
    config.LEIS_DIR.mkdir(parents=True, exist_ok=True)
    
    laws = {
        "Codigo_Penal.txt": """Código Penal Português

Artigo 368.º - Corrupção
1. Quem, sendo funcionário público, solicitar ou aceitar, para si ou para terceiro, vantagem patrimonial ou não patrimonial, para praticar ou omitir acto relativo ao exercício das suas funções, é punido com pena de prisão de 1 a 5 anos.
2. A mesma pena aplica-se a quem oferecer ou prometer a vantagem.

Artigo 347.º - Resistência e coacção sobre funcionário
Quem empregar violência ou ameaça grave para se opor a que funcionário pratique acto relativo ao exercício das suas funções é punido com pena de prisão até 5 anos.""",

        "Constituicao_da_Republica_Portuguesa.txt": """Constituição da República Portuguesa

Artigo 32.º - Garantias de processo criminal
1. O processo criminal assegura todas as garantias de defesa, incluindo o recurso.
2. Todo o arguido se presume inocente até ao trânsito em julgado da sentença de condenação.""",

        "Codigo_de_Processo_Penal.txt": """Código de Processo Penal

Artigo 57.º - Constituição de arguido
Artigo 58.º - Direitos do arguido
Artigo 61.º - Direito ao silêncio e a defensor""",
    }

    for filename, content in laws.items():
        filepath = config.LEIS_DIR / filename
        if not filepath.exists():  # Só cria se não existir
            filepath.write_text(content, encoding="utf-8")
            logger.info(f"✅ Criado: {filename}")

    print(f"\n✅ Leis de exemplo criadas em {config.LEIS_DIR}")
    print("Agora executa: python scripts/ingest.py")


if __name__ == "__main__":
    create_sample_laws()
