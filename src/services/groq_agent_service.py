"""Serviço do agente especialista de cimentação via Groq Cloud API.

Permite inferência ultra-rápida na nuvem com modelos de ponta (Llama 3.3 70B, etc.),
dispensando a necessidade de Ollama ou GPU local no computador do usuário.
Aplica as mesmas regras determinísticas e guardrails do módulo requisitos_ia.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from config import GROQ_API_KEY, GROQ_DEFAULT_MODEL, GROQ_MODELS, GROQ_TEMPERATURE
from src.services.requisitos_ia import (
    construir_pedido_correcao,
    derivar_requisitos,
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

--- CATÁLOGO FECHADO DE ADITIVOS HOMOLOGADOS ---
{catalogo_formatado}

--- EXEMPLOS CANÔNICOS DE REFERÊNCIA (FEW-SHOT) ---
Exemplo 1 (Poço Frio / Superfície: BHCT 18°C, BHST 35°C, densidade 12.8 ppg):
{{
  "pasta_nome": "Lead Slurry (Superfície)",
  "classe_cimento": "G",
  "densidade_alvo_ppg": 12.8,
  "agua_gal_sk": 7.5,
  "aditivos": [
    {{"nome": "Bentonita (Gel)", "concentracao_bwoc_pct": 3.0, "justificativa": "Extensor para atingir baixa densidade e estabilizar água livre em seção rasa."}},
    {{"nome": "Cloreto de Cálcio (Flocos)", "concentracao_bwoc_pct": 2.0, "justificativa": "Acelerador para ganho de resistência rápida em temperatura fria (BHCT 18°C)."}}
  ],
  "parecer_tecnico": "Pasta leve com pega acelerada para ancoragem de sapata de superfície."
}}

Exemplo 2 (Poço Profundo HPHT: BHCT 85°C, BHST 125°C, densidade 16.5 ppg, reologia crítica):
{{
  "pasta_nome": "Tail Slurry (Sapata)",
  "classe_cimento": "G",
  "densidade_alvo_ppg": 16.5,
  "agua_gal_sk": 5.0,
  "aditivos": [
    {{"nome": "Flor de Sílica (SSA-1)", "concentracao_bwoc_pct": 35.0, "justificativa": "35% BWOC para prevenção mandatória de regressão de resistência sob BHST 125°C."}},
    {{"nome": "Retardador HR-12", "concentracao_bwoc_pct": 0.50, "justificativa": "Retardador de alta performance para garantir tempo de espessamento em BHCT de 85°C."}},
    {{"nome": "Dispersante CFR-2", "concentracao_bwoc_pct": 0.35, "justificativa": "Otimiza a reologia e minimiza perdas de carga anulares durante o bombeio."}},
    {{"nome": "Barita", "concentracao_bwoc_pct": 20.0, "justificativa": "Densificante para atingir a densidade alvo de 16.5 ppg."}}
  ],
  "parecer_tecnico": "Pasta densificada e termoestável para isolamento de zona HPHT."
}}

FORMATO OBRIGATÓRIO: responda SOMENTE um JSON válido, sem texto fora do objeto.
UNIDADES: `concentracao_bwoc_pct` é sempre percentual BWOC numérico (ex: 35.0 significa 35% BWOC, 0.35 significa 0.35% BWOC)."""


def _construir_prompt_usuario(dados_poco: Dict[str, Any], tipo_pasta: str, requisitos: List[Dict[str, Any]]) -> str:
    return f"""Projete uma formulação técnica para a **{tipo_pasta}**.

--- DADOS OPERACIONAIS E GEOMECÂNICOS DO POÇO ---
- Profundidade medida: {dados_poco.get('prof_topo', 0):.1f} m até {dados_poco.get('prof_base', 2000):.1f} m
- Gradiente de poro: {dados_poco.get('grad_poro', 9.2):.2f} ppg
- Gradiente de fratura: {dados_poco.get('grad_fratura', 16.8):.2f} ppg
- Janela de densidade-alvo: {dados_poco.get('densidade_min_alvo', 15.0):.2f} a {dados_poco.get('densidade_max_alvo', 16.0):.2f} ppg
- Temperatura estática de fundo (BHST): {dados_poco.get('bhst_c', 80.0):.1f} °C
- Temperatura circulante de fundo (BHCT): {dados_poco.get('bhct_c', 60.0):.1f} °C
- Tempo estimado de bombeio: {dados_poco.get('tempo_bombeio_min', 120):.0f} min (+ 60 min de margem de espessamento)
- Formação de alta permeabilidade: {'Sim' if dados_poco.get('zona_permeavel', False) else 'Não'}
- Potencial de migração de gás: {'Sim' if dados_poco.get('presenca_gas', False) else 'Não'}
- Risco de perda de circulação: {'Sim' if dados_poco.get('perda_circulacao', False) else 'Não'}
- Reologia crítica / alta perda de carga anular: {'Sim' if dados_poco.get('reologia_critica', False) else 'Não'}
- Observações de engenharia: {dados_poco.get('observacoes', 'Nenhuma')}

--- REQUISITOS CRÍTICOS MANDATÓRIOS (DERIVADOS DETERMINISTICAMENTE) ---
{resumo_requisitos(requisitos)}

Retorne exclusivamente o JSON da formulação completa. Todos os requisitos críticos acima DEVEM ser atendidos na sua sugestão."""


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

    requisitos = derivar_requisitos(dados_poco)
    mensagens: List[Dict[str, str]] = [
        {"role": "system", "content": _construir_prompt_sistema(catalogo_aditivos)},
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
            continue

        logger.warning("Formulação bloqueada via Groq: %s pendências críticas após correção.", len(validacao["pendencias"]))
        recomendacao["bloqueada"] = True
        return False, recomendacao, "Formulação bloqueada: requisitos críticos não atendidos após correção via Groq Cloud. Revise os itens pendentes antes de aplicar na calculadora."

    return False, None, "Fluxo de recomendação Groq encerrado sem resultado."
