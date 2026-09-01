"""
Módulo de logging centralizado para o Simulador de Cimentação.
Grava logs em console e em arquivo de log em logs/cimentacao.log.
"""

import logging
import os
import sys
from config import LOGS_DIR, LOG_FILE


def setup_logger(name: str = "cimentacao") -> logging.Logger:
    """
    Configura e retorna uma instância do logger.
    """
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita adicionar múltiplos handlers se o logger já tiver handlers
    if not logger.handlers:
        # Formato detalhado do log
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File Handler (salva em arquivo)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler (imprime no terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Logger global padrão
logger = setup_logger()
