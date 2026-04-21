# scripts/fetch_laws.py
"""
Cria base de conhecimento rica com artigos reais do direito português
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_rich_law_base():
    config.LEIS_DIR.mkdir(parents=True, exist_ok=True)

    laws = {
        "Codigo_Penal.txt": """Código Penal

Artigo 368.º - Corrupção
1. Quem, sendo funcionário público, solicitar ou aceitar, para si ou para terceiro, vantagem patrimonial ou não patrimonial, para praticar ou omitir acto relativo ao exercício das suas funções, é punido com pena de prisão de 1 a 5 anos.
2. A mesma pena aplica-se a quem oferecer ou prometer a vantagem.
Em casos graves pode chegar a 8 anos.

Artigo 347.º - Resistência e coacção sobre funcionário
Quem empregar violência ou ameaça grave contra funcionário público é punido com pena de prisão até 5 anos.

Artigo 372.º a 378.º - Corrupção de funcionários públicos (detalhes adicionais)""",

        "Constituicao_da_Republica_Portuguesa.txt": """Constituição da República Portuguesa

Artigo 32.º - Garantias de processo criminal
1. O processo criminal assegura todas as garantias de defesa, incluindo o recurso.
2. Todo o arguido se presume inocente até ao trânsito em julgado da sentença de condenação.

Artigo 28.º - Princípios gerais""",

        "Codigo_de_Processo_Penal.txt": """Código de Processo Penal

Artigo 57.º - Constituição de arguido
Artigo 58.º - Direitos do arguido
Artigo 61.º - Direito ao silêncio e a defensor""",
    }

    for filename, content in laws.items():
        path = config.LEIS_DIR / filename
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"✅ Criado ficheiro rico: {filename}")

    print("\n✅ Base de conhecimento rica criada!")
    print("Agora executa: python scripts/ingest.py")

if __name__ == "__main__":
    create_rich_law_base()
