"""
Simulador Visual de Cimentação de Poços de Petróleo
Interface Profissional de Engenharia de Poços — Estilo OpenLab Drilling (NORCE)
"""

import streamlit as st
from src.services.aditivo_service import AditivoService
from src.services.calculadora import processar_calculos_pastas
from src.ui.tab_parametros_poco import render_parametros_poco
from src.ui.tabs_pastas import render_config_pastas
from src.ui.tab_agente_ia import render_tab_agente_ia
from src.ui.dashboard import render_dashboard, render_analise_individual
from src.utils.logger import logger

# Configuração da página Streamlit
st.set_page_config(
    page_title="Cementing Simulator & Engineering Suite | OpenLab Style",
    layout="wide",
    page_icon="🛢️",
    initial_sidebar_state="collapsed"
)

# Injeção de CSS Industrial de Alto Padrão com Tipografia Harmoniosa e Legível
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    /* Fundo da aplicação */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-size: 15px;
    }

    /* Tipografia Harmoniosa e Legível */
    h1 { font-size: 1.75rem !important; font-weight: 700 !important; color: #38bdf8 !important; letter-spacing: -0.02em; }
    h2 { font-size: 1.45rem !important; font-weight: 600 !important; color: #f8fafc !important; }
    h3 { font-size: 1.25rem !important; font-weight: 600 !important; color: #38bdf8 !important; margin-top: 10px !important; }
    h4 { font-size: 1.10rem !important; font-weight: 600 !important; color: #f1f5f9 !important; }
    h5 { font-size: 0.98rem !important; font-weight: 600 !important; color: #cbd5e1 !important; }
    
    /* Legendas e Textos Explicativos */
    .stCaption, [data-testid="stCaptionContainer"] {
        font-size: 0.88rem !important;
        color: #94a3b8 !important;
        line-height: 1.45 !important;
    }

    /* Labels de Inputs e Formulários */
    label, [data-testid="stWidgetLabel"] p {
        font-size: 0.90rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
    }

    /* Header de Telemetria Superior Estilo Rig Control Room */
    .rig-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, #111827 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .rig-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .rig-badge {
        background-color: #0f172a;
        border: 1px solid #0284c7;
        color: #38bdf8;
        padding: 3px 9px;
        border-radius: 4px;
        font-size: 0.76rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .rig-status {
        display: flex;
        align-items: center;
        gap: 14px;
        font-size: 0.82rem;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-dot {
        height: 9px;
        width: 9px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #10b981;
    }

    /* Container de Abas Profissional */
    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        color: #94a3b8 !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.2s ease-in-out;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
        background-color: rgba(56, 189, 248, 0.06) !important;
        border-radius: 6px 6px 0 0;
    }

    /* Cartões e Containers */
    [data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 16px;
    }

    /* Métricas Digitais */
    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        color: #94a3b8 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #f8fafc !important;
    }

    /* Botões */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        border: 1px solid #38bdf8;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.92rem;
        border-radius: 6px;
        padding: 8px 16px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        border-color: #7dd3fc;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização da Session State para o banco de aditivos
if 'aditivos_db' not in st.session_state:
    st.session_state.aditivos_db = AditivoService.inicializar_banco()

# Cabeçalho Superior Estilo Sala de Controle OpenLab
st.markdown("""
<div class="rig-header">
    <div class="rig-title">
        <span>🛢️ CEMENTING SIMULATOR & ENGINEERING SUITE</span>
        <span class="rig-badge">API SPEC 10A / 10B</span>
        <span class="rig-badge">HYDRAULIC CORE v2.4</span>
    </div>
    <div class="rig-status">
        <span><span class="status-dot"></span> SIMULATOR READY</span>
        <span>|</span>
        <span>UNITS: OILFIELD (US/API)</span>
        <span>|</span>
        <span>BOURGOYNE ET AL. COMPLIANT</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4 Abas Principais de Engenharia
tab_poco, tab_pastas, tab_ia, tab_resultados = st.tabs([
    "📐 1. Geometria & Banco de Aditivos",
    "🧪 2. Configuração das Pastas",
    "🧠 3. Módulo Especialista de Formulação",
    "📊 4. Telemetria, Dashboard & Ficha de Traço"
])

# 1. Aba de Parâmetros do Poço e Gestão de Aditivos
with tab_poco:
    params_poco, aditivos_db = render_parametros_poco(st.session_state.aditivos_db)

# 2. Aba de Configuração das Pastas
with tab_pastas:
    pastas_config = render_config_pastas(aditivos_db)

# 3. Processamento dos Cálculos do Motor de Cimentação
resultados_finais = processar_calculos_pastas(
    pastas_config=pastas_config,
    aditivos_db=aditivos_db,
    d_broca=params_poco['d_broca'],
    d_ext=params_poco['d_ext'],
    d_int=params_poco['d_int'],
    fator_excesso=params_poco['fator_excesso'],
    dist_sapata=params_poco['dist_sapata']
)

# 4. Aba do Agente de IA Especialista
with tab_ia:
    render_tab_agente_ia(aditivos_db=aditivos_db, total_pastas=len(pastas_config))

# 5. Aba de Resultados e Gráficos
with tab_resultados:
    render_dashboard(resultados_finais, params_poco)
    render_analise_individual(resultados_finais)
