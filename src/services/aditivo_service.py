"""
Serviço de gerenciamento, persistência e formatação do catálogo de aditivos (JSON).
"""

import json
import os
from typing import Dict
import pandas as pd
from config import DATA_DIR, DB_FILE, ADITIVOS_PADRAO
from src.utils.logger import logger


class AditivoService:
    """Gerencia a leitura, gravação e formatação de aditivos em arquivo JSON e DataFrame."""

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
    def salvar_banco(aditivos_db: Dict[str, dict]) -> None:
        """Salva o dicionário completo de aditivos no arquivo JSON."""
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(aditivos_db, f, indent=4, ensure_ascii=False)
            logger.info(f"Banco de aditivos salvo com sucesso em: {DB_FILE}")
        except Exception as e:
            logger.error(f"Erro ao salvar banco de aditivos: {e}")

    @staticmethod
    def salvar_aditivo(nome: str, densidade: float, tipo: str, categoria: str = "Especial / Outro") -> Dict[str, dict]:
        """Adiciona um novo aditivo ao banco e salva persistentemente."""
        db = AditivoService.carregar_aditivos()
        db[nome] = {
            "densidade": float(densidade),
            "tipo": tipo,
            "categoria": categoria
        }
        AditivoService.salvar_banco(db)
        logger.info(f"Novo aditivo adicionado com sucesso: '{nome}' (densidade={densidade}, tipo={tipo}, categoria={categoria})")
        return db

    @staticmethod
    def restaurar_padrao() -> Dict[str, dict]:
        """Restaura o banco com os 26 aditivos canônicos do catálogo padrão."""
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(ADITIVOS_PADRAO, f, indent=4, ensure_ascii=False)
            logger.info("Catálogo de aditivos padrão restaurado.")
        except Exception as e:
            logger.error(f"Erro ao restaurar catálogo padrão: {e}")
        return ADITIVOS_PADRAO.copy()

    @staticmethod
    def obter_dataframe(aditivos_db: Dict[str, dict]) -> pd.DataFrame:
        """Converte o dicionário de aditivos em um DataFrame formatado para visualização em tabela."""
        dados = []
        for nome, info in aditivos_db.items():
            dados.append({
                "Nome do Aditivo": nome,
                "Categoria": info.get("categoria", "Geral"),
                "Tipo": str(info.get("tipo", "solido")).capitalize(),
                "SG": f"{info.get('densidade', 1.0):.2f}",
                "Dosagem Usual": info.get("dosagem_tipica", "Conforme projeto"),
                "Aplicação / Indicação": info.get("indicacao", "-")
            })
        return pd.DataFrame(dados)
