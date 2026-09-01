"""
Serviço com a lógica matemática de cimentação de poços de petróleo.
"""

import math
from typing import List, Dict, Any
from config import M_SACO, RO_AGUA, D_CIMENTO, VOLUME_AGUA_POR_CLASSE
from src.models.pasta import ConfigPasta
from src.utils.logger import logger


def calcular_geometria(
    d_broca: float,
    d_ext: float,
    d_int: float,
    altura_secao: float,
    fator_excesso: float,
    dist_sapata: float,
    calc_colar: bool
) -> float:
    """
    Calcula o volume necessário para cobrir uma seção do anular (ft³).
    Inclui o volume entre sapata e colar flutuante se calc_colar=True.
    """
    vol_anular = (math.pi / 4) * (d_broca**2 - d_ext**2) * altura_secao / 144
    vol_colar = (math.pi / 4) * (d_int**2) * dist_sapata / 144 if calc_colar else 0
    vol_total = (vol_anular * fator_excesso) + vol_colar
    return vol_total


def processar_calculos_pastas(
    pastas_config: List[ConfigPasta],
    aditivos_db: Dict[str, dict],
    d_broca: float,
    d_ext: float,
    d_int: float,
    fator_excesso: float,
    dist_sapata: float
) -> List[Dict[str, Any]]:
    """
    Processa a lista de pastas e calcula rendimento, densidade, volume total e quantidade de sacos.
    """
    logger.info(f"Iniciando cálculo para {len(pastas_config)} pastas de cimento.")
    resultados = []

    for p in pastas_config:
        num_p = p.numero

        # Fator água-cimento (gal/saco)
        if p.fator_agua_cimento > 0:
            vol_agua_gal = p.fator_agua_cimento
        else:
            vol_agua_gal = VOLUME_AGUA_POR_CLASSE.get(p.classe, 5.0)

        massa_agua = vol_agua_gal * RO_AGUA
        massa_cimento = M_SACO
        vol_cimento_gal = massa_cimento / (D_CIMENTO * RO_AGUA)

        massa_total = massa_agua + massa_cimento
        vol_total_gal = vol_agua_gal + vol_cimento_gal

        composicao_volumes = {"Água": vol_agua_gal, "Cimento": vol_cimento_gal}

        for aditivo, pct in p.porcentagens.items():
            if pct > 0 and aditivo in aditivos_db:
                info = aditivos_db[aditivo]
                massa_adit = (pct / 100) * M_SACO

                if info['tipo'] == 'solido':
                    vol_adit = massa_adit / (info['densidade'] * RO_AGUA)
                else:
                    # Salmoura: substituição volumétrica referente à água pura
                    vol_adit = max(0, (massa_adit + massa_agua) / (info['densidade'] * RO_AGUA) - vol_agua_gal)

                massa_total += massa_adit
                vol_total_gal += vol_adit
                composicao_volumes[aditivo] = vol_adit

        rendimento = vol_total_gal / 7.5  # conversão gal -> ft³ por saco
        densidade = massa_total / vol_total_gal if vol_total_gal > 0 else 0

        # Colar flutuante é considerado apenas na pasta 1 (fundo do poço)
        considerar_colar = (num_p == 1)
        vol_necessario_ft3 = calcular_geometria(
            d_broca, d_ext, d_int, p.dist_fundo, fator_excesso, dist_sapata, considerar_colar
        )
        num_sacos = math.ceil(vol_necessario_ft3 / rendimento) if rendimento > 0 else 0

        # Cálculo da Pressão Hidrostática da seção (psi) = 0.052 * densidade (ppg) * altura (ft)
        p_hidrostatica = 0.052 * densidade * p.dist_fundo

        logger.info(
            f"Pasta {num_p}: Densidade={densidade:.2f} ppg, Rendimento={rendimento:.4f} ft³/sk, "
            f"Vol={vol_necessario_ft3:.2f} ft³, Sacos={num_sacos}, P_hid={p_hidrostatica:.2f} psi"
        )

        # Detalhamento de cada componente para a Ficha de Traço Operacional
        detalhes_componentes = [
            {
                'Componente': 'Água de Mistura',
                'Categoria': 'Fluido Base',
                'Dosagem': f"{vol_agua_gal:.2f} gal/sk",
                'Vol (gal/sk)': vol_agua_gal,
                'Massa (lb/sk)': massa_agua,
                'Massa Total (lb)': massa_agua * num_sacos,
                'Vol Total (bbl)': (vol_agua_gal * num_sacos) / 42.0
            },
            {
                'Componente': f"Cimento Classe {p.classe}",
                'Categoria': 'Cimento Base',
                'Dosagem': "100.0% (94 lb/sk)",
                'Vol (gal/sk)': vol_cimento_gal,
                'Massa (lb/sk)': massa_cimento,
                'Massa Total (lb)': massa_cimento * num_sacos,
                'Vol Total (bbl)': (vol_cimento_gal * num_sacos) / 42.0
            }
        ]

        for aditivo, pct in p.porcentagens.items():
            if pct > 0 and aditivo in aditivos_db:
                info = aditivos_db[aditivo]
                m_adit = (pct / 100) * M_SACO
                v_adit = composicao_volumes.get(aditivo, 0.0)
                detalhes_componentes.append({
                    'Componente': aditivo,
                    'Categoria': info.get('categoria', 'Aditivo'),
                    'Dosagem': f"{pct:.2f}% BWOC",
                    'Vol (gal/sk)': v_adit,
                    'Massa (lb/sk)': m_adit,
                    'Massa Total (lb)': m_adit * num_sacos,
                    'Vol Total (bbl)': (v_adit * num_sacos) / 42.0
                })

        resultados.append({
            'numero': num_p,
            'classe': p.classe,
            'densidade': densidade,
            'rendimento': rendimento,
            'volume': vol_necessario_ft3,
            'sacos': num_sacos,
            'altura': p.dist_fundo,
            'pressao_hidrostatica': p_hidrostatica,
            'composicao': composicao_volumes,
            'detalhes': detalhes_componentes
        })

    return resultados
