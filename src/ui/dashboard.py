"""
Componente visual de Telemetria e Dashboard — Estilo OpenLab Drilling (NORCE).
Layout balanceado, tipografia de alta legibilidade, Esquemático 2D Didático e Janela Geomecânica com Auditoria Rigorosa de Toda a Coluna.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional, Tuple

PLOTLY_CONFIG_INTERATIVO = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'height': 900,
        'width': 1400,
        'scale': 2
    },
    'responsive': True
}

def _gerar_perfil_escada_fluidos(
    z_max: float,
    z_toc: float,
    pastas_topo_base: List[Dict[str, Any]],
    dens_lama: float,
    sapatas_meta: Optional[List[Dict[str, Any]]] = None,
    lda_ft: float = 0.0,
    fator_escala_alturas: float = 1.0
) -> Tuple[List[float], List[float], List[Dict[str, Any]]]:
    """
    Gera coordenadas (x=densidade_ppg, y=profundidade_ft) em formato de degraus ortogonais (step-plot)
    representando o programa de fluidos e pastas (Safe Mud Weight) em cada cota do poço,
    acompanhando as sapatas históricas (casing points) e as pastas de cimento na base.
    """
    x_step: List[float] = []
    y_step: List[float] = []
    casing_points: List[Dict[str, Any]] = []

    z_start = lda_ft if lda_ft > 0 and lda_ft < z_toc * 0.5 else 0.0

    # 1. Fases de Revestimento Acima do TOC (20" Condutor/Superfície -> 13 3/8" Intermediário no TOC)
    if z_toc > 1500.0:
        # Se for perfil do Mar do Norte (ex: 15/9-13 com TD ~ 3260m = 10695ft), posiciona Sapata 20" em 718m (2355.6 ft) ou proporcional
        if abs(z_max - 10695.5) < 250.0:
            z_sapata_20 = min(718.0 * 3.28084, z_toc * 0.65)
            z_sapata_958 = 2701.0 * 3.28084
        elif sapatas_meta and len(sapatas_meta) > 0:
            s0_ft = float(sapatas_meta[0].get("sapata_m", 500.0)) * 3.28084
            z_sapata_20 = min(max(s0_ft, z_start + 300.0), z_toc * 0.65)
            s_ult_ft = float(sapatas_meta[-1].get("sapata_m", 2623.0)) * 3.28084
            z_sapata_958 = min(max(s_ult_ft, z_toc + 500.0), z_max - 200.0)
        else:
            z_sapata_20 = round(z_toc * 0.39, 1)
            z_sapata_958 = round(z_max * 0.83, 1)

        dens_fase1 = max(9.00, round(dens_lama - 1.84, 2))

        # Fase 1: Condutor / Superfície 20" (de z_start até z_sapata_20)
        x_step.extend([dens_fase1, dens_fase1])
        y_step.extend([z_start, z_sapata_20])
        casing_points.append({
            "prof_ft": z_sapata_20,
            "diam": '20"',
            "densidade": dens_fase1
        })

        # Fase 2: Revestimento Intermediário 13 3/8" (de z_sapata_20 até z_toc)
        x_step.extend([dens_lama, dens_lama])
        y_step.extend([z_sapata_20, z_toc])
        casing_points.append({
            "prof_ft": z_toc,
            "diam": '13 3/8"',
            "densidade": dens_lama
        })
    elif z_toc > 0:
        x_step.extend([dens_lama, dens_lama])
        y_step.extend([z_start, z_toc])
        casing_points.append({
            "prof_ft": z_toc,
            "diam": '13 3/8"',
            "densidade": dens_lama
        })
        z_sapata_958 = round(z_max * 0.83, 1)
    else:
        x_step.append(dens_lama)
        y_step.append(z_start)
        z_sapata_958 = round(z_max * 0.83, 1)

    # 2. Intervalos de Pastas de Cimento (do TOC até o fundo do poço)
    z_cursor = z_toc
    for idx, p in enumerate(pastas_topo_base):
        dens_p = float(p.get("densidade", 15.80))
        h_p = float(p.get("altura", 500.0)) * fator_escala_alturas
        z_prox = z_max if idx == len(pastas_topo_base) - 1 else min(z_cursor + h_p, z_max)

        # Salto horizontal ortogonal na interface entre fluidos
        if len(x_step) > 0 and abs(x_step[-1] - dens_p) > 0.001:
            x_step.append(dens_p)
            y_step.append(z_cursor)

        x_step.extend([dens_p, dens_p])
        y_step.extend([z_cursor, z_prox])
        z_cursor = z_prox

    # Se sobrar intervalo até a base
    if z_cursor < z_max and len(x_step) > 0:
        x_step.extend([x_step[-1], x_step[-1]])
        y_step.extend([z_cursor, z_max])

    # Sapata de Revestimento de Produção 9 5/8" na seção inferior (ex: 2.701 m no poço 15/9-13)
    if z_sapata_958 > z_toc + 200.0 and z_sapata_958 < z_max - 100.0:
        dens_na_sapata = x_step[-1] if len(x_step) > 0 else 15.80
        casing_points.append({
            "prof_ft": z_sapata_958,
            "diam": '9 5/8"',
            "densidade": dens_na_sapata
        })

    return x_step, y_step, casing_points


@st.dialog("🛡️ Janela Geomecânica & Curvas de Pressão em Tela Cheia", width="large")
def _exibir_dialog_janela_geomecanica(
    fig: go.Figure,
    badge_html: Optional[str] = None,
    fonte: Optional[str] = None,
    min_m_poro: Optional[float] = None,
    min_m_frac: Optional[float] = None
):
    c_m1, c_m2, c_m3 = st.columns([1.5, 1, 1])
    with c_m1:
        st.markdown(f"**Perfil Geomecânico:** `{fonte or 'Perfil Analítico'}`")
    with c_m2:
        if min_m_poro is not None:
            cor_p = "#10b981" if min_m_poro >= 0 else "#ef4444"
            st.markdown(f"Margem Mín. Poro: <b style='color:{cor_p}'>{'+' if min_m_poro>=0 else ''}{min_m_poro:.2f} ppg</b>", unsafe_allow_html=True)
    with c_m3:
        if min_m_frac is not None:
            cor_f = "#10b981" if min_m_frac >= 0 else "#ef4444"
            st.markdown(f"Margem Mín. Fratura: <b style='color:{cor_f}'>{'+' if min_m_frac>=0 else ''}{min_m_frac:.2f} ppg</b>", unsafe_allow_html=True)

    if badge_html:
        st.html(badge_html)

    fig_full = go.Figure(fig)
    fig_full.update_layout(
        height=720,
        margin=dict(l=60, r=30, t=20, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.14,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color="#cbd5e1")
        )
    )
    st.plotly_chart(fig_full, width="stretch", config=PLOTLY_CONFIG_INTERATIVO)
    st.caption("💡 *Dica:* Utilize as ferramentas na barra superior do gráfico para aplicar zoom retangular em seções críticas (gargalos), mover a curva (pan) ou exportar a imagem em alta resolução (PNG 300 DPI).")


@st.dialog("📐 Esquemático 2D do Poço em Tela Cheia", width="large")
def _exibir_dialog_esquematico(fig: go.Figure, titulo: str = "Esquemático 2D do Poço"):
    st.markdown(f"##### {titulo}")
    fig_full = go.Figure(fig)
    fig_full.update_layout(
        height=750,
        margin=dict(l=70, r=70, t=20, b=40)
    )
    st.plotly_chart(fig_full, width="stretch", config=PLOTLY_CONFIG_INTERATIVO)
    st.caption("💡 *Dica:* Use o zoom e a barra de ferramentas do Plotly para inspecionar as cotas das camadas, a folga anular e a sapata de revestimento.")


def render_dashboard(resultados_finais: List[Dict[str, Any]], params_poco: Optional[Dict[str, float]] = None):
    """
    Renderiza o painel de telemetria com cartões digitais SCADA via st.html, esquemático 2D e janela de pressão.
    """
    if not resultados_finais:
        st.warning("⚠️ Nenhuma pasta calculada para exibição.")
        return

    params_poco = params_poco or {
        'd_broca': 17.00, 'd_ext': 13.375, 'd_int': 12.415, 'fator_excesso': 1.75, 'dist_sapata': 40.0, 'dens_lama': 9.50
    }

    # Cálculos Globais Consolidados
    total_sacos_poco = sum(r['sacos'] for r in resultados_finais)
    total_volume_ft3 = sum(r['volume'] for r in resultados_finais)
    total_volume_bbl = total_volume_ft3 / 5.615
    total_altura_ft = sum(r['altura'] for r in resultados_finais)
    total_p_hid_psi = sum(r.get('pressao_hidrostatica', 0.0) for r in resultados_finais)
    densidade_media_ppg = (total_p_hid_psi / (0.052 * total_altura_ft)) if total_altura_ft > 0 else 0.0

    st.markdown("### 🛢️ Telemetria Hidrostática & Indicadores Operacionais")
    st.caption("Leituras em tempo real dos parâmetros hidrostáticos e volumétricos do poço:")

    # 1. Cartões de Telemetria Digital de Alto Contraste (Estilo SCADA / OpenLab) renderizados via st.html
    pct_p_hid = min(max((total_p_hid_psi / 5000.0) * 100, 5), 100)
    pct_emw = min(max(((densidade_media_ppg - 8.33) / (18.0 - 8.33)) * 100, 5), 100)
    pct_vol = min(max((total_volume_bbl / 500.0) * 100, 5), 100)
    pct_sacos = min(max((total_sacos_poco / 1500.0) * 100, 5), 100)

    html_cards = f"""
<style>
/* Forçar segmented_control do esquemático a ficar sempre horizontal, sem empilhar */
div[data-testid="stSegmentedControl"] {{
    width: 100% !important;
}}
div[data-testid="stSegmentedControl"] > div {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 4px !important;
    align-items: center !important;
    justify-content: stretch !important;
}}
div[data-testid="stSegmentedControl"] button {{
    flex: 1 1 0 !important;
    white-space: nowrap !important;
    font-size: 0.80rem !important;
    font-weight: 500 !important;
    padding: 3px 6px !important;
    min-height: 36px !important;
    height: 36px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
/* Alinhamento uniforme dos botões de Tela Cheia */
div[data-testid="stButton"] > button {{
    height: 36px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
/* Alinhamento do Toggle da Janela Geomecânica */
div[data-testid="stToggle"] {{
    min-height: 36px !important;
    height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
}}
</style>
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; width: 100%;">
    <!-- Card 1: Pressão Hidrostática -->
    <div style="background: #111827; border: 1px solid #1f2937; border-left: 4px solid #38bdf8; border-radius: 8px; padding: 14px 16px; box-sizing: border-box;">
        <div style="font-size: 0.80rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">
            PRESSÃO HIDROSTÁTICA
        </div>
        <div style="font-size: 0.72rem; color: #64748b; margin-bottom: 6px;">Fundo do Poço (Bottomhole)</div>
        <div style="display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.80rem; font-weight: 700; color: #38bdf8; line-height: 1;">{total_p_hid_psi:,.1f}</span>
            <span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8;">psi</span>
        </div>
        <div style="background: #1e293b; border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #0284c7, #38bdf8); height: 100%; width: {pct_p_hid:.0f}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.70rem; color: #64748b; margin-top: 5px; font-family: 'JetBrains Mono';">
            <span>0 psi</span>
            <span>Grad: {total_p_hid_psi/max(total_altura_ft,1):.2f} psi/ft</span>
            <span>5.000 psi</span>
        </div>
    </div>

    <!-- Card 2: Densidade Média Equivalente -->
    <div style="background: #111827; border: 1px solid #1f2937; border-left: 4px solid #10b981; border-radius: 8px; padding: 14px 16px; box-sizing: border-box;">
        <div style="font-size: 0.80rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">
            DENSIDADE EQUIVALENTE
        </div>
        <div style="font-size: 0.72rem; color: #64748b; margin-bottom: 6px;">Coluna de Cimento (EMW)</div>
        <div style="display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.80rem; font-weight: 700; color: #10b981; line-height: 1;">{densidade_media_ppg:.2f}</span>
            <span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8;">ppg</span>
        </div>
        <div style="background: #1e293b; border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #059669, #10b981); height: 100%; width: {pct_emw:.0f}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.70rem; color: #64748b; margin-top: 5px; font-family: 'JetBrains Mono';">
            <span>8.33 ppg (Água)</span>
            <span>SG: {densidade_media_ppg/8.33:.2f}</span>
            <span>18.0 ppg</span>
        </div>
    </div>

    <!-- Card 3: Volume Total da Calda -->
    <div style="background: #111827; border: 1px solid #1f2937; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 14px 16px; box-sizing: border-box;">
        <div style="font-size: 0.80rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">
            VOLUME TOTAL CALDA
        </div>
        <div style="font-size: 0.72rem; color: #64748b; margin-bottom: 6px;">Anular + Sapata (ft³ / bbl)</div>
        <div style="display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.80rem; font-weight: 700; color: #f59e0b; line-height: 1;">{total_volume_bbl:,.1f}</span>
            <span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8;">bbl</span>
        </div>
        <div style="background: #1e293b; border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #d97706, #f59e0b); height: 100%; width: {pct_vol:.0f}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.70rem; color: #64748b; margin-top: 5px; font-family: 'JetBrains Mono';">
            <span>0 bbl</span>
            <span>{total_volume_ft3:,.1f} ft³</span>
            <span>500 bbl</span>
        </div>
    </div>

    <!-- Card 4: Sacos de Cimento -->
    <div style="background: #111827; border: 1px solid #1f2937; border-left: 4px solid #a855f7; border-radius: 8px; padding: 14px 16px; box-sizing: border-box;">
        <div style="font-size: 0.80rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">
            TOTAL DE SACOS
        </div>
        <div style="font-size: 0.72rem; color: #64748b; margin-bottom: 6px;">Cimento Seco (94 lb / sk)</div>
        <div style="display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.80rem; font-weight: 700; color: #a855f7; line-height: 1;">{total_sacos_poco:,}</span>
            <span style="font-size: 0.95rem; font-weight: 600; color: #94a3b8;">sk</span>
        </div>
        <div style="background: #1e293b; border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #7e22ce, #a855f7); height: 100%; width: {pct_sacos:.0f}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.70rem; color: #64748b; margin-top: 5px; font-family: 'JetBrains Mono';">
            <span>0 sk</span>
            <span>{(total_sacos_poco*94.0)/2204.62:.1f} t métricas</span>
            <span>1.500 sk</span>
        </div>
    </div>
</div>
"""
    st.html(html_cards)

    # 2. Painel Duplo: Esquemático 2D + Janela de Pressão Operacional
    col_well_schema, col_press_window = st.columns([1.15, 1.25], gap="large")

    # --- ESQUEMÁTICO 2D DO POÇO COM SELETOR DE MODO (DIDÁTICO vs REAL) ---
    with col_well_schema:
        c_tit_sch, c_btn_sch = st.columns([2.2, 1.0], vertical_alignment="center")
        with c_tit_sch:
            st.markdown("#### 📐 Esquemático 2D")
        with c_btn_sch:
            btn_tela_cheia_sch = st.button("⛶ Tela Cheia", key="btn_modal_schema", help="Visualizar esquemático 2D em tela cheia com alta resolução.", use_container_width=True)

        c_sub_sch, c_mode_sch = st.columns([1.1, 1.3], vertical_alignment="center")
        with c_sub_sch:
            st.caption("Distribuição no anular e sapata:")
        with c_mode_sch:
            modo_escala = st.segmented_control(
                "Modo de Escala",
                options=["📘 Didático", "📏 Escala Real"],
                default="📘 Didático",
                key="seg_modo_escala_schema",
                label_visibility="collapsed"
            )
            if not modo_escala:
                modo_escala = "📘 Didático"

        cores_pastas = ["#f59e0b", "#38bdf8", "#10b981", "#ec4899", "#8b5cf6"]

        fig_schema = go.Figure()

        # Profundidades acumuladas
        alturas = [r['altura'] for r in resultados_finais]
        prof_base = sum(alturas)
        h_sapata = params_poco.get('dist_sapata', 40.0)

        # Configuração dimensional horizontal e vertical
        if modo_escala.startswith("📘 Didático"):
            r_hole = 4.0
            r_casing_od = 2.0
            r_casing_id = 1.5
            x_lim = 10.5
            show_xaxis = False

            # No modo didático, a sapata recebe proporção visual destacada
            h_pasta_1 = resultados_finais[0]['altura'] if resultados_finais else 500.0
            visual_h_sapata = max(h_sapata, h_pasta_1 * 0.25, prof_base * 0.10)
            y_colar_visual = prof_base - visual_h_sapata
        else:
            r_hole = params_poco['d_broca'] / 2.0
            r_casing_od = params_poco['d_ext'] / 2.0
            r_casing_id = params_poco['d_int'] / 2.0
            x_lim = r_hole * 1.6
            show_xaxis = True
            visual_h_sapata = h_sapata
            y_colar_visual = max(prof_base - h_sapata, 0)

        # Inverte a ordem para desenhar do topo para a base (Pasta N no topo, Pasta 1 no fundo)
        pastas_ordenadas_topo_base = list(reversed(resultados_finais))

        prof_atual = 0.0
        for idx, r in enumerate(pastas_ordenadas_topo_base):
            cor = cores_pastas[(r['numero'] - 1) % len(cores_pastas)]
            h = r['altura']
            nome_p = f"Pasta {r['numero']} (Classe {r.get('classe', 'G')})"
            y_top = prof_atual
            y_bottom = prof_atual + h

            # Anular Esquerdo: [-r_hole, -r_casing_od]
            fig_schema.add_shape(
                type="rect",
                x0=-r_hole, x1=-r_casing_od,
                y0=y_top, y1=y_bottom,
                fillcolor=cor, line=dict(color="#0f172a", width=1.5),
                layer="below"
            )
            # Anular Direito: [+r_casing_od, +r_hole]
            fig_schema.add_shape(
                type="rect",
                x0=r_casing_od, x1=r_hole,
                y0=y_top, y1=y_bottom,
                fillcolor=cor, line=dict(color="#0f172a", width=1.5),
                layer="below"
            )

            # Traço invisível para Hover descritivo
            fig_schema.add_trace(go.Scatter(
                x=[0], y=[(y_top + y_bottom) / 2],
                mode='markers',
                marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                hoverinfo='text',
                hovertext=f"<b>{nome_p}</b><br>Densidade: {r['densidade']:.2f} ppg<br>Intervalo: {y_top:.0f} ft a {y_bottom:.0f} ft<br>Altura: {h:.0f} ft | Sacos: {r['sacos']} sk",
                showlegend=False
            ))

            # No modo didático, adiciona cota vertical com setas e texto à esquerda (estilo slide Profa. Nara)
            if modo_escala == "📘 Didático (Visão Clara)":
                x_cota_esq = -r_hole - 0.7
                y_mid = (y_top + y_bottom) / 2
                
                fig_schema.add_shape(
                    type="line",
                    x0=x_cota_esq, x1=x_cota_esq,
                    y0=y_top, y1=y_bottom,
                    line=dict(color="#94a3b8", width=1.5)
                )
                fig_schema.add_shape(
                    type="line",
                    x0=x_cota_esq - 0.25, x1=x_cota_esq + 0.25,
                    y0=y_top, y1=y_top,
                    line=dict(color="#94a3b8", width=1.5)
                )
                fig_schema.add_shape(
                    type="line",
                    x0=x_cota_esq - 0.25, x1=x_cota_esq + 0.25,
                    y0=y_bottom, y1=y_bottom,
                    line=dict(color="#94a3b8", width=1.5)
                )

                fig_schema.add_annotation(
                    x=x_cota_esq - 0.35,
                    y=y_mid,
                    text=f"<b>{h:,.0f} ft</b><br><span style='font-size:0.80em;color:#94a3b8;'>P{r['numero']} ({r.get('classe','G')})</span>",
                    showarrow=False,
                    font=dict(size=12, color="#f8fafc", family="JetBrains Mono"),
                    xanchor="right"
                )

            prof_atual += h

        # 2. Paredes de Aço do Revestimento (Casing Walls)
        fig_schema.add_shape(
            type="rect",
            x0=-r_casing_od, x1=-r_casing_id,
            y0=0, y1=prof_base,
            fillcolor="#475569", line=dict(color="#1e293b", width=1.5)
        )
        fig_schema.add_shape(
            type="rect",
            x0=r_casing_id, x1=r_casing_od,
            y0=0, y1=prof_base,
            fillcolor="#475569", line=dict(color="#1e293b", width=1.5)
        )

        # 3. Interior do Revestimento (Fluido de Deslocamento / Lama acima do Colar)
        fig_schema.add_shape(
            type="rect",
            x0=-r_casing_id, x1=r_casing_id,
            y0=0, y1=y_colar_visual,
            fillcolor="#0f172a", line=dict(color="rgba(0,0,0,0)")
        )

        # 4. Bolsão de Cimento da Sapata (Shoe Track: entre Colar e Sapata)
        cor_sapata = cores_pastas[0]  # Cor da Pasta 1 (Sapata)
        fig_schema.add_shape(
            type="rect",
            x0=-r_casing_id, x1=r_casing_id,
            y0=y_colar_visual, y1=prof_base,
            fillcolor=cor_sapata, line=dict(color="#0f172a", width=1.5)
        )

        # Desenho da Válvula / Colar Flutuador
        fig_schema.add_shape(
            type="rect",
            x0=-r_casing_id * 0.95, x1=r_casing_id * 0.95,
            y0=y_colar_visual - (visual_h_sapata * 0.12), y1=y_colar_visual,
            fillcolor="#1e293b", line=dict(color="#64748b", width=1.5)
        )

        # Linhas de referência horizontais locais
        fig_schema.add_shape(
            type="line",
            x0=-r_casing_id, x1=r_hole + (1.2 if modo_escala == "📘 Didático (Visão Clara)" else 0.5),
            y0=y_colar_visual, y1=y_colar_visual,
            line=dict(color="#f59e0b", width=1.5, dash="dot")
        )

        fig_schema.add_shape(
            type="line",
            x0=-r_hole, x1=r_hole + (1.2 if modo_escala == "📘 Didático (Visão Clara)" else 0.5),
            y0=prof_base, y1=prof_base,
            line=dict(color="#ef4444", width=2)
        )

        # Cotas do Bolsão de Sapata e Rótulos à Direita
        if modo_escala == "📘 Didático (Visão Clara)":
            x_cota_dir = r_hole + 1.2
            y_mid_sapata = (y_colar_visual + prof_base) / 2

            fig_schema.add_shape(
                type="line",
                x0=x_cota_dir, x1=x_cota_dir,
                y0=y_colar_visual, y1=prof_base,
                line=dict(color="#f59e0b", width=1.5)
            )
            fig_schema.add_shape(
                type="line",
                x0=x_cota_dir - 0.25, x1=x_cota_dir + 0.25,
                y0=y_colar_visual, y1=y_colar_visual,
                line=dict(color="#f59e0b", width=1.5)
            )
            fig_schema.add_shape(
                type="line",
                x0=x_cota_dir - 0.25, x1=x_cota_dir + 0.25,
                y0=prof_base, y1=prof_base,
                line=dict(color="#f59e0b", width=1.5)
            )

            fig_schema.add_annotation(
                x=x_cota_dir + 0.35,
                y=y_mid_sapata,
                text=f"<b>{h_sapata:,.0f} ft</b><br><span style='font-size:0.78em;color:#f59e0b;'>Sapata-Colar</span>",
                showarrow=False,
                font=dict(size=12, color="#f8fafc", family="JetBrains Mono"),
                xanchor="left"
            )

            fig_schema.add_annotation(
                x=x_cota_dir + 0.35,
                y=y_colar_visual,
                text=f"<b>Colar:</b> {prof_base - h_sapata:,.0f} ft",
                showarrow=False,
                font=dict(size=11, color="#f59e0b", family="JetBrains Mono"),
                xanchor="left",
                yanchor="bottom"
            )

            fig_schema.add_annotation(
                x=x_cota_dir + 0.35,
                y=prof_base,
                text=f"<b>Sapata:</b> {prof_base:,.0f} ft",
                showarrow=False,
                font=dict(size=11, color="#ef4444", family="JetBrains Mono"),
                xanchor="left",
                yanchor="top"
            )

            fig_schema.add_annotation(
                x=0, y=prof_base + (prof_base * 0.09),
                text=f"<b>DI: {params_poco['d_int']:.3f}\"</b>  │  <b>DE: {params_poco['d_ext']:.3f}\"</b>  │  <b>D_poço: {params_poco['d_broca']:.3f}\"</b>",
                showarrow=False,
                font=dict(size=11, color="#94a3b8", family="JetBrains Mono")
            )
            y_range_max = prof_base * 1.15
        else:
            fig_schema.add_annotation(
                x=r_hole + 0.8,
                y=y_colar_visual,
                text=f"Colar ({prof_base - h_sapata:.0f} ft)",
                showarrow=False,
                font=dict(size=10, color="#f59e0b", family="JetBrains Mono"),
                xanchor="left"
            )
            fig_schema.add_annotation(
                x=r_hole + 0.8,
                y=prof_base,
                text=f"Sapata ({prof_base:.0f} ft)",
                showarrow=False,
                font=dict(size=10, color="#ef4444", family="JetBrains Mono"),
                xanchor="left"
            )
            y_range_max = prof_base * 1.05

        fig_schema.update_layout(
            height=490,
            yaxis=dict(
                autorange="reversed",
                title="Profundidade Medida (MD em ft)",
                title_font=dict(size=13, color="#94a3b8"),
                tickfont=dict(size=12, family="JetBrains Mono", color="#cbd5e1"),
                gridcolor="#1e293b",
                range=[y_range_max, -prof_base * 0.03],
                zeroline=False
            ),
            xaxis=dict(
                visible=show_xaxis,
                title="Raio do Poço (polegadas)" if show_xaxis else "",
                title_font=dict(size=12, color="#94a3b8"),
                range=[-x_lim, x_lim],
                tickvals=[-r_hole, -r_casing_od, 0, r_casing_od, r_hole] if show_xaxis else [],
                ticktext=[f"-{r_hole:.1f}\"", f"-{r_casing_od:.1f}\"", "0", f"+{r_casing_od:.1f}\"", f"+{r_hole:.1f}\""] if show_xaxis else [],
                tickfont=dict(size=10, family="JetBrains Mono", color="#94a3b8"),
                gridcolor="#1e293b",
                zerolinecolor="#334155"
            ),
            margin=dict(l=80, r=90 if modo_escala.startswith("📘 Didático") else 40, t=20, b=35),
            paper_bgcolor="#111827",
            plot_bgcolor="#0b0f19"
        )

        st.plotly_chart(fig_schema, width="stretch", config=PLOTLY_CONFIG_INTERATIVO)

        if btn_tela_cheia_sch:
            _exibir_dialog_esquematico(fig_schema, f"Esquemático 2D do Poço ({modo_escala})")

    # --- JANELA DE PRESSÃO OPERACIONAL (SINCRONIZADA COM A GEOMECÂNICA DA ABA 3) ---
    with col_press_window:
        perfil_real_df = st.session_state.get('perfil_geomecanico_ativo', None)
        fonte_geomec = st.session_state.get('fonte_geomecanica_ativa', 'Perfil Ativo')

        c_tit_pw, c_btn_pw = st.columns([2.2, 1.0], vertical_alignment="center")
        with c_tit_pw:
            st.markdown("#### 🛡️ Janela Geomecânica")
        with c_btn_pw:
            btn_tela_cheia_janela = st.button("⛶ Tela Cheia", key="btn_modal_janela", help="Visualizar a janela geomecânica e EMW em tela cheia com alta resolução.", use_container_width=True)

        if perfil_real_df is not None:
            c_sub_pw, c_unid_pw, c_tog_pw = st.columns([1.25, 1.15, 0.90], vertical_alignment="center")
            with c_sub_pw:
                st.caption(f"Perfil: **{fonte_geomec}**" if st.session_state.get("tog_curvas_reais_dash", True) else "Perfil analítico (Aba 3):")
            with c_unid_pw:
                unid_prof_janela = st.segmented_control(
                    "Unidade Vertical",
                    options=["📏 Metros (m)", "📐 Pés (ft)"],
                    default="📏 Metros (m)",
                    key="seg_unid_prof_janela",
                    label_visibility="collapsed"
                )
                if not unid_prof_janela:
                    unid_prof_janela = "📏 Metros (m)"
            with c_tog_pw:
                usar_curvas_reais = st.toggle("🌐 Curvas Reais", value=True, key="tog_curvas_reais_dash")
        else:
            usar_curvas_reais = False
            c_sub_pw, c_unid_pw = st.columns([1.6, 1.1], vertical_alignment="center")
            with c_sub_pw:
                st.caption("Perfil dinâmico da coluna hidrostática versus limites geomecânicos (Aba 3):")
            with c_unid_pw:
                unid_prof_janela = st.segmented_control(
                    "Unidade Vertical",
                    options=["📏 Metros (m)", "📐 Pés (ft)"],
                    default="📏 Metros (m)",
                    key="seg_unid_prof_janela",
                    label_visibility="collapsed"
                )
                if not unid_prof_janela:
                    unid_prof_janela = "📏 Metros (m)"

        usar_metros = unid_prof_janela.startswith("📏")
        fator_y = 0.3048 if usar_metros else 1.0
        unid_lbl = "m" if usar_metros else "ft"

        # Gradientes da formação configurados no Módulo Especialista (Aba 3)
        grad_poro_alvo = float(st.session_state.get('ia_poro', 10.20))
        grad_frac_alvo = float(st.session_state.get('ia_frac', 16.80))
        grad_poro_topo = min(grad_poro_alvo, 9.00)
        grad_frac_topo = max(grad_frac_alvo - 1.0, 14.50)
        dens_lama = params_poco.get('dens_lama', 9.50)

        if usar_curvas_reais and perfil_real_df is not None:
            # ── MODO 1: CURVAS REAIS CONTÍNUAS DO PERFIL GEOMECÂNICO ──
            prof_reais_ft = perfil_real_df["prof_ft"].values
            z_max = float(np.nanmax(prof_reais_ft)) if len(prof_reais_ft) > 0 else 1000.0

            frac_curve = perfil_real_df["fratura_ppg"].values
            poro_curve = perfil_real_df["poro_ppg"].values
            colapso_curve = perfil_real_df["colapso_ppg"].values if "colapso_ppg" in perfil_real_df.columns else None
            sobrecarga_curve = perfil_real_df["sobrecarga_ppg"].values if "sobrecarga_ppg" in perfil_real_df.columns else None
            lim_inf_curve = perfil_real_df["limite_inferior_ppg"].values if "limite_inferior_ppg" in perfil_real_df.columns else poro_curve
            depth_steps = prof_reais_ft
            lama_curve = np.full_like(depth_steps, dens_lama)

            # Salvaguarda automática de escala: se as alturas somadas forem < 25% do poço (ex: digitadas em metros ~1460 em vez de ~4700 ft),
            # aplica conversão métrica (x 3.28084) para posicionar o TOC na sapata intermediária real (~1.827 m / 5.994 ft)
            if z_max > 6500.0 and total_altura_ft < z_max * 0.25 and (total_altura_ft * 3.28084) <= z_max * 0.75:
                fator_escala_alturas = 3.28084
            else:
                fator_escala_alturas = 1.0

            altura_cimento_plot_ft = total_altura_ft * fator_escala_alturas
            z_toc = max(0.0, z_max - altura_cimento_plot_ft)
            pastas_topo_base = list(reversed(resultados_finais))

            emw_curve = []
            for z in depth_steps:
                if z <= 0:
                    emw_curve.append(dens_lama)
                elif z <= z_toc:
                    emw_curve.append(dens_lama)
                else:
                    p_acum_psi = 0.052 * dens_lama * z_toc
                    z_layer_top = z_toc
                    for p in pastas_topo_base:
                        h = p['altura'] * fator_escala_alturas
                        z_layer_bottom = z_layer_top + h
                        if z <= z_layer_top:
                            break
                        dz = min(z, z_layer_bottom) - z_layer_top
                        p_acum_psi += 0.052 * p['densidade'] * dz
                        z_layer_top = z_layer_bottom
                    emw_val = p_acum_psi / (0.052 * z)
                    emw_curve.append(emw_val)
            emw_curve = np.array(emw_curve)

            # Auditoria contra limites reais
            valid_frac = ~np.isnan(frac_curve)
            valid_inf = ~np.isnan(lim_inf_curve)
            diff_frac = frac_curve[valid_frac] - emw_curve[valid_frac] if valid_frac.sum() > 0 else np.array([1.0])
            diff_poro = emw_curve[valid_inf] - lim_inf_curve[valid_inf] if valid_inf.sum() > 0 else np.array([1.0])

            min_margem_frac = float(np.nanmin(diff_frac)) if len(diff_frac) else 0.0
            min_margem_poro = float(np.nanmin(diff_poro)) if len(diff_poro) else 0.0

            if min_margem_frac < 0:
                idx_viol = np.where(frac_curve - emw_curve < 0)[0]
                z_ini = depth_steps[idx_viol[0]] * fator_y
                z_fim = depth_steps[idx_viol[-1]] * fator_y
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE FRATURA REAL:</b> EMW excede a fratura de campo entre <b>{z_ini:,.0f} {unid_lbl} e {z_fim:,.0f} {unid_lbl}</b> (excesso de até <b>{abs(min_margem_frac):.2f} ppg</b>).
                    <br><span style="font-size: 0.78rem; color: #cbd5e1;">💡 <i>Ajuste operacional:</i> Reduza a densidade da pasta de topo (Lead) ou diminua a altura da coluna de cimento.</span>
                </div>"""
            elif min_margem_poro < 0:
                idx_viol = np.where(emw_curve - lim_inf_curve < 0)[0]
                z_ini = depth_steps[idx_viol[0]] * fator_y
                z_fim = depth_steps[idx_viol[-1]] * fator_y
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE INSTABILIDADE/KICK:</b> EMW abaixo do limite inferior (Poro/Colapso) entre <b>{z_ini:,.0f} {unid_lbl} e {z_fim:,.0f} {unid_lbl}</b> (déficit de até <b>{abs(min_margem_poro):.2f} ppg</b>).
                </div>"""
            else:
                badge_html = f"""<div style="background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #a7f3d0; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between;">
                    <span><b>🟢 COLUNA 100% CONFORME COM PERFIL REAL</b> ({fonte_geomec})</span>
                    <span>Margem Mín. Poro/Colapso: <b>+{min_margem_poro:.2f} ppg</b> │ Fratura: <b>+{min_margem_frac:.2f} ppg</b></span>
                </div>"""
            st.html(badge_html)

            meta_ativo = st.session_state.get("metadados_geomecanicos_ativos", {})
            sapatas_meta = meta_ativo.get("sapatas", []) if meta_ativo else []
            lda_ft = float(meta_ativo.get("lda_ft", 0.0)) if meta_ativo else 0.0
            max_x_val = 19.2

            y_plot = depth_steps * fator_y
            lda_plot = lda_ft * fator_y

            fig_window = go.Figure()

            # Faixa de Lâmina d'Água (Water Depth) no topo
            if lda_plot > 0:
                fig_window.add_hrect(
                    y0=0, y1=lda_plot,
                    fillcolor="rgba(56, 189, 248, 0.22)",
                    line_width=1,
                    line_color="rgba(56, 189, 248, 0.45)",
                    annotation_text=f"🌊 Lâmina d'Água (LDA = {lda_plot:.0f} {unid_lbl})",
                    annotation_position="top left",
                    annotation_font=dict(color="#38bdf8", size=10, family="JetBrains Mono")
                )

            # Preenchimento do Corredor Seguro Real (Janela Operacional Segura)
            if lim_inf_curve is not None and not np.all(np.isnan(lim_inf_curve)):
                lim_inf_clipped = np.clip(lim_inf_curve, 6.5, 20.0)
                fig_window.add_trace(go.Scatter(
                    x=lim_inf_clipped, y=y_plot, mode='lines',
                    line=dict(color='rgba(239, 68, 68, 0.0)', width=0.5),
                    showlegend=False, hoverinfo="skip"
                ))
                fig_window.add_trace(go.Scatter(
                    x=frac_curve, y=y_plot, mode='lines',
                    fill='tonextx', fillcolor='rgba(34, 197, 94, 0.12)',
                    line=dict(color='rgba(203, 213, 225, 0.2)', width=0.5),
                    name='Janela Operacional Segura'
                ))

            # Curva de Sobrecarga (Gardner)
            if sobrecarga_curve is not None and not np.all(np.isnan(sobrecarga_curve)):
                fig_window.add_trace(go.Scatter(
                    x=sobrecarga_curve, y=y_plot, mode='lines',
                    line=dict(color='#94a3b8', width=1.8, dash='dot'),
                    name='Sobrecarga (Gardner)'
                ))

            # Curva de Fratura Real (LOT)
            fig_window.add_trace(go.Scatter(
                x=frac_curve, y=y_plot, mode='lines',
                line=dict(color='#f8fafc', width=2.8),
                name='Gradiente de Fratura (LOT)'
            ))

            # Curva de Poro Real (Eaton)
            fig_window.add_trace(go.Scatter(
                x=poro_curve, y=y_plot, mode='lines',
                line=dict(color='#ef4444', width=2.3),
                name='Pressão de Poros (Eaton)'
            ))

            # Curva de Colapso Real (Mohr-Coulomb)
            if colapso_curve is not None and not np.all(np.isnan(colapso_curve)):
                fig_window.add_trace(go.Scatter(
                    x=colapso_curve, y=y_plot, mode='lines',
                    line=dict(color='#f97316', width=2.0, dash='dash'),
                    name='Colapso (Mohr-Coulomb)'
                ))

            # Curva 1: Escada Verde de Fluidos e Pastas (Safe Mud Weight)
            x_escada, y_escada_ft, casing_pts = _gerar_perfil_escada_fluidos(
                z_max=z_max,
                z_toc=z_toc,
                pastas_topo_base=pastas_topo_base,
                dens_lama=dens_lama,
                sapatas_meta=sapatas_meta,
                lda_ft=lda_ft,
                fator_escala_alturas=fator_escala_alturas
            )
            y_escada_plot = [y * fator_y for y in y_escada_ft]
            fig_window.add_trace(go.Scatter(
                x=x_escada, y=y_escada_plot, mode='lines',
                line=dict(color='#22c55e', width=3.4),
                name='Programa Lama + Pastas (Escada)'
            ))

            # Marcadores triangulares nas sapatas sobre a escada
            if casing_pts:
                fig_window.add_trace(go.Scatter(
                    x=[cp["densidade"] for cp in casing_pts],
                    y=[cp["prof_ft"] * fator_y for cp in casing_pts],
                    mode='markers',
                    marker=dict(symbol='triangle-left', size=11, color='#f8fafc', line=dict(color='#0f172a', width=1.5)),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # Curva 2: EMW Real Integrado da Coluna de Cimento
            fig_window.add_trace(go.Scatter(
                x=emw_curve, y=y_plot, mode='lines',
                line=dict(color='#38bdf8', width=2.2, dash='dash'),
                name=f'🌊 EMW Acumulado ({emw_curve[0]:.2f} ➔ {emw_curve[-1]:.2f} ppg)'
            ))

            # Anotações das Sapatas (Casing Points) na lateral direita
            for cp in casing_pts:
                p_val = cp['prof_ft'] * fator_y
                diam_s = cp.get('diam', '')
                p_str = f"{p_val:,.0f}".replace(",", ".") if usar_metros else f"{p_val:,.0f}"
                lbl = f"Sapata {diam_s} ({p_str} {unid_lbl})"
                fig_window.add_hline(
                    y=p_val, line_dash="dashdot", line_color="rgba(148, 163, 184, 0.45)", line_width=1.1
                )
                fig_window.add_annotation(
                    x=19.05, y=p_val,
                    text=f"<b>◀ {lbl}</b>",
                    showarrow=False,
                    xanchor="right",
                    yanchor="bottom",
                    yshift=3,
                    bgcolor="rgba(15, 23, 42, 0.85)",
                    bordercolor="rgba(148, 163, 184, 0.4)",
                    borderwidth=1,
                    borderpad=3,
                    font=dict(size=10, color="#f8fafc", family="JetBrains Mono")
                )

        else:
            # ── MODO 2: GRADIENTE ANALÍTICO TEÓRICO REFINADO COM COMPACTAÇÃO FÍSICA ──
            prof_base_m = float(st.session_state.get('ia_base', 3260.0))
            prof_base_ft = prof_base_m * 3.28084
            z_max = max(prof_base_ft, total_altura_ft * 1.25, 4000.0)
            depth_steps = np.linspace(0, z_max, 150)
            max_x_val = 19.2

            if z_max > 6500.0 and total_altura_ft < z_max * 0.25 and (total_altura_ft * 3.28084) <= z_max * 0.75:
                fator_escala_alturas = 3.28084
            else:
                fator_escala_alturas = 1.0

            # Compactação física realista de bacia sedimentar (curvatura suave sem retas rígidas)
            grad_poro_topo = min(grad_poro_alvo, 8.80)
            grad_frac_topo = max(grad_frac_alvo - 2.0, 13.50)

            fator_comp_poro = (depth_steps / z_max) ** 0.70
            fator_comp_frac = (depth_steps / z_max) ** 0.60
            poro_curve = grad_poro_topo + (grad_poro_alvo - grad_poro_topo) * fator_comp_poro
            frac_curve = grad_frac_topo + (grad_frac_alvo - grad_frac_topo) * fator_comp_frac
            lama_curve = np.full_like(depth_steps, dens_lama)

            # Posição das pastas na base com lama até a superfície (TOC realista)
            z_toc = max(0.0, z_max - (total_altura_ft * fator_escala_alturas))
            pastas_topo_base = list(reversed(resultados_finais))

            emw_curve = []
            for z in depth_steps:
                if z <= 0:
                    emw_curve.append(dens_lama)
                elif z <= z_toc:
                    emw_curve.append(dens_lama)
                else:
                    p_acum_psi = 0.052 * dens_lama * z_toc
                    z_layer_top = z_toc
                    for p in pastas_topo_base:
                        h = p['altura'] * fator_escala_alturas
                        z_layer_bottom = z_layer_top + h
                        if z <= z_layer_top:
                            break
                        dz = min(z, z_layer_bottom) - z_layer_top
                        p_acum_psi += 0.052 * p['densidade'] * dz
                        z_layer_top = z_layer_bottom
                    emw_val = p_acum_psi / (0.052 * z)
                    emw_curve.append(emw_val)
            emw_curve = np.array(emw_curve)

            diff_frac = frac_curve - emw_curve
            diff_poro = emw_curve - poro_curve
            min_margem_frac = float(np.min(diff_frac))
            min_margem_poro = float(np.min(diff_poro))

            if min_margem_frac < 0:
                idx_viol_frac = np.where(diff_frac < 0)[0]
                z_ini_frac = depth_steps[idx_viol_frac[0]] * fator_y
                z_fim_frac = depth_steps[idx_viol_frac[-1]] * fator_y
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE FRATURA:</b> EMW excede a fratura entre <b>{z_ini_frac:,.0f} {unid_lbl} e {z_fim_frac:,.0f} {unid_lbl}</b> (excesso de até <b>{abs(min_margem_frac):.2f} ppg</b>).
                    <br><span style="font-size: 0.78rem; color: #cbd5e1;">💡 <i>Solução:</i> Utilize uma pasta de preenchimento mais leve (<b>Lead Slurry</b>) na seção superior.</span>
                </div>"""
            elif min_margem_poro < 0:
                idx_viol_poro = np.where(diff_poro < 0)[0]
                z_ini_poro = depth_steps[idx_viol_poro[0]] * fator_y
                z_fim_poro = depth_steps[idx_viol_poro[-1]] * fator_y
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE KICK:</b> Coluna subbalanceada entre <b>{z_ini_poro:,.0f} {unid_lbl} e {z_fim_poro:,.0f} {unid_lbl}</b> (déficit de até <b>{abs(min_margem_poro):.2f} ppg</b> abaixo do poro).
                </div>"""
            else:
                badge_html = f"""<div style="background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #a7f3d0; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between;">
                    <span><b>🟢 COLUNA 100% CONFORME</b> (Janela Segura)</span>
                    <span>Margem Mín. Poro: <b>+{min_margem_poro:.2f} ppg</b> │ Fratura: <b>+{min_margem_frac:.2f} ppg</b></span>
                </div>"""
            
            st.html(badge_html)

            y_plot = depth_steps * fator_y
            lda_plot = 300.0 * fator_y

            fig_window = go.Figure()

            # Faixa de Lâmina d'água representativa no analítico
            fig_window.add_hrect(
                y0=0, y1=lda_plot,
                fillcolor="rgba(56, 189, 248, 0.22)",
                line_width=1,
                line_color="rgba(56, 189, 248, 0.45)",
                annotation_text=f"🌊 Lâmina d'Água (LDA = {lda_plot:.0f} {unid_lbl})",
                annotation_position="top left",
                annotation_font=dict(color="#38bdf8", size=10, family="JetBrains Mono")
            )

            # Preenchimento da Janela Segura
            fig_window.add_trace(go.Scatter(
                x=poro_curve, y=y_plot, mode='lines',
                line=dict(color='rgba(239, 68, 68, 0.0)', width=0.5),
                showlegend=False, hoverinfo="skip"
            ))
            fig_window.add_trace(go.Scatter(
                x=frac_curve, y=y_plot, mode='lines',
                fill='tonextx', fillcolor='rgba(34, 197, 94, 0.12)',
                line=dict(color='rgba(203, 213, 225, 0.2)', width=0.5),
                name='Janela Operacional Segura'
            ))

            # Curva de Fratura
            fig_window.add_trace(go.Scatter(
                x=frac_curve, y=y_plot, mode='lines',
                line=dict(color='#f8fafc', width=2.8),
                name='Gradiente de Fratura (LOT)'
            ))

            # Curva de Poro
            fig_window.add_trace(go.Scatter(
                x=poro_curve, y=y_plot, mode='lines',
                line=dict(color='#ef4444', width=2.3),
                name='Pressão de Poros (Eaton)'
            ))

            # 1. Escada Verde de Fluidos e Pastas (Safe Mud Weight)
            x_escada, y_escada_ft, casing_pts = _gerar_perfil_escada_fluidos(
                z_max=z_max,
                z_toc=z_toc,
                pastas_topo_base=pastas_topo_base,
                dens_lama=dens_lama,
                sapatas_meta=None,
                lda_ft=300.0,
                fator_escala_alturas=fator_escala_alturas
            )
            y_escada_plot = [y * fator_y for y in y_escada_ft]
            fig_window.add_trace(go.Scatter(
                x=x_escada, y=y_escada_plot, mode='lines',
                line=dict(color='#22c55e', width=3.4),
                name='Programa Lama + Pastas (Escada)'
            ))

            if casing_pts:
                fig_window.add_trace(go.Scatter(
                    x=[cp["densidade"] for cp in casing_pts],
                    y=[cp["prof_ft"] * fator_y for cp in casing_pts],
                    mode='markers',
                    marker=dict(symbol='triangle-left', size=11, color='#f8fafc', line=dict(color='#0f172a', width=1.5)),
                    showlegend=False,
                    hoverinfo='skip'
                ))

            # 2. Curva EMW Acumulado
            fig_window.add_trace(go.Scatter(
                x=emw_curve, y=y_plot, mode='lines',
                line=dict(color='#38bdf8', width=2.2, dash='dash'),
                name=f'🌊 EMW Acumulado ({emw_curve[0]:.2f} ➔ {emw_curve[-1]:.2f} ppg)'
            ))

            # Anotações dos Casing Points na lateral direita
            for cp in casing_pts:
                p_val = cp['prof_ft'] * fator_y
                diam_s = cp.get('diam', '')
                p_str = f"{p_val:,.0f}".replace(",", ".") if usar_metros else f"{p_val:,.0f}"
                lbl = f"Sapata {diam_s} ({p_str} {unid_lbl})"
                fig_window.add_hline(
                    y=p_val, line_dash="dashdot", line_color="rgba(148, 163, 184, 0.45)", line_width=1.1
                )
                fig_window.add_annotation(
                    x=19.05, y=p_val,
                    text=f"<b>◀ {lbl}</b>",
                    showarrow=False,
                    xanchor="right",
                    yanchor="bottom",
                    yshift=3,
                    bgcolor="rgba(15, 23, 42, 0.85)",
                    bordercolor="rgba(148, 163, 184, 0.4)",
                    borderwidth=1,
                    borderpad=3,
                    font=dict(size=10, color="#f8fafc", family="JetBrains Mono")
                )

        min_x_val = 6.5
        max_x_val = 19.2

        fig_window.update_layout(
            height=480,
            yaxis=dict(
                autorange="reversed",
                title=f"Profundidade Vertical - TVD ({unid_lbl})",
                title_font=dict(size=13, color="#94a3b8"),
                tickfont=dict(size=12, family="JetBrains Mono", color="#cbd5e1"),
                gridcolor="#1e293b",
                zeroline=False
            ),
            xaxis=dict(
                title="Densidade Equivalente / Gradiente (lbm/gal - ppg)",
                title_font=dict(size=13, color="#94a3b8"),
                tickfont=dict(size=12, family="JetBrains Mono", color="#cbd5e1"),
                gridcolor="#1e293b",
                zerolinecolor="#334155",
                range=[min_x_val, max_x_val]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.28,
                xanchor="center",
                x=0.5,
                font=dict(size=10.5, color="#cbd5e1")
            ),
            margin=dict(l=50, r=20, t=10, b=35),
            paper_bgcolor="#111827",
            plot_bgcolor="#0b0f19"
        )

        st.plotly_chart(fig_window, width="stretch", config=PLOTLY_CONFIG_INTERATIVO)

        if btn_tela_cheia_janela:
            _exibir_dialog_janela_geomecanica(
                fig_window,
                badge_html=badge_html,
                fonte=fonte_geomec if usar_curvas_reais else "Modelo Analítico (Aba 3)",
                min_m_poro=min_margem_poro,
                min_m_frac=min_margem_frac
            )

    # 3. Tabela Executiva Consolidada
    st.markdown("---")
    st.markdown("#### 📋 Matriz Hidráulica & Cubagem por Seção de Pasta")

    dados_tabela = [{
        'Seção': f"Pasta {r['numero']}",
        'Classe API': f"Classe {r.get('classe', 'G')}",
        'Altura (ft)': f"{r['altura']:,.1f}",
        'Sacos (sk)': f"{r['sacos']:,}",
        'Rendimento (ft³/sk)': f"{r['rendimento']:.4f}",
        'Volume Calda (bbl)': f"{r['volume']/5.615:.1f}",
        'Densidade (ppg)': f"{r['densidade']:.2f}",
        'P. Hidrostática (psi)': f"{r.get('pressao_hidrostatica', 0.0):.1f}"
    } for r in resultados_finais]

    df_resumo = pd.DataFrame(dados_tabela)
    st.dataframe(df_resumo, hide_index=True, width="stretch")


def render_analise_individual(resultados_finais: List[Dict[str, Any]]):
    """
    Renderiza a Ficha de Traço Operacional (Rig Batch Sheet) e a análise de componentes.
    """
    if not resultados_finais:
        return

    st.markdown("---")
    st.markdown("### 🔬 Ficha de Traço Operacional (*Batch Sheet*) & Distribuição Química")
    st.caption("Detalhamento estequiométrico para pesagem e mistura em sonda:")

    c_sel, _ = st.columns([1.5, 2.5])
    with c_sel:
        pasta_selecionada = st.selectbox(
            "Selecione a Pasta para Detalhamento Operacional:",
            options=[f"Pasta {r['numero']} (Classe {r.get('classe', 'G')})" for r in resultados_finais],
            key="sb_pasta_analise"
        )

    # Extrai o índice numérico da pasta
    num_p_str = pasta_selecionada.split(" ")[1]
    idx_pasta = int(num_p_str) - 1
    pasta_alvo = resultados_finais[idx_pasta]
    detalhes = pasta_alvo.get('detalhes', [])

    vol_bbl = pasta_alvo['volume'] / 5.615
    ton_cimento = (pasta_alvo['sacos'] * 94.0) / 2204.62

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Volume da Pasta", f"{pasta_alvo['volume']:.1f} ft³", f"{vol_bbl:.1f} bbl")
    c2.metric("Sacos de Cimento", f"{pasta_alvo['sacos']:,} sk", f"{ton_cimento:.2f} t métricas")
    c3.metric("Rendimento (Yield)", f"{pasta_alvo['rendimento']:.4f} ft³/sk")
    c4.metric("Densidade Resultante", f"{pasta_alvo['densidade']:.2f} ppg")

    col_tabela, col_grafico = st.columns([1.1, 1], gap="large")

    df_detalhes = pd.DataFrame(detalhes)

    with col_tabela:
        st.markdown(f"##### 📋 Ficha de Pesagem & Mistura ({pasta_selecionada})")
        df_display = pd.DataFrame([{
            'Componente': item['Componente'],
            'Categoria': item['Categoria'],
            'Dosagem': item['Dosagem'],
            'Vol/sk (gal)': f"{item['Vol (gal/sk)']:.3f}",
            'Massa/sk (lb)': f"{item['Massa (lb/sk)']:.2f}",
            'Massa Total (lb)': f"{item['Massa Total (lb)']:,.0f}",
            'Vol Total (bbl)': f"{item['Vol Total (bbl)']:.2f}"
        } for item in detalhes])

        st.dataframe(df_display, hide_index=True, width="stretch")

    with col_grafico:
        st.markdown("##### 📊 Distribuição por Componente")
        metrica_grafico = st.segmented_control(
            "Métrica de Visualização:",
            ["Massa por Saco (lb/sk)", "Volume por Saco (gal/sk)", "Massa Total no Poço (lb)"],
            default="Massa por Saco (lb/sk)",
            key="seg_metrica_grafico"
        )

        coluna_map = {
            "Massa por Saco (lb/sk)": ('Massa (lb/sk)', 'Massa por Saco (lb/sk)', 'lb/sk'),
            "Volume por Saco (gal/sk)": ('Vol (gal/sk)', 'Volume por Saco (gal/sk)', 'gal/sk'),
            "Massa Total no Poço (lb)": ('Massa Total (lb)', 'Massa Total Requerida (lb)', 'lb')
        }

        col_val, label_eixo, unidade = coluna_map.get(metrica_grafico, ('Massa (lb/sk)', 'Massa por Saco (lb/sk)', 'lb/sk'))

        fig_bar = px.bar(
            df_detalhes,
            x=col_val,
            y='Componente',
            color='Categoria',
            orientation='h',
            text=df_detalhes[col_val].apply(lambda v: f"{v:,.2f} {unidade}"),
            color_discrete_sequence=["#38bdf8", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#a855f7"]
        )

        fig_bar.update_traces(
            textposition='outside',
            cliponaxis=False,
            textfont=dict(size=11, family="JetBrains Mono", color="#cbd5e1")
        )
        fig_bar.update_layout(
            xaxis_title=label_eixo,
            xaxis_title_font=dict(size=12, color="#94a3b8"),
            xaxis=dict(tickfont=dict(size=11, family="JetBrains Mono", color="#cbd5e1"), gridcolor="#1e293b"),
            yaxis_title="",
            yaxis=dict(tickfont=dict(size=12, color="#f1f5f9"), categoryorder='total ascending'),
            height=340,
            margin=dict(l=20, r=40, t=20, b=20),
            paper_bgcolor="#111827",
            plot_bgcolor="#0b0f19",
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(size=10, color="#cbd5e1"))
        )

        st.plotly_chart(fig_bar, width="stretch", config=PLOTLY_CONFIG_INTERATIVO)
