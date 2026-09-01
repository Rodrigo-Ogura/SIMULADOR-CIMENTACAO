"""
Serviço de gerenciamento e persistência de aditivos (JSON).
"""

import json
import os
from typing import Dict
from config import DATA_DIR, DB_FILE, ADITIVOS_PADRAO
from src.utils.logger import logger


class AditivoService:
    """Gerencia a leitura e gravação de aditivos em arquivo JSON."""

    @staticmethod
    def inicializar_banco() -> Dict[str, dict]:
        """Garante que a pasta data/ e o arquivo aditivos_db.json existam."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)

        if not os.path.exists(DB_FILE):
            logger.info(f"Criando banco de aditivos padrão em: {DB_FILE}")
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(ADITIVOS_PADRAO, f, indent=4, ensure_ascii=False)
            return ADITIVOS_PADRAO.copy()
        
        return AditivoService.carregar_aditivos()

    @staticmethod
    def carregar_aditivos() -> Dict[str, dict]:
        """Carrega todos os aditivos cadastrados."""
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
                return db
        except Exception as e:
            logger.error(f"Erro ao carregar banco de aditivos: {e}")
            return ADITIVOS_PADRAO.copy()

    @staticmethod
    def salvar_aditivo(nome: str, densidade: float, tipo: str, categoria: str = "Especial / Outro") -> Dict[str, dict]:
        """Adiciona um novo aditivo ao banco e salva persistentemente."""
        db = AditivoService.carregar_aditivos()
        db[nome] = {
            "densidade": float(densidade),
            "tipo": tipo,
            "categoria": categoria
        }

        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)

        logger.info(f"Novo aditivo adicionado com sucesso: '{nome}' (densidade={densidade}, tipo={tipo}, categoria={categoria})")
        return db
