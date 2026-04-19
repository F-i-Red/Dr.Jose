# utils/logger.py
import logging
import sys
from pathlib import Path

def setup_logger(name: str = "dr_jose", level: int = logging.INFO) -> logging.Logger:
    """Configura e retorna um logger estruturado"""
    
    # Criar diretório de logs se não existir
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato detalhado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para ficheiro
    file_handler = logging.FileHandler(log_dir / "dr_jose.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola (mais simples)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger
