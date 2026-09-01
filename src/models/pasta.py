"""
Modelo de Dados para Configuração de Pasta de Cimento.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ConfigPasta:
    numero: int
    dist_fundo: float
    classe: str
    fator_agua_cimento: float = 0.0
    porcentagens: Dict[str, float] = field(default_factory=dict)
