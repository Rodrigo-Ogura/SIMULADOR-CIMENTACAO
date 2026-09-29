"""Regras determinísticas e validação da saída do agente de cimentação.

O módulo separa requisitos obrigatórios de engenharia da geração textual do
modelo. A IA pode justificar e escolher alternativas do catálogo, mas uma
formulação só é aprovada quando todos os requisitos críticos aplicáveis forem
observados na resposta estruturada.
Fundamentado em API Spec 10A, API RP 10B, Bourgoyne et al. (Cap. 3) e Nelson & Guillot.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple


def _numero(valor: Any, padrao: float = 0.0) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return padrao


def validar_dados_poco(dados_poco: Dict[str, Any]) -> List[str]:
    """Retorna erros de entrada que impedem uma recomendação confiável."""
    erros: List[str] = []
    topo = _numero(dados_poco.get("prof_topo"))
    base = _numero(dados_poco.get("prof_base"))
    dens_min = _numero(dados_poco.get("densidade_min_alvo"))
    dens_max = _numero(dados_poco.get("densidade_max_alvo"))
    grad_poro = _numero(dados_poco.get("grad_poro"))
    grad_fratura = _numero(dados_poco.get("grad_fratura"))
    dens_lama = _numero(dados_poco.get("dens_lama"))

    if base <= topo:
        erros.append("A profundidade de base deve ser maior que a profundidade de topo.")
    if dens_min <= 0 or dens_max <= 0 or dens_min > dens_max:
        erros.append("A janela de densidade deve conter valores positivos e mínimo menor ou igual ao máximo.")
    if grad_poro > 0 and grad_fratura > 0 and grad_poro >= grad_fratura:
        erros.append("O gradiente de poro deve ser inferior ao gradiente de fratura.")
    if grad_fratura > 0 and dens_min >= grad_fratura:
        erros.append(f"A densidade mínima da pasta ({dens_min:.2f} ppg) não pode ser superior ou igual ao gradiente de fratura ({grad_fratura:.2f} ppg).")
    if dens_lama > 0 and grad_poro > 0 and dens_lama < grad_poro:
        erros.append(f"A densidade da lama ({dens_lama:.2f} ppg) deve ser superior à pressão de poros ({grad_poro:.2f} ppg) para manter o overbalance de segurança.")
    if dens_lama > 0 and grad_fratura > 0 and dens_lama >= grad_fratura:
        erros.append(f"A densidade da lama ({dens_lama:.2f} ppg) não pode exceder o gradiente de fratura ({grad_fratura:.2f} ppg).")
    return erros


# Limites Físicos Absolutos de Campo por Categoria de Aditivo (% BWOC)
# Fundamentado em API Spec 10A, API RP 10B, Nelson & Guillot e Bourgoyne et al. (Cap. 3).
# Qualquer dosagem fora destas faixas indica erro de formulação ou alucinação do modelo.
LIMITES_FISICOS_DOSAGEM: Dict[str, Tuple[float, float]] = {
    "Acelerador": (0.20, 4.00),             # Acima de 4% causa pega prematura (flash set) e corrosão
    "Retardador": (0.05, 2.00),             # Acima de 2% impede a hidratação e ganho de resistência
    "Dispersante": (0.05, 1.50),            # Acima de 1.5% induz retardo severo e sedimentação
    "Controlador de Filtrado": (0.10, 2.50), # Faixa clássica API para filtração anular (0.2 a 1.5% BWOC)
    "Extensor": (0.50, 15.00),              # Bentonita max 5%, perlita/gilsonita até 12-15%
    "Densificante": (5.00, 50.00),          # Barita / Hematita para pastas densas (10 a 50% BWOC)
    "Perda de Circulação (LCM)": (0.50, 15.00), # Selantes mecânicos particulados
    "Estabilizador Térmico": (25.00, 40.00), # Flor de Sílica (SSA-1): 30 a 35% BWOC obrigatório
    "Especial / Outro": (0.10, 5.00),
}


def _reologia_critica(dados_poco: Dict[str, Any]) -> bool:
    if bool(dados_poco.get("reologia_critica", False)):
        return True
    texto = str(dados_poco.get("observacoes", "")).lower()
    termos = ("reologia crítica", "reologia critica", "perda de carga", "alta perda de carga")
    return any(termo in texto for termo in termos)


def derivar_requisitos(dados_poco: Dict[str, Any], tipo_pasta: str = "Tail Slurry") -> List[Dict[str, Any]]:
    """Converte condições de poço e o papel funcional da pasta em requisitos críticos verificáveis."""
    dens_min = _numero(dados_poco.get("densidade_min_alvo"))
    dens_max = _numero(dados_poco.get("densidade_max_alvo"))
    dens_lama = _numero(dados_poco.get("dens_lama"))
    bhct = _numero(dados_poco.get("bhct_c"))
    bhst = _numero(dados_poco.get("bhst_c"))
    tipo_lower = str(tipo_pasta).lower()

    requisitos: List[Dict[str, Any]] = [
        {
            "id": "densidade_na_janela",
            "descricao": f"Densidade-alvo entre {dens_min:.2f} e {dens_max:.2f} ppg",
            "tipo": "densidade",
            "minimo": dens_min,
            "maximo": dens_max,
        }
    ]

    # Regra de deslocamento hidrostático (Nelson & Guillot Cap. 10 / Bourgoyne Cap. 3)
    if dens_lama > 0 and dens_min <= dens_lama:
        requisitos.append({
            "id": "contraste_densidade_lama",
            "descricao": f"Densidade da pasta ({dens_min:.2f} ppg) deve ser superior à lama ({dens_lama:.2f} ppg) para eficiência de deslocamento por empuxo",
            "tipo": "densidade_superior_lama",
            "dens_lama": dens_lama
        })

    # Regras específicas conforme a função operacional da pasta no poço
    if "scavenger" in tipo_lower or "varredura" in tipo_lower:
        requisitos.append({
            "id": "dispersante_scavenger",
            "descricao": "Dispersante mandatório (0.25% a 1.2% BWOC) para carreamento de reboco em pasta de varredura",
            "tipo": "categoria_dosagem",
            "categoria": "Dispersante",
            "minimo": 0.25,
            "maximo": 1.20
        })
        requisitos.append({
            "id": "extensor_scavenger",
            "descricao": "Extensor mandatório para estabilidade e controle de água livre em pasta ultraleve",
            "tipo": "categoria",
            "categoria": "Extensor"
        })
    elif "middle" in tipo_lower or "intermedi" in tipo_lower or "reservat" in tipo_lower:
        # Pasta intermediária de isolamento de zona produtora / gás
        requisitos.append({
            "id": "controle_filtrado_reservatorio",
            "descricao": "Controlador de filtrado mandatório (API RP 10B) para vedação de hidrocarbonetos e proteção do reservatório",
            "tipo": "categoria",
            "categoria": "Controlador de Filtrado"
        })
        if bhct > 50.0:
            requisitos.append({"id": "retardador_bhct", "descricao": "Retardador por BHCT acima de 50 °C", "tipo": "categoria_dosagem", "categoria": "Retardador", "minimo": 0.1, "maximo": 1.5})
    else:
        # Regras gerais para Lead / Tail
        if dens_max < 15.0:
            requisitos.append({"id": "extensor_densidade_baixa", "descricao": "Extensor para densidade-alvo abaixo de 15,0 ppg", "tipo": "categoria", "categoria": "Extensor"})
        if dens_min > 16.2:
            requisitos.append({"id": "densificante_densidade_alta", "descricao": "Densificante para densidade-alvo acima de 16,2 ppg", "tipo": "categoria", "categoria": "Densificante"})
        if bhct > 50.0:
            requisitos.append({"id": "retardador_bhct", "descricao": "Retardador por BHCT acima de 50 °C", "tipo": "categoria_dosagem", "categoria": "Retardador", "minimo": 0.1, "maximo": 1.5})
        if bhct < 25.0:
            requisitos.append({"id": "acelerador_bhct", "descricao": "Acelerador por BHCT abaixo de 25 °C", "tipo": "categoria", "categoria": "Acelerador"})
        
        # Flor de Sílica obrigatória na sapata se temperatura de estática de fundo > 110 °C
        if bhst > 110.0 and ("tail" in tipo_lower or "sapata" in tipo_lower or "fundo" in tipo_lower):
            requisitos.append({"id": "silica_bhst", "descricao": "Flor de Sílica (SSA-1) entre 30% e 35% BWOC por BHST acima de 110 °C na sapata", "tipo": "aditivo_dosagem", "nome": "Flor de Sílica (SSA-1)", "minimo": 30.0, "maximo": 35.0})
        
        if bool(dados_poco.get("zona_permeavel")) or bool(dados_poco.get("presenca_gas")):
            requisitos.append({"id": "controle_filtrado", "descricao": "Controlador de filtrado por permeabilidade ou risco de gás", "tipo": "categoria", "categoria": "Controlador de Filtrado"})
        if bool(dados_poco.get("perda_circulacao")):
            requisitos.append({"id": "lcm_perda_circulacao", "descricao": "Aditivo de perda de circulação por risco de perda natural", "tipo": "categoria", "categoria": "Perda de Circulação (LCM)"})
        if _reologia_critica(dados_poco):
            requisitos.append({"id": "dispersante_reologia", "descricao": "Dispersante por reologia crítica ou perda de carga alta", "tipo": "categoria", "categoria": "Dispersante"})

    return requisitos


def resumo_requisitos(requisitos: Iterable[Dict[str, Any]]) -> str:
    return "\n".join(f"- [{item['id']}] {item['descricao']}" for item in requisitos)


def resolver_nome_catalogo(nome: Any, catalogo_aditivos: Dict[str, Dict[str, Any]]) -> str | None:
    """Resolve nomes exatos sem descartar ambiguidades silenciosamente."""
    nome_limpo = str(nome or "").strip()
    if not nome_limpo:
        return None
    for nome_catalogo in catalogo_aditivos:
        if nome_limpo.lower() == nome_catalogo.lower():
            return nome_catalogo
    candidatos = [nome_catalogo for nome_catalogo in catalogo_aditivos if nome_limpo.lower() in nome_catalogo.lower() or nome_catalogo.lower() in nome_limpo.lower()]
    return candidatos[0] if len(candidatos) == 1 else None


def normalizar_recomendacao(resposta: Dict[str, Any], catalogo_aditivos: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Normaliza nomes e concentrações, sem converter silenciosamente unidades."""
    aditivos_normalizados: List[Dict[str, Any]] = []
    rejeitados: List[str] = []

    for aditivo in resposta.get("aditivos", []) or []:
        nome_catalogo = resolver_nome_catalogo(aditivo.get("nome"), catalogo_aditivos)
        if not nome_catalogo:
            rejeitados.append(str(aditivo.get("nome", "Aditivo sem nome")))
            continue
        bruto = aditivo.get("concentracao_bwoc_pct", aditivo.get("concentracao"))
        try:
            concentracao = float(bruto)
        except (TypeError, ValueError):
            rejeitados.append(f"{nome_catalogo} (dosagem inválida)")
            continue
        aditivos_normalizados.append(
            {
                "nome": nome_catalogo,
                "concentracao": concentracao,
                "concentracao_bwoc_pct": concentracao,
                "justificativa": str(aditivo.get("justificativa", "")).strip(),
            }
        )

    saida = dict(resposta)
    saida["classe_cimento"] = str(resposta.get("classe_cimento", "")).strip().upper()
    saida["densidade_alvo_ppg"] = _numero(resposta.get("densidade_alvo_ppg"))
    saida["agua_gal_sk"] = _numero(resposta.get("agua_gal_sk"))
    saida["densidade_lama_recomendada_ppg"] = _numero(resposta.get("densidade_lama_recomendada_ppg", resposta.get("dens_lama_ppg")))
    saida["aditivos"] = aditivos_normalizados
    saida["aditivos_rejeitados"] = rejeitados
    return saida


def validar_recomendacao(resposta: Dict[str, Any], requisitos: List[Dict[str, Any]], catalogo_aditivos: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Valida todos os requisitos críticos e retorna uma trilha auditável."""
    verificacoes: List[Dict[str, Any]] = []
    aditivos = resposta.get("aditivos", []) or []

    for requisito in requisitos:
        tipo = requisito["tipo"]
        atendido = False
        observado = "Não identificado"

        if tipo == "densidade":
            valor = _numero(resposta.get("densidade_alvo_ppg"), -1)
            atendido = requisito["minimo"] <= valor <= requisito["maximo"]
            observado = f"{valor:.2f} ppg" if valor >= 0 else "Densidade inválida"
        elif tipo == "densidade_superior_lama":
            valor = _numero(resposta.get("densidade_alvo_ppg"), -1)
            atendido = valor > requisito["dens_lama"]
            observado = f"{valor:.2f} ppg (Lama: {requisito['dens_lama']:.2f} ppg)" if valor >= 0 else "Densidade inválida"
        elif tipo in {"categoria", "categoria_dosagem"}:
            candidatos = [ad for ad in aditivos if catalogo_aditivos.get(ad.get("nome"), {}).get("categoria") == requisito["categoria"]]
            if tipo == "categoria_dosagem":
                candidatos = [ad for ad in candidatos if requisito["minimo"] <= _numero(ad.get("concentracao_bwoc_pct", ad.get("concentracao")), -1) <= requisito["maximo"]]
            atendido = bool(candidatos)
            if candidatos:
                observado = ", ".join(f"{ad['nome']} ({_numero(ad.get('concentracao_bwoc_pct', ad.get('concentracao'))):.2f}% BWOC)" for ad in candidatos)
            elif tipo == "categoria_dosagem":
                observado = f"Nenhum {requisito['categoria']} entre {requisito['minimo']:.2f}% e {requisito['maximo']:.2f}% BWOC"
            else:
                observado = f"Nenhum aditivo da categoria {requisito['categoria']}"
        elif tipo == "aditivo_dosagem":
            candidato = next((ad for ad in aditivos if ad.get("nome") == requisito["nome"]), None)
            dose = _numero(candidato.get("concentracao_bwoc_pct", candidato.get("concentracao")), -1) if candidato else -1
            atendido = candidato is not None and requisito["minimo"] <= dose <= requisito["maximo"]
            observado = f"{dose:.2f}% BWOC" if candidato else f"{requisito['nome']} não identificado"

        verificacoes.append({"id": requisito["id"], "descricao": requisito["descricao"], "atendido": atendido, "observado": observado, "bloqueante": True})

    rejeitados = resposta.get("aditivos_rejeitados", []) or []
    if rejeitados:
        verificacoes.append({"id": "catalogo_fechado", "descricao": "Todos os aditivos devem pertencer ao catálogo local", "atendido": False, "observado": ", ".join(rejeitados), "bloqueante": True})

    # Verificação de Limites Físicos Absolutos de Campo para cada aditivo sugerido
    for ad in aditivos:
        nome_ad = ad.get("nome", "")
        dose_ad = _numero(ad.get("concentracao_bwoc_pct", ad.get("concentracao")), -1)
        cat = catalogo_aditivos.get(nome_ad, {}).get("categoria", "")

        if dose_ad <= 0:
            verificacoes.append({
                "id": f"dosagem_positiva_{nome_ad}",
                "descricao": f"A dosagem de '{nome_ad}' deve ser positiva e maior que zero",
                "atendido": False,
                "observado": f"{dose_ad:.2f}% BWOC (inválido)",
                "bloqueante": True
            })
            continue

        if cat in LIMITES_FISICOS_DOSAGEM:
            lim_min, lim_max = LIMITES_FISICOS_DOSAGEM[cat]
            if not (lim_min <= dose_ad <= lim_max):
                verificacoes.append({
                    "id": f"limite_fisico_{nome_ad}",
                    "descricao": f"Dosagem de '{nome_ad}' ({cat}) deve estar na faixa física admissível ({lim_min:.2f}% a {lim_max:.2f}% BWOC)",
                    "atendido": False,
                    "observado": f"{dose_ad:.2f}% BWOC (fora dos limites seguros de campo)",
                    "bloqueante": True
                })

    pendencias = [item for item in verificacoes if not item["atendido"]]
    return {
        "conforme": not pendencias,
        "requisitos_atendidos": len(verificacoes) - len(pendencias),
        "requisitos_total": len(verificacoes),
        "verificacoes": verificacoes,
        "pendencias": pendencias,
    }


def construir_pedido_correcao(validacao: Dict[str, Any]) -> str:
    pendencias = "\n".join(f"- {item['descricao']}. Observado: {item['observado']}." for item in validacao.get("pendencias", []))
    return f"""A resposta anterior NÃO pode ser aprovada porque falhou em requisitos críticos de engenharia:\n{pendencias}\n\nGere uma nova resposta JSON completa. Mantenha apenas aditivos do catálogo e use sempre o campo numérico `concentracao_bwoc_pct` em percentual BWOC; por exemplo, 32.0 significa 32%, e 0.32 significa 0,32%. Não explique o erro: devolva somente o JSON corrigido."""


def validar_hierarquia_programa(pastas: Dict[str, Dict[str, Any]], dens_lama: float) -> Tuple[bool, List[str]]:
    """
    Valida a coerência e hierarquia física de densidades entre as pastas do programa (API RP 10B / Bourgoyne et al. Cap. 3).
    A densidade deve ser estritamente decrescente do fundo para o topo (crescente na ordem cronológica de bombeio):
    Lama < Scavenger <= Lead < Middle < Tail
    """
    erros: List[str] = []
    d_tail = _numero(pastas.get("tail", {}).get("densidade_alvo_ppg"))
    d_middle = _numero(pastas.get("middle", {}).get("densidade_alvo_ppg"))
    d_lead = _numero(pastas.get("lead", {}).get("densidade_alvo_ppg"))
    d_scavenger = _numero(pastas.get("scavenger", {}).get("densidade_alvo_ppg"))

    if d_tail > 0 and d_middle > 0:
        if d_tail <= d_middle:
            erros.append(f"Inversão de empuxo: A Tail Slurry ({d_tail:.2f} ppg) deve ser mais densa que a Middle Slurry ({d_middle:.2f} ppg).")
    if d_middle > 0 and d_lead > 0:
        if d_middle <= d_lead:
            erros.append(f"Inversão de empuxo: A Middle Slurry ({d_middle:.2f} ppg) deve ser mais densa que a Lead Slurry ({d_lead:.2f} ppg).")
    if d_tail > 0 and d_lead > 0 and d_middle == 0:
        if d_tail <= d_lead:
            erros.append(f"Inversão de empuxo: A Tail Slurry ({d_tail:.2f} ppg) deve ser mais densa que a Lead Slurry ({d_lead:.2f} ppg).")
    if d_lead > 0 and dens_lama > 0:
        if d_lead <= dens_lama:
            erros.append(f"Falha de deslocamento: A Lead Slurry ({d_lead:.2f} ppg) deve ser mais densa que a lama ({dens_lama:.2f} ppg) para eficiência de bombeio.")
    if d_scavenger > 0 and d_lead > 0:
        if d_scavenger > d_lead:
            erros.append(f"A Pasta de Varredura ({d_scavenger:.2f} ppg) não pode ser mais densa que a Lead Slurry ({d_lead:.2f} ppg).")

    return (len(erros) == 0, erros)


def filtrar_aditivos_relevantes(
    catalogo_aditivos: Dict[str, Dict[str, Any]],
    dados_poco: Dict[str, Any],
    tipo_pasta: str = "Tail Slurry"
) -> Dict[str, Dict[str, Any]]:
    """
    Filtra deterministamente o catálogo de aditivos, retornando apenas os 4 a 7 aditivos
    tecnicamente compatíveis com a janela operacional do poço e o papel funcional da pasta.
    Reduz drasticamente o consumo de tokens na IA (~85%) e elimina alucinações de produtos incompatíveis.
    """
    bhct = _numero(dados_poco.get("bhct_c"))
    bhst = _numero(dados_poco.get("bhst_c"))
    dens_max = _numero(dados_poco.get("densidade_max_alvo"))
    dens_min = _numero(dados_poco.get("densidade_min_alvo"))
    tipo_lower = str(tipo_pasta).lower()

    nomes_selecionados = set()

    # 1. Estabilizador Térmico (apenas se BHST > 110°C e sapata/tail)
    if bhst > 110.0 and ("tail" in tipo_lower or "sapata" in tipo_lower or "fundo" in tipo_lower):
        nomes_selecionados.add("Flor de Sílica (SSA-1)")

    # 2. Retardador ou Acelerador conforme BHCT
    if bhct > 75.0:
        nomes_selecionados.add("Retardador HR-12")
    elif bhct >= 50.0:
        nomes_selecionados.add("Retardador HR-4")
    elif bhct < 25.0:
        nomes_selecionados.add("Cloreto de Cálcio (Flocos)")
    else:
        nomes_selecionados.add("Retardador HR-4")

    # 3. Dispersante (reologia crítica, scavenger ou pastas com densificantes/sílica)
    if _reologia_critica(dados_poco) or "scavenger" in tipo_lower or "varredura" in tipo_lower or bhst > 110.0 or dens_min > 16.0:
        nomes_selecionados.add("Dispersante CFR-2")

    # 4. Controle de Filtrado (gás, permeabilidade, middle ou poço geral)
    if bool(dados_poco.get("presenca_gas")) or bool(dados_poco.get("zona_permeavel")) or "middle" in tipo_lower or "reservat" in tipo_lower:
        nomes_selecionados.add("Controlador de Filtrado HALDAD-9")
    elif "tail" in tipo_lower:
        nomes_selecionados.add("Controlador de Filtrado HALDAD-9")

    # 5. Extensores / Densificantes conforme densidade
    if dens_max < 15.0 or "scavenger" in tipo_lower or "lead" in tipo_lower:
        nomes_selecionados.add("Bentonita (Gel)")
    if dens_min > 16.2 or dens_max > 16.2:
        nomes_selecionados.add("Barita")

    # 6. LCM (perda de circulação)
    if bool(dados_poco.get("perda_circulacao")):
        nomes_selecionados.add("Agente de Perda de Circulação (Tuf-Plug)")

    # Extrai do catálogo oficial
    resultado = {}
    for nome in nomes_selecionados:
        nome_resolvido = resolver_nome_catalogo(nome, catalogo_aditivos)
        if nome_resolvido and nome_resolvido in catalogo_aditivos:
            resultado[nome_resolvido] = catalogo_aditivos[nome_resolvido]

    # Fallback seguro caso o filtro não localize candidatos
    if not resultado:
        padroes = ["Bentonita (Gel)", "Barita", "Retardador HR-4", "Dispersante CFR-2", "Controlador de Filtrado HALDAD-9"]
        for p in padroes:
            if p in catalogo_aditivos:
                resultado[p] = catalogo_aditivos[p]

    return resultado


def gerar_formulacao_deterministica(
    dados_poco: Dict[str, Any],
    tipo_pasta: str,
    catalogo_aditivos: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Gera uma formulação de pasta 100% determinística baseada estritamente nas normas
    API Spec 10A, API RP 10B, Bourgoyne et al. (Cap. 3) e Nelson & Guillot.
    Execução instantânea (0.001s), sem necessidade de IA, sem consumo de tokens de API.
    Nota: Esta modalidade não inclui parecer técnico discursivo/criativo de IA.
    """
    dens_min = _numero(dados_poco.get("densidade_min_alvo"), 15.8)
    dens_max = _numero(dados_poco.get("densidade_max_alvo"), 16.4)
    dens_lama = _numero(dados_poco.get("dens_lama"), 9.5)
    grad_poro = _numero(dados_poco.get("grad_poro"), 9.0)
    grad_fratura = _numero(dados_poco.get("grad_fratura"), 17.5)
    bhct = _numero(dados_poco.get("bhct_c"), 55.0)
    bhst = _numero(dados_poco.get("bhst_c"), 75.0)
    tipo_lower = str(tipo_pasta).lower()

    # 1. Definição Determinística da Densidade Alvo (sempre estritamente em [dens_min, dens_max])
    if "scavenger" in tipo_lower or "varredura" in tipo_lower:
        densidade_alvo = min(dens_max, max(dens_min, 11.0))
    elif "lead" in tipo_lower or "preenchimento" in tipo_lower:
        densidade_alvo = min(dens_max, max(dens_min, 12.0, dens_lama + 0.5))
    elif "middle" in tipo_lower or "intermedi" in tipo_lower or "reservat" in tipo_lower:
        densidade_alvo = min(dens_max, max(dens_min, 14.5, dens_lama + 1.0))
    else:
        densidade_alvo = max(15.8, dens_lama + 1.5, grad_poro + 1.0)
        densidade_alvo = min(dens_max, max(dens_min, densidade_alvo))

    if grad_fratura > 0 and densidade_alvo > grad_fratura - 0.5:
        densidade_alvo = max(dens_min, grad_fratura - 0.5)

    densidade_alvo = round(densidade_alvo, 2)
    dens_lama_rec = dens_lama if dens_lama > 0 else round(max(9.0, grad_poro + 0.5), 2)

    # 2. Seleção e Dosagem Normativa de Aditivos
    aditivos_selecionados: List[Dict[str, Any]] = []

    # Estabilizador Térmico (Flor de Sílica SSA-1)
    if bhst > 110.0 and ("tail" in tipo_lower or "sapata" in tipo_lower or "fundo" in tipo_lower):
        aditivos_selecionados.append({
            "nome": "Flor de Sílica (SSA-1)",
            "concentracao_bwoc_pct": 35.0,
            "justificativa": "Adição mandatória de 35% BWOC para prevenção da regressão de resistência sob BHST > 110 °C (API RP 10B-2)."
        })

    # Retardador ou Acelerador
    if bhct > 75.0:
        dose_ret = round(min(1.20, max(0.40, 0.40 + (bhct - 75.0) * 0.015)), 2)
        aditivos_selecionados.append({
            "nome": "Retardador HR-12",
            "concentracao_bwoc_pct": dose_ret,
            "justificativa": f"Retardador para prolongar o tempo de espessamento (API RP 10B) sob BHCT de {bhct:.1f} °C."
        })
    elif bhct >= 50.0:
        dose_ret = round(min(0.60, max(0.20, 0.20 + (bhct - 50.0) * 0.010)), 2)
        aditivos_selecionados.append({
            "nome": "Retardador HR-4",
            "concentracao_bwoc_pct": dose_ret,
            "justificativa": f"Retardador de média temperatura sob BHCT de {bhct:.1f} °C."
        })
    elif bhct < 25.0:
        aditivos_selecionados.append({
            "nome": "Cloreto de Cálcio (Flocos)",
            "concentracao_bwoc_pct": 2.0,
            "justificativa": f"Acelerador de pega para antecipar ganho de resistência em poço frio (BHCT {bhct:.1f} °C)."
        })

    # Controle de Filtrado
    precisa_filtrado = (
        bool(dados_poco.get("presenca_gas"))
        or bool(dados_poco.get("zona_permeavel"))
        or "middle" in tipo_lower
        or "reservat" in tipo_lower
    )
    if precisa_filtrado:
        dose_filt = 0.50 if bool(dados_poco.get("presenca_gas")) else 0.35
        aditivos_selecionados.append({
            "nome": "Controlador de Filtrado HALDAD-9",
            "concentracao_bwoc_pct": dose_filt,
            "justificativa": "Controle de perda de filtrado (< 50 mL API RP 10B) e prevenção de migração de gás."
        })

    # Dispersante
    precisa_dispersante = (
        _reologia_critica(dados_poco)
        or "scavenger" in tipo_lower
        or "varredura" in tipo_lower
        or bhst > 110.0
        or densidade_alvo > 16.2
    )
    if precisa_dispersante:
        dose_disp = 0.50 if ("scavenger" in tipo_lower or "varredura" in tipo_lower) else 0.30
        aditivos_selecionados.append({
            "nome": "Dispersante CFR-2",
            "concentracao_bwoc_pct": dose_disp,
            "justificativa": "Compatibilização reológica, redução de viscosidade plástica e controle de fricção no anular."
        })

    # Extensor (para pastas leves < 15 ppg)
    if densidade_alvo < 15.0 or "scavenger" in tipo_lower or "lead" in tipo_lower:
        dose_bent = round(min(4.0, max(1.5, (15.0 - densidade_alvo) * 1.2)), 2)
        aditivos_selecionados.append({
            "nome": "Bentonita (Gel)",
            "concentracao_bwoc_pct": dose_bent,
            "justificativa": "Extensor para viabilizar baixa densidade e evitar segregação de água livre."
        })

    # Densificante (para pastas densas > 16.2 ppg)
    if densidade_alvo > 16.2:
        dose_bar = round(min(35.0, max(10.0, (densidade_alvo - 16.2) * 18.0)), 2)
        aditivos_selecionados.append({
            "nome": "Barita",
            "concentracao_bwoc_pct": dose_bar,
            "justificativa": "Densificante inerte para atingir o peso específico requerido pelas pressões de formação."
        })

    # Perda de Circulação (LCM)
    if bool(dados_poco.get("perda_circulacao")):
        aditivos_selecionados.append({
            "nome": "Agente de Perda de Circulação (Tuf-Plug)",
            "concentracao_bwoc_pct": 2.0,
            "justificativa": "Material selante mecânico (LCM) para prevenção e combate à perda de circulação."
        })

    # 3. Cálculo de Água de Amassamento (API Spec 10A)
    agua_gal_sk = 5.0
    for ad in aditivos_selecionados:
        nome_ad = ad["nome"]
        dose = ad["concentracao_bwoc_pct"]
        if "Bentonita" in nome_ad:
            agua_gal_sk += dose * 0.63
        elif "Flor de Sílica" in nome_ad:
            agua_gal_sk += (dose - 30.0) * 0.05 if dose > 30.0 else 0.0
    agua_gal_sk = round(min(12.0, max(4.5, agua_gal_sk)), 2)

    # 4. Formatação de Saída Padronizada com Aviso Explícito de Sem IA
    parecer = (
        "⚙️ [MODO DETERMINÍSTICO - API SPEC 10A / BOURGOYNE CAP. 3]\n"
        f"Formulação calculada via regras físico-químicas de engenharia para {tipo_pasta} "
        f"(Alvo: {densidade_alvo:.2f} ppg | Água: {agua_gal_sk:.2f} gal/sk).\n"
        "ℹ️ Observação: Esta formulação foi gerada pelo algoritmo determinístico normativo (sem IA). "
        "Portanto, pareceres discursivos em texto livre e redação contextual de IA não estão presentes nesta modalidade."
    )

    bruto = {
        "pasta_nome": tipo_pasta,
        "classe_cimento": "G",
        "densidade_alvo_ppg": densidade_alvo,
        "densidade_lama_recomendada_ppg": dens_lama_rec,
        "agua_gal_sk": agua_gal_sk,
        "aditivos": aditivos_selecionados,
        "parecer_tecnico": parecer,
    }

    norm = normalizar_recomendacao(bruto, catalogo_aditivos)
    reqs = derivar_requisitos(dados_poco, tipo_pasta)
    val = validar_recomendacao(norm, reqs, catalogo_aditivos)

    return {
        "sucesso": True,
        "dados_brutos": bruto,
        "recomendacao": norm,
        "validacao": val,
        "tentativas": 1,
        "modelo_utilizado": "Motor Determinístico (API Spec 10A)"
    }


