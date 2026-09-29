"""Serviço do agente especialista de cimentação via Groq Cloud API.

Permite inferência ultra-rápida na nuvem com modelos de ponta (Llama 3.3 70B, etc.),
dispensando a necessidade de Ollama ou GPU local no computador do usuário.
Aplica as mesmas regras determinísticas e guardrails do módulo requisitos_ia.
Fundamentado em API Spec 10A, API RP 10B, Bourgoyne et al. (Cap. 3) e Nelson & Guillot.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from config import GROQ_API_KEY, GROQ_DEFAULT_MODEL, GROQ_MODELS, GROQ_TEMPERATURE
from src.services.requisitos_ia import (
    construir_pedido_correcao,
    derivar_requisitos,
    filtrar_aditivos_relevantes,
    normalizar_recomendacao,
    resumo_requisitos,
    validar_dados_poco,
    validar_recomendacao,
)
from src.utils.logger import logger

try:
    from groq import Groq
    GROQ_INSTALADO = True
except ImportError:
    GROQ_INSTALADO = False
    Groq = None  # type: ignore


def _sanitizar_chave(chave: Any) -> str:
    """Remove espaços, quebras de linha e caracteres não-ASCII acidentais da chave."""
    if not chave:
        return ""
    texto = str(chave).strip()
    return "".join(c for c in texto if c.isascii() and not c.isspace())


def obter_cliente_groq(api_key: Optional[str] = None) -> Optional[Any]:
    """Obtém uma instância autenticada do cliente Groq."""
    if not GROQ_INSTALADO:
        return None
    chave = _sanitizar_chave(api_key or GROQ_API_KEY)
    if not chave:
        return None
    try:
        return Groq(api_key=chave)
    except Exception as erro:
        logger.error(f"Erro ao instanciar cliente Groq: {erro}")
        return None


def verificar_status_groq(api_key: Optional[str] = None) -> Tuple[bool, List[str], str]:
    """Verifica se a Groq API está acessível, valida a chave e retorna todos os modelos de chat disponíveis."""
    if not GROQ_INSTALADO:
        return False, GROQ_MODELS, "Biblioteca 'groq' não está instalada no ambiente virtual."

    chave = _sanitizar_chave(api_key or GROQ_API_KEY)
    if not chave:
        return False, GROQ_MODELS, "Chave de API da Groq não configurada. Insira sua GROQ_API_KEY."

    try:
        cliente = Groq(api_key=chave)
        lista_remota = cliente.models.list()
        
        # Filtra modelos estritamente voltados a geração de texto / chat (remove guardrails, whisper, áudio/voz, embeds)
        termos_exclusao = (
            "guard", "whisper", "embed", "prompt-guard", "tts", "moderation",
            "distil-whisper", "orpheus", "canopylabs", "audio", "voice", "speech"
        )
        candidatos = [
            m.id for m in lista_remota.data
            if not any(t in m.id.lower() for t in termos_exclusao)
        ]
        
        # Ordenação prioritária dos melhores LLMs de raciocínio de engenharia
        def pontuacao_modelo(nome: str) -> tuple:
            n = nome.lower()
            if "qwen3.8" in n or "qwen3.8-27b" in n:
                return (0, n)
            elif "gpt-oss-120b" in n:
                return (1, n)
            elif "compound" in n:
                return (2, n)
            elif "qwen3.6" in n or "qwen" in n:
                return (3, n)
            elif "llama" in n:
                return (4, n)
            elif "deepseek" in n:
                return (5, n)
            else:
                return (6, n)
        
        modelos_ordenados = sorted(candidatos, key=pontuacao_modelo)
        
        if not modelos_ordenados:
            modelos_ordenados = GROQ_MODELS

        return True, modelos_ordenados, "Groq Cloud API conectada com sucesso."
    except Exception as erro:
        msg = str(erro)
        if "invalid_api_key" in msg.lower() or "401" in msg:
            return False, GROQ_MODELS, "Chave de API da Groq inválida. Verifique sua chave em console.groq.com/keys."
        return False, GROQ_MODELS, f"Falha de conexão com Groq API: {msg}"


def _construir_prompt_sistema(catalogo_aditivos_filtrado: Dict[str, Any]) -> str:
    linhas_catalogo = []
    for nome, dados in catalogo_aditivos_filtrado.items():
        cat = dados.get("categoria", "Geral")
        dose = dados.get("dosagem_tipica", "Conforme projeto")
        linhas_catalogo.append(f"- {nome} ({cat}): usual {dose}")

    catalogo_formatado = "\n".join(linhas_catalogo)

    return f"""Você é um Engenheiro de Cimentação Sênior (API Spec 10A / API RP 10B e Bourgoyne et al. Cap. 3).
Projete uma formulação técnica para a pasta solicitada, respeitando a janela geomecânica e os requisitos operacionais.

CATÁLOGO HOMOLOGADO PARA ESTE CENÁRIO (use APENAS estes aditivos):
{catalogo_formatado}

DIRETRIZES TÉCNICAS:
1. Respeite as dosagens usuais e os limites API (% BWOC).
2. Densidade: mantenha overbalance sobre a lama e margem segura abaixo da fratura (densidade_lama < densidade_pasta < grad_fratura).
3. Campo `concentracao_bwoc_pct` deve ser numérico (ex: 35.0 para 35%, 0.40 para 0.40%).

FORMATO DE RESPOSTA OBRIGATÓRIO (apenas JSON válido):
{{
  "pasta_nome": "Nome da Pasta",
  "classe_cimento": "G",
  "densidade_alvo_ppg": 15.8,
  "densidade_lama_recomendada_ppg": 9.5,
  "agua_gal_sk": 5.0,
  "aditivos": [
    {{"nome": "Nome Exato do Aditivo", "concentracao_bwoc_pct": 0.40, "justificativa": "Razão técnica concisa"}}
  ],
  "parecer_tecnico": "Parecer executivo fundamentando a estabilidade e eficiência de deslocamento da pasta."
}}"""


def _construir_prompt_usuario(dados_poco: Dict[str, Any], tipo_pasta: str, requisitos: List[Dict[str, Any]]) -> str:
    return f"""Projete a formulação técnica para: **{tipo_pasta}**.

DADOS DO POÇO:
- Intervalo: {dados_poco.get('prof_topo', 0):.0f} m a {dados_poco.get('prof_base', 2000):.0f} m
- Janela de Densidade Alvo: {dados_poco.get('densidade_min_alvo', 15.0):.2f} a {dados_poco.get('densidade_max_alvo', 16.0):.2f} ppg
- Pressões: Poro = {dados_poco.get('grad_poro', 9.2):.2f} ppg | Fratura = {dados_poco.get('grad_fratura', 16.8):.2f} ppg | Lama = {dados_poco.get('dens_lama', 9.5):.2f} ppg
- Temperaturas: BHCT = {dados_poco.get('bhct_c', 60.0):.1f} °C | BHST = {dados_poco.get('bhst_c', 80.0):.1f} °C
- Condições: Gás={'Sim' if dados_poco.get('presenca_gas') else 'Não'}, Permeabilidade={'Sim' if dados_poco.get('zona_permeavel') else 'Não'}, Perda de Circulação={'Sim' if dados_poco.get('perda_circulacao') else 'Não'}, Reologia Crítica={'Sim' if dados_poco.get('reologia_critica') else 'Não'}
- Observações: {dados_poco.get('observacoes', 'Nenhuma')}

REQUISITOS CRÍTICOS A CUMPRIR:
{resumo_requisitos(requisitos)}

Retorne exclusivamente o JSON."""


def _chamar_groq(cliente: Any, modelo: str, mensagens: List[Dict[str, str]]) -> Tuple[bool, str, str]:
    try:
        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=mensagens,
            response_format={"type": "json_object"},
            temperature=GROQ_TEMPERATURE,
        )
        conteudo = resposta.choices[0].message.content or ""
        if not conteudo:
            return False, "", "A API da Groq retornou uma resposta vazia."
        return True, conteudo, ""
    except Exception as erro:
        logger.exception("Erro na chamada à Groq API")
        return False, "", f"Erro na Groq API: {erro}"


def _interpretar_resposta(conteudo: str, catalogo_aditivos: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
    try:
        resposta_bruta = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        return None, f"A resposta do modelo não é um JSON válido: {erro}"
    if not isinstance(resposta_bruta, dict):
        return None, "A resposta JSON do modelo deve ser um objeto."
    return normalizar_recomendacao(resposta_bruta, catalogo_aditivos), ""


def recomendar_formulacao_groq(
    dados_poco: Dict[str, Any],
    catalogo_aditivos: Dict[str, Any],
    tipo_pasta: str = "Tail Slurry (Sapata)",
    modelo: str = GROQ_DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Gera, valida e corrige uma formulação de cimentação via Groq Cloud API."""
    erros_entrada = validar_dados_poco(dados_poco)
    if erros_entrada:
        return False, None, "Dados do poço inválidos: " + " | ".join(erros_entrada)

    cliente = obter_cliente_groq(api_key)
    if cliente is None:
        return False, None, "Cliente Groq não inicializado. Verifique se a chave GROQ_API_KEY foi informada."

    requisitos = derivar_requisitos(dados_poco, tipo_pasta)
    catalogo_filtrado = filtrar_aditivos_relevantes(catalogo_aditivos, dados_poco, tipo_pasta)
    mensagens: List[Dict[str, str]] = [
        {"role": "system", "content": _construir_prompt_sistema(catalogo_filtrado)},
        {"role": "user", "content": _construir_prompt_usuario(dados_poco, tipo_pasta, requisitos)},
    ]

    for tentativa in (1, 2):
        logger.info("Gerando formulação via Groq Cloud (%s), tentativa %s.", modelo, tentativa)
        sucesso_chamada, conteudo, mensagem = _chamar_groq(cliente, modelo, mensagens)
        if not sucesso_chamada:
            return False, None, mensagem

        recomendacao, erro_parse = _interpretar_resposta(conteudo, catalogo_aditivos)
        if recomendacao is None:
            return False, None, erro_parse

        validacao = validar_recomendacao(recomendacao, requisitos, catalogo_aditivos)
        recomendacao["validacao_aderencia"] = validacao
        recomendacao["tentativas_ia"] = tentativa
        recomendacao["correcao_aplicada"] = tentativa > 1
        recomendacao["provedor"] = f"Groq Cloud ({modelo})"

        if validacao["conforme"]:
            logger.info("Formulação aprovada via Groq: %s/%s requisitos críticos.", validacao["requisitos_atendidos"], validacao["requisitos_total"])
            return True, recomendacao, "Recomendação aprovada após validação de requisitos críticos (Groq Cloud)."

        if tentativa == 1:
            logger.info("Solicitando autocorreção à Groq por pendências em requisitos...")
            mensagens.extend([
                {"role": "assistant", "content": conteudo},
                {"role": "user", "content": construir_pedido_correcao(validacao)},
            ])

    return False, recomendacao, "A formulação gerada pela Groq Cloud não atendeu a todos os requisitos críticos após 2 tentativas."
