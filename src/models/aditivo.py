"""
Modelo de Dados para Aditivos.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Aditivo:
    nome: str
    densidade: float
    tipo: Literal["solido", "salmoura"]
    categoria: str = "Outro"

    def to_dict(self) -> dict:
        return {
            "densidade": self.densidade,
            "tipo": self.tipo,
            "categoria": self.categoria
        }

    @classmethod
    def from_dict(cls, nome: str, data: dict) -> "Aditivo":
        return cls(
            nome=nome,
            densidade=float(data["densidade"]),
            tipo=data.get("tipo", "solido"),
            categoria=data.get("categoria", "Outro")
        )
