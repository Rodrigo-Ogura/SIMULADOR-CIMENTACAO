"""
Script de Auditoria Integral e Validação Funcional Automática do Simulador.
Testa todos os serviços, modelos de dados, motores matemáticos e regras de IA.
"""

import sys
import os
import json
import io
import math
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Garante path raiz
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import ADITIVOS_PADRAO, DATA_DIR, DB_FILE
from src.services.aditivo_service import AditivoService
from src.services.geomecanica_service import GeomecanicaService
from src.services.calculadora import calcular_geometria, processar_calculos_pastas
from src.models.pasta import ConfigPasta
from src.services.requisitos_ia import (
    derivar_requisitos,
    validar_dados_poco,
    validar_recomendacao,
    normalizar_recomendacao,
    validar_hierarquia_programa,
    filtrar_aditivos_relevantes,
    gerar_formulacao_deterministica,
    LIMITES_FISICOS_DOSAGEM
)
from src.services.groq_agent_service import _construir_prompt_sistema, _construir_prompt_usuario, _interpretar_resposta

falhas = []
sucessos = []

def registrar_teste(nome: str, condicao: bool, detalhe: str = ""):
    if condicao:
        sucessos.append(nome)
        print(f"  [OK] {nome}")
    else:
        falhas.append(f"{nome}: {detalhe}")
        print(f"  [FALHA] {nome} -> {detalhe}")


print("=" * 60)
print("INICIANDO CHECKUP GERAL DO SIMULADOR DE CIMENTAÇÃO")
print("=" * 60)

# ── TESTE 1: BANCO DE DADOS DE ADITIVOS E ADITIVOSERVICE ──
print("\n--- TESTE 1: AditivoService e Catálogo de Aditivos ---")
try:
    banco = AditivoService.carregar_aditivos()
    registrar_teste("Carregar banco de aditivos", isinstance(banco, dict) and len(banco) >= 20, f"Qtd: {len(banco)}")
    
    # Verifica integridade da Flor de Sílica
    silica = banco.get("Flor de Sílica (SSA-1)", {})
    registrar_teste("Categoria Flor de Sílica é Estabilizador Térmico", silica.get("categoria") == "Estabilizador Térmico", f"Cat: {silica.get('categoria')}")
    
    # Verifica DataFrame
    df_adit = AditivoService.obter_dataframe(banco)
    registrar_teste("Obter DataFrame de aditivos", isinstance(df_adit, pd.DataFrame) and len(df_adit) == len(banco))
    
    # Salvar e restaurar
    novo_db = AditivoService.salvar_aditivo("__Teste_Aditivo__", 1.5, "solido", "Geral")
    registrar_teste("Salvar novo aditivo", "__Teste_Aditivo__" in novo_db)
    novo_db.pop("__Teste_Aditivo__", None)
    AditivoService.salvar_banco(novo_db)
    registrar_teste("Remover aditivo de teste e salvar", "__Teste_Aditivo__" not in AditivoService.carregar_aditivos())
except Exception as e:
    falhas.append(f"Erro em AditivoService: {e}")

# ── TESTE 2: GEOMECANICA SERVICE ──
print("\n--- TESTE 2: GeomecanicaService e Perfis do Mar do Norte ---")
try:
    pocos = GeomecanicaService.listar_pocos_presets()
    registrar_teste("Listar poços presets", len(pocos) == 5, f"Poços: {pocos}")
    
    variantes = GeomecanicaService.listar_variantes()
    registrar_teste("Listar variantes", set(variantes.keys()) == {"A", "B", "K"})
    
    # Testa carga de todos os 5 poços nas variantes B e A
    total_presets_carregados = 0
    for p in pocos:
        for v in ("B", "A", "K"):
            df_p = GeomecanicaService.carregar_preset(p, v)
            if df_p is not None and len(df_p) > 50:
                total_presets_carregados += 1
                metricas = GeomecanicaService.extrair_metricas_resumo(df_p)
                assert "prof_max_m" in metricas
                assert "gargalo_min_ppg" in metricas
                assert "fratura_base_ppg" in metricas
                assert "poro_base_ppg" in metricas
                assert metricas["fratura_base_ppg"] > 14.0
    registrar_teste("Carga e métricas de 15 presets (5 poços x 3 variantes com Fratura Base > 14 ppg)", total_presets_carregados == 15, f"Carregados: {total_presets_carregados}/15")

    # Upload de CSV simulado
    csv_teste = "Profundidade (m),Gradiente de Poros (ppg),Gradiente de Fratura (ppg)\n1000,9.2,14.5\n2000,10.1,16.2\n3000,11.0,17.0\n"
    suc_up, df_up, msg_up = GeomecanicaService.processar_csv_upload(csv_teste, "m", "Teste Upload")
    registrar_teste("Processamento de CSV customizado (Upload)", suc_up and len(df_up) == 3, msg_up)
except Exception as e:
    falhas.append(f"Erro em GeomecanicaService: {e}")

# ── TESTE 3: CALCULADORA DE BALANÇO DE MASSA E RENDIMENTO ──
print("\n--- TESTE 3: Calculadora de Balanço de Massa e Hidráulica ---")
try:
    # Volume de anular simples
    vol = calcular_geometria(17.0, 13.375, 12.415, 1000.0, 1.5, 40.0, True)
    registrar_teste("Cálculo geométrico de anular", vol > 0, f"Vol: {vol:.2f} ft³")
    
    # Pastas com aditivos sólidos e líquidos
    p1 = ConfigPasta(
        numero=1, classe="G", dist_fundo=500.0, fator_agua_cimento=5.0,
        porcentagens={"Flor de Sílica (SSA-1)": 35.0, "Retardador HR-12": 0.5, "Dispersante CFR-2": 0.3}
    )
    p2 = ConfigPasta(
        numero=2, classe="G", dist_fundo=1500.0, fator_agua_cimento=7.5,
        porcentagens={"Bentonita (Gel)": 3.0}
    )
    res_pastas = processar_calculos_pastas([p1, p2], banco, 17.0, 13.375, 12.415, 1.5, 40.0)
    registrar_teste("Processar cálculos de 2 pastas", len(res_pastas) == 2)
    registrar_teste("Densidade P1 coerente (> 15.5 ppg)", res_pastas[0]['densidade'] > 15.5, f"d={res_pastas[0]['densidade']:.2f}")
    registrar_teste("Densidade P2 mais leve (< 14.5 ppg)", res_pastas[1]['densidade'] < 14.5, f"d={res_pastas[1]['densidade']:.2f}")
    registrar_teste("Rendimento e sacos positivos", res_pastas[0]['sacos'] > 0 and res_pastas[0]['rendimento'] > 0)
    registrar_teste("Pressão hidrostática calculada", res_pastas[0]['pressao_hidrostatica'] > 0)
except Exception as e:
    falhas.append(f"Erro em Calculadora: {e}")

# ── TESTE 4: REQUISITOS IA & MOTOR DETERMINÍSTICO ──
print("\n--- TESTE 4: Requisitos IA, Guardrails e Motor Determinístico ---")
try:
    cenarios = [
        ("Tail HPHT Quente", {
            'prof_topo': 2500, 'prof_base': 3000, 'grad_poro': 9.2, 'grad_fratura': 16.5,
            'dens_lama': 9.6, 'densidade_min_alvo': 15.8, 'densidade_max_alvo': 16.4,
            'bhst_c': 118.0, 'bhct_c': 85.0, 'presenca_gas': True, 'reologia_critica': True
        }, "Tail Slurry (Sapata / Fundo)"),
        ("Middle Reservatório Gás", {
            'prof_topo': 1500, 'prof_base': 2500, 'grad_poro': 9.0, 'grad_fratura': 15.8,
            'dens_lama': 9.6, 'densidade_min_alvo': 14.5, 'densidade_max_alvo': 15.4,
            'bhst_c': 75.0, 'bhct_c': 55.0, 'presenca_gas': True
        }, "Middle Slurry (Intermediária / Reservatório / Gás)"),
        ("Lead Leve Frio", {
            'prof_topo': 500, 'prof_base': 1500, 'grad_poro': 8.8, 'grad_fratura': 14.5,
            'dens_lama': 9.6, 'densidade_min_alvo': 12.0, 'densidade_max_alvo': 13.5,
            'bhst_c': 35.0, 'bhct_c': 22.0, 'perda_circulacao': True
        }, "Lead Slurry (Preenchimento / Topo)"),
        ("Scavenger Varredura", {
            'prof_topo': 0, 'prof_base': 500, 'grad_poro': 8.5, 'grad_fratura': 13.0,
            'dens_lama': 9.6, 'densidade_min_alvo': 11.0, 'densidade_max_alvo': 11.8,
            'bhst_c': 25.0, 'bhct_c': 18.0
        }, "Scavenger Slurry (Varredura)")
    ]

    recs_geradas = {}
    for nome_cen, d_cen, tipo_cen in cenarios:
        # Teste de filtragem
        adits_filt = filtrar_aditivos_relevantes(banco, d_cen, tipo_cen)
        registrar_teste(f"Filtro de aditivos enxuto para {nome_cen}", 2 <= len(adits_filt) <= 7, f"Qtd: {len(adits_filt)}")
        
        # Teste do motor determinístico
        res_det = gerar_formulacao_deterministica(d_cen, tipo_cen, banco)
        val = res_det['validacao']
        recs_geradas[tipo_cen] = res_det['recomendacao']
        registrar_teste(f"Motor Determinístico {nome_cen} 100% conforme", val['conforme'], f"Pendências: {val.get('pendencias')}")
        
    # Teste de Hierarquia de programa (Rayleigh-Taylor)
    hier_ok, hier_errs = validar_hierarquia_programa({
        'tail': recs_geradas["Tail Slurry (Sapata / Fundo)"],
        'middle': recs_geradas["Middle Slurry (Intermediária / Reservatório / Gás)"],
        'lead': recs_geradas["Lead Slurry (Preenchimento / Topo)"],
        'scavenger': recs_geradas["Scavenger Slurry (Varredura)"]
    }, 9.6)
    registrar_teste("Validação de hierarquia Tetra-Pasta (Lama < Scav <= Lead < Mid < Tail)", hier_ok, f"Erros: {hier_errs}")

    # Teste específico: Sincronização do Poço 15/9-13 (Var. B) em Programa Bi-Pasta
    df_13b = GeomecanicaService.carregar_preset("15/9-13", "B")
    metr_13b = GeomecanicaService.extrair_metricas_resumo(df_13b)
    meta_13b = GeomecanicaService.obter_metadados_poco_preset("15/9-13")
    lama_13b = float(meta_13b.get("dens_lama_fundo_ppg", 10.85))
    poro_b = float(metr_13b.get("poro_base_ppg", 9.28))
    frac_b = float(metr_13b.get("fratura_base_ppg", 16.12))

    tail_dmin = max(15.60, round(lama_13b + 1.0, 2), round(poro_b + 1.0, 2))
    tail_dmax = max(tail_dmin + 0.40, min(16.50, round(frac_b - 0.5, 2)))

    dados_tail_13b = {
        'prof_topo': 2200, 'prof_base': 3260, 'grad_poro': poro_b, 'grad_fratura': frac_b,
        'dens_lama': lama_13b, 'densidade_min_alvo': tail_dmin, 'densidade_max_alvo': tail_dmax,
        'bhst_c': 112.0, 'bhct_c': 73.0, 'tempo_bombeio_min': 150
    }
    dados_lead_13b = {
        'prof_topo': 1000, 'prof_base': 2200, 'grad_poro': 8.5, 'grad_fratura': 14.5,
        'dens_lama': min(lama_13b, 12.0 - 0.5), 'densidade_min_alvo': 12.0, 'densidade_max_alvo': 13.5,
        'bhst_c': 75.0, 'bhct_c': 45.0, 'tempo_bombeio_min': 180
    }
    res_t = gerar_formulacao_deterministica(dados_tail_13b, "Tail Slurry (Sapata / Fundo)", banco)["recomendacao"]
    res_l = gerar_formulacao_deterministica(dados_lead_13b, "Lead Slurry (Preenchimento / Topo)", banco)["recomendacao"]
    bi_ok, bi_err = validar_hierarquia_programa({"tail": res_t, "lead": res_l}, lama_13b)
    registrar_teste(
        "Programa Bi-Pasta com Perfil 15/9-13 (B) sem Inversão de Empuxo",
        bi_ok and res_t['densidade_alvo_ppg'] > res_l['densidade_alvo_ppg'],
        f"Tail: {res_t['densidade_alvo_ppg']:.2f} ppg > Lead: {res_l['densidade_alvo_ppg']:.2f} ppg (Lama: {lama_13b:.2f} ppg)"
    )

except Exception as e:
    falhas.append(f"Erro em Requisitos IA: {e}")

# ── TESTE 5: PROMPTS LEVES E INTERPRETAÇÃO GROQ ──
print("\n--- TESTE 5: Prompts Leves e Robustez de Parser JSON ---")
try:
    p_sis = _construir_prompt_sistema(adits_filt)
    p_usr = _construir_prompt_usuario(d_cen, tipo_cen, derivar_requisitos(d_cen, tipo_cen))
    tokens_est = (len(p_sis) + len(p_usr)) // 4
    registrar_teste("Prompt enxuto abaixo de 600 tokens (Groq 1k seguro)", tokens_est < 600, f"Tokens estimados: ~{tokens_est}")
    
    # Teste parser JSON resiliente
    json_teste = '{"pasta_nome": "Tail", "classe_cimento": "G", "densidade_alvo_ppg": 16.0, "agua_gal_sk": 5.0, "aditivos": [{"nome": "Flor de Sílica (SSA-1)", "concentracao_bwoc_pct": 35.0}], "parecer_tecnico": "Ok"}'
    rec_p, erro_p = _interpretar_resposta(json_teste, banco)
    registrar_teste("Interpretar resposta JSON válida", rec_p is not None and rec_p['densidade_alvo_ppg'] == 16.0, erro_p)
except Exception as e:
    falhas.append(f"Erro em Prompts/Parser: {e}")

# ── TESTE 6: INTEGRIDADE DE CONFIG E LIMITES FÍSICOS ──
print("\n--- TESTE 6: Limites Físicos e Configurações Globais ---")
try:
    for cat_nome, (l_min, l_max) in LIMITES_FISICOS_DOSAGEM.items():
        assert l_min > 0, f"Limite mínimo de {cat_nome} deve ser > 0"
        assert l_max > l_min, f"Limite máximo de {cat_nome} deve ser maior que o mínimo"
    registrar_teste("Matriz de limites físicos de dosagem consistente", True)
except Exception as e:
    falhas.append(f"Erro em limites físicos: {e}")

print("\n" + "=" * 60)
print(f"RELATÓRIO FINAL: {len(sucessos)} TESTES PASSARAM | {len(falhas)} FALHAS")
print("=" * 60)
if falhas:
    print("\nFALHAS IDENTIFICADAS:")
    for f in falhas:
        print(f"  [X] {f}")
    sys.exit(1)
else:
    print("\n[OK] TODAS AS ROTINAS E MÓDULOS ESTÃO FUNCIONANDO EM PERFEITA ORDEM!")
    sys.exit(0)
