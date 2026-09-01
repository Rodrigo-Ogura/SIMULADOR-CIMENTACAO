"""Regras determinísticas e validação da saída do agente de cimentação.

O módulo separa requisitos obrigatórios de engenharia da geração textual do
modelo. A IA pode justificar e escolher alternativas do catálogo, mas uma
formulação só é aprovada quando todos os requisitos críticos aplicáveis forem
observados na resposta estruturada.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


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

    if base <= topo:
        erros.append("A profundidade de base deve ser maior que a profundidade de topo.")
    if dens_min <= 0 or dens_max <= 0 or dens_min > dens_max:
        erros.append("A janela de densidade deve conter valores positivos e mínimo menor ou igual ao máximo.")
    if grad_poro > 0 and grad_fratura > 0 and grad_poro >= grad_fratura:
        erros.append("O gradiente de poro deve ser inferior ao gradiente de fratura.")
    if grad_fratura > 0 and dens_max > grad_fratura - 0.5:
        erros.append("A densidade máxima deve permanecer ao menos 0,5 ppg abaixo do gradiente de fratura.")
    return erros


def _reologia_critica(dados_poco: Dict[str, Any]) -> bool:
    if bool(dados_poco.get("reologia_critica", False)):
        return True
    texto = str(dados_poco.get("observacoes", "")).lower()
    termos = ("reologia crítica", "reologia critica", "perda de carga", "alta perda de carga")
    return any(termo in texto for termo in termos)


def derivar_requisitos(dados_poco: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Converte condições de poço em requisitos críticos verificáveis."""
    dens_min = _numero(dados_poco.get("densidade_min_alvo"))
    dens_max = _numero(dados_poco.get("densidade_max_alvo"))
    bhct = _numero(dados_poco.get("bhct_c"))
    bhst = _numero(dados_poco.get("bhst_c"))

    requisitos: List[Dict[str, Any]] = [
        {
            "id": "densidade_na_janela",
            "descricao": f"Densidade-alvo entre {dens_min:.2f} e {dens_max:.2f} ppg",
            "tipo": "densidade",
            "minimo": dens_min,
            "maximo": dens_max,
        }
    ]

    if dens_max < 15.0:
        requisitos.append({"id": "extensor_densidade_baixa", "descricao": "Extensor para densidade-alvo abaixo de 15,0 ppg", "tipo": "categoria", "categoria": "Extensor"})
    if dens_min > 16.2:
        requisitos.append({"id": "densificante_densidade_alta", "descricao": "Densificante para densidade-alvo acima de 16,2 ppg", "tipo": "categoria", "categoria": "Densificante"})
    if bhct > 50.0:
        requisitos.append({"id": "retardador_bhct", "descricao": "Retardador por BHCT acima de 50 °C", "tipo": "categoria_dosagem", "categoria": "Retardador", "minimo": 0.1, "maximo": 1.5})
    if bhct < 25.0:
        requisitos.append({"id": "acelerador_bhct", "descricao": "Acelerador por BHCT abaixo de 25 °C", "tipo": "categoria", "categoria": "Acelerador"})
    if bhst > 110.0:
        requisitos.append({"id": "silica_bhst", "descricao": "Flor de Sílica (SSA-1) entre 30% e 35% BWOC por BHST acima de 110 °C", "tipo": "aditivo_dosagem", "nome": "Flor de Sílica (SSA-1)", "minimo": 30.0, "maximo": 35.0})
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
                "concentracao_bwoc_pct": concentracao,
                "concentracao": concentracao,
                "justificativa": str(aditivo.get("justificativa", "Aditivo recomendado para as condições do poço.")).strip(),
            }
        )

    saida = dict(resposta)
    saida["classe_cimento"] = str(resposta.get("classe_cimento", "")).strip().upper()
    saida["densidade_alvo_ppg"] = _numero(resposta.get("densidade_alvo_ppg"))
    saida["agua_gal_sk"] = _numero(resposta.get("agua_gal_sk"))
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
        elif tipo in {"categoria", "categoria_dosagem"}:
            candidatos = [ad for ad in aditivos if catalogo_aditivos.get(ad.get("nome"), {}).get("categoria") == requisito["categoria"]]
            if tipo == "categoria_dosagem":
                candidatos = [ad for ad in candidatos if requisito["minimo"] <= _numero(ad.get("concentracao_bwoc_pct"), -1) <= requisito["maximo"]]
            atendido = bool(candidatos)
            if candidatos:
                observado = ", ".join(f"{ad['nome']} ({_numero(ad.get('concentracao_bwoc_pct')):.2f}% BWOC)" for ad in candidatos)
            elif tipo == "categoria_dosagem":
                observado = f"Nenhum {requisito['categoria']} entre {requisito['minimo']:.2f}% e {requisito['maximo']:.2f}% BWOC"
            else:
                observado = f"Nenhum aditivo da categoria {requisito['categoria']}"
        elif tipo == "aditivo_dosagem":
            candidato = next((ad for ad in aditivos if ad.get("nome") == requisito["nome"]), None)
            dose = _numero(candidato.get("concentracao_bwoc_pct"), -1) if candidato else -1
            atendido = candidato is not None and requisito["minimo"] <= dose <= requisito["maximo"]
            observado = f"{dose:.2f}% BWOC" if candidato else f"{requisito['nome']} não identificado"

        verificacoes.append({"id": requisito["id"], "descricao": requisito["descricao"], "atendido": atendido, "observado": observado, "bloqueante": True})

    rejeitados = resposta.get("aditivos_rejeitados", []) or []
    if rejeitados:
        verificacoes.append({"id": "catalogo_fechado", "descricao": "Todos os aditivos devem pertencer ao catálogo local", "atendido": False, "observado": ", ".join(rejeitados), "bloqueante": True})

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
    return f"""A resposta anterior NÃO pode ser aprovada porque falhou em requisitos críticos:\n{pendencias}\n\nGere uma nova resposta JSON completa. Mantenha apenas aditivos do catálogo e use sempre o campo numérico `concentracao_bwoc_pct` em percentual BWOC; por exemplo, 32.0 significa 32%, e 0.32 significa 0,32%. Não explique o erro: devolva somente o JSON corrigido."""
