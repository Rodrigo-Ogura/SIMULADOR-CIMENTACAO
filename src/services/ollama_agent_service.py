"""Serviço do agente especialista de cimentação via Ollama Local.

A resposta do modelo é cercada por regras determinísticas: ela só é aprovada
quando passa pela validação de requisitos críticos aplicáveis ao poço.
Fundamentado em API Spec 10A, API RP 10B, Bourgoyne et al. (Cap. 3) e Nelson & Guillot.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import requests

from config import OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL, OLLAMA_TEMPERATURE, OLLAMA_TIMEOUT
from src.services.requisitos_ia import (
    construir_pedido_correcao,
    derivar_requisitos,
    normalizar_recomendacao,
    resumo_requisitos,
    validar_dados_poco,
    validar_recomendacao,
)
from src.utils.logger import logger


def verificar_status_ollama(base_url: str = OLLAMA_BASE_URL) -> Tuple[bool, List[str], str]:
    try:
        resposta = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        if resposta.status_code == 200:
            modelos = [item.get("name", "") for item in resposta.json().get("models", []) if item.get("name")]
            return True, modelos, "Ollama conectado com sucesso."
        return False, [], f"Servidor Ollama respondeu com status {resposta.status_code}."
    except requests.exceptions.ConnectionError:
        return False, [], "Não foi possível conectar ao Ollama. Verifique se o aplicativo está aberto e rodando."
    except Exception as erro:
        return False, [], f"Erro ao verificar status do Ollama: {erro}"


def _construir_prompt_sistema(catalogo_aditivos: Dict[str, Any]) -> str:
    linhas_catalogo = []
    for nome, dados in catalogo_aditivos.items():
        cat = dados.get("categoria", "Geral")
        tipo = dados.get("tipo", "solido")
        dens = dados.get("densidade", 1.0)
        dose = dados.get("dosagem_tipica", "Conforme projeto")
        ind = dados.get("indicacao", "")
        faixas_temp = []
        if "bhct_min_c" in dados:
            faixas_temp.append(f"BHCT {dados['bhct_min_c']:.0f} a {dados.get('bhct_max_c', 140):.0f}°C")
        elif "bhct_max_c" in dados:
            faixas_temp.append(f"BHCT < {dados['bhct_max_c']:.0f}°C")
        if "bhst_min_c" in dados:
            faixas_temp.append(f"BHST > {dados['bhst_min_c']:.0f}°C")
        temp_str = f" | {', '.join(faixas_temp)}" if faixas_temp else ""
        linhas_catalogo.append(f"- {nome} [Cat: {cat} | Tipo: {tipo} | d={dens:.2f} | Dosagem usual: {dose}{temp_str}] -> {ind}")

    catalogo_formatado = "\n".join(linhas_catalogo)

    return f"""Você é um Engenheiro de Cimentação Sênior, especializado em API Spec 10A / API RP 10B, Bourgoyne et al. (Cap. 3), Nelson & Guillot e Manuais da Indústria (Halliburton/Schlumberger).

Você deve gerar uma formulação tecnicamente rigorosa e consistente. Siga estritamente as heurísticas de engenharia da indústria para seleção de aditivos:

--- HEURÍSTICAS DE DECISÃO E SELEÇÃO TÉCNICA ---
1. RETARDADOR:
   - Se BHCT entre 50 °C e 75 °C: Selecione preferencialmente 'Retardador HR-4' (dosagem típica 0.20% a 0.40% BWOC).
   - Se BHCT acima de 75 °C: Selecione preferencialmente 'Retardador HR-12' (dosagem típica 0.40% a 0.80% BWOC).
2. ESTABILIZADOR TÉRMICO (BHST > 110 °C):
   - Adicione obrigatoriamente exatamente 35.0% BWOC de 'Flor de Sílica (SSA-1)' contra a regressão de resistência à compressão (strength retrogression).
3. CONTROLE DE FILTRADO (Permeabilidade ou Risco de Gás):
   - Selecione 'Controlador de Filtrado HALDAD-9' ou 'Controlador de Filtrado HALDAD-14' (dosagem 0.30% a 0.60% BWOC).
4. ACELERADOR DE PEGA (BHCT < 25 °C):
   - Selecione 'Cloreto de Cálcio (Flocos)' ou 'Cloreto de Cálcio (Salmoura)' (dosagem 1.50% a 2.00% BWOC).
5. DENSIDADE E REOLOGIA:
   - Se densidade < 15.0 ppg: Use 'Bentonita (Gel)' (1.5% a 3.0% BWOC).
   - Se densidade > 16.2 ppg: Use 'Barita' (15% a 35% BWOC).
   - Se reologia crítica ou alta perda de carga: Use 'Dispersante CFR-2' ou 'Dispersante CFR-1' (0.25% a 0.40% BWOC).
6. LAMA DE PERFURAÇÃO & EFICIÊNCIA DE DESLOCAMENTO (Bourgoyne et al. Cap. 3 / Nelson & Guillot Cap. 10):
   - A lama de perfuração deve manter overbalance sobre a pressão de poros (+0.30 a +0.80 ppg).
   - Para evitar canalização e instabilidade de Rayleigh-Taylor, a densidade da pasta de cimento deve superar a densidade da lama (densidade_lama < densidade_lead <= densidade_tail).
   - Indique sempre a `densidade_lama_recomendada_ppg` avaliando a janela geomecânica.

--- CATÁLOGO FECHADO DE ADITIVOS HOMOLOGADOS ---
{catalogo_formatado}

--- EXEMPLOS CANÔNICOS DE REFERÊNCIA (FEW-SHOT) ---
Exemplo 1 (Poço Frio / Superfície: BHCT 18°C, BHST 35°C, densidade 12.8 ppg, lama 9.2 ppg):
{{
  "pasta_nome": "Lead Slurry (Superfície)",
  "classe_cimento": "G",
  "densidade_alvo_ppg": 12.8,
  "densidade_lama_recomendada_ppg": 9.2,
  "agua_gal_sk": 7.5,
  "aditivos": [
    {{"nome": "Bentonita (Gel)", "concentracao_bwoc_pct": 3.0, "justificativa": "Extensor para atingir baixa densidade e estabilizar água livre em seção rasa."}},
    {{"nome": "Cloreto de Cálcio (Flocos)", "concentracao_bwoc_pct": 2.0, "justificativa": "Acelerador para ganho de resistência rápida em temperatura fria (BHCT 18°C)."}}
  ],
  "parecer_tecnico": "Pasta leve com pega acelerada para ancoragem de sapata de superfície e deslocamento sobre lama de 9.2 ppg."
}}

Exemplo 2 (Poço Profundo HPHT: BHCT 85°C, BHST 125°C, densidade 16.5 ppg, lama 10.8 ppg, reologia crítica):
{{
  "pasta_nome": "Tail Slurry (Sapata)",
  "classe_cimento": "G",
  "densidade_alvo_ppg": 16.5,
  "densidade_lama_recomendada_ppg": 10.8,
  "agua_gal_sk": 5.0,
  "aditivos": [
    {{"nome": "Flor de Sílica (SSA-1)", "concentracao_bwoc_pct": 35.0, "justificativa": "35% BWOC para prevenção mandatória de regressão de resistência sob BHST 125°C."}},
    {{"nome": "Retardador HR-12", "concentracao_bwoc_pct": 0.50, "justificativa": "Retardador de alta performance para garantir tempo de espessamento em BHCT de 85°C."}},
    {{"nome": "Dispersante CFR-2", "concentracao_bwoc_pct": 0.35, "justificativa": "Otimiza a reologia e minimiza perdas de carga anulares durante o bombeio."}},
    {{"nome": "Barita", "concentracao_bwoc_pct": 20.0, "justificativa": "Densificante para atingir a densidade alvo de 16.5 ppg."}}
  ],
  "parecer_tecnico": "Pasta densificada e termoestável para isolamento de zona HPHT com overbalance garantido."
}}

FORMATO OBRIGATÓRIO: responda SOMENTE um JSON válido, sem texto fora do objeto.
UNIDADES: `concentracao_bwoc_pct` é sempre percentual BWOC numérico (ex: 35.0 significa 35% BWOC, 0.35 significa 0.35% BWOC)."""


def _construir_prompt_usuario(dados_poco: Dict[str, Any], tipo_pasta: str, requisitos: List[Dict[str, Any]]) -> str:
    return f"""Projete uma formulação para a **{tipo_pasta}**.

--- DADOS OPERACIONAIS E GEOMECÂNICOS ---
- Profundidade medida: {dados_poco.get('prof_topo', 0):.1f} m até {dados_poco.get('prof_base', 2000):.1f} m
- Gradiente de poro: {dados_poco.get('grad_poro', 9.2):.2f} ppg
- Gradiente de fratura: {dados_poco.get('grad_fratura', 16.8):.2f} ppg
- Densidade da lama no poço: {dados_poco.get('dens_lama', 9.5):.2f} ppg
- Janela de densidade-alvo: {dados_poco.get('densidade_min_alvo', 15.0):.2f} a {dados_poco.get('densidade_max_alvo', 16.0):.2f} ppg
- BHST: {dados_poco.get('bhst_c', 80.0):.1f} °C
- BHCT: {dados_poco.get('bhct_c', 60.0):.1f} °C
- Tempo de bombeio: {dados_poco.get('tempo_bombeio_min', 120):.0f} min (+ 60 min de margem)
- Alta permeabilidade: {'Sim' if dados_poco.get('zona_permeavel', False) else 'Não'}
- Potencial de gás: {'Sim' if dados_poco.get('presenca_gas', False) else 'Não'}
- Perda de circulação: {'Sim' if dados_poco.get('perda_circulacao', False) else 'Não'}
- Reologia crítica / perda de carga alta: {'Sim' if dados_poco.get('reologia_critica', False) else 'Não'}
- Observações: {dados_poco.get('observacoes', 'Nenhuma')}

--- REQUISITOS CRÍTICOS DERIVADOS DETERMINISTICAMENTE ---
{resumo_requisitos(requisitos)}

Retorne somente o JSON da formulação completa. Todos os requisitos críticos devem aparecer na formulação."""


def _chamar_ollama(base_url: str, modelo: str, mensagens: List[Dict[str, str]]) -> Tuple[bool, str, str]:
    payload = {
        "model": modelo,
        "messages": mensagens,
        "format": "json",
        "stream": False,
        "options": {"temperature": OLLAMA_TEMPERATURE, "top_p": 1.0},
    }
    try:
        resposta = requests.post(f"{base_url.rstrip('/')}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT)
        if resposta.status_code != 200:
            return False, "", f"Ollama retornou erro HTTP {resposta.status_code}: {resposta.text}"
        conteudo = resposta.json().get("message", {}).get("content", "")
        if not conteudo:
            return False, "", "Ollama retornou uma mensagem vazia."
        return True, conteudo, ""
    except requests.exceptions.Timeout:
        return False, "", f"Tempo limite de {OLLAMA_TIMEOUT}s excedido aguardando o Ollama."
    except Exception as erro:
        logger.exception("Erro inesperado na comunicação com Ollama")
        return False, "", f"Erro inesperado: {erro}"


def _interpretar_resposta(conteudo: str, catalogo_aditivos: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
    try:
        resposta_bruta = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        return None, f"A resposta do modelo não é um JSON válido: {erro}"
    if not isinstance(resposta_bruta, dict):
        return None, "A resposta JSON do modelo deve ser um objeto."
    return normalizar_recomendacao(resposta_bruta, catalogo_aditivos), ""


def recomendar_formulacao(
    dados_poco: Dict[str, Any],
    catalogo_aditivos: Dict[str, Any],
    tipo_pasta: str = "Tail Slurry (Sapata)",
    modelo: str = OLLAMA_DEFAULT_MODEL,
    base_url: str = OLLAMA_BASE_URL,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Gera, valida e, quando necessário, solicita uma única correção ao agente."""
    erros_entrada = validar_dados_poco(dados_poco)
    if erros_entrada:
        return False, None, "Dados do poço inválidos: " + " | ".join(erros_entrada)

    requisitos = derivar_requisitos(dados_poco)
    mensagens: List[Dict[str, str]] = [
        {"role": "system", "content": _construir_prompt_sistema(catalogo_aditivos)},
        {"role": "user", "content": _construir_prompt_usuario(dados_poco, tipo_pasta, requisitos)},
    ]

    for tentativa in (1, 2):
        logger.info("Tentativa %s de recomendação via Ollama (%s)", tentativa, modelo)
        sucesso_chamada, conteudo, mensagem = _chamar_ollama(base_url, modelo, mensagens)
        if not sucesso_chamada:
            return False, None, mensagem

        recomendacao, erro_parse = _interpretar_resposta(conteudo, catalogo_aditivos)
        if recomendacao is None:
            return False, None, erro_parse

        validacao = validar_recomendacao(recomendacao, requisitos, catalogo_aditivos)
        recomendacao["validacao_aderencia"] = validacao
        recomendacao["tentativas_ia"] = tentativa
        recomendacao["correcao_aplicada"] = tentativa > 1
        recomendacao["provedor"] = f"Ollama Local ({modelo})"

        if validacao["conforme"]:
            logger.info("Formulação aprovada via Ollama: %s/%s requisitos.", validacao["requisitos_atendidos"], validacao["requisitos_total"])
            return True, recomendacao, "Recomendação aprovada após validação de requisitos críticos (Ollama Local)."

        if tentativa == 1:
            logger.info("Solicitando autocorreção ao Ollama por pendências em requisitos...")
            mensagens.extend([
                {"role": "assistant", "content": conteudo},
                {"role": "user", "content": construir_pedido_correcao(validacao)},
            ])

    return False, recomendacao, "A formulação gerada pelo Ollama não atendeu a todos os requisitos críticos após 2 tentativas."
