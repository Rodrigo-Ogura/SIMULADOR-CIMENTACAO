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
    dens_lama: float
) -> Tuple[List[float], List[float], List[Dict[str, Any]]]:
    """
    Gera coordenadas (x=densidade_ppg, y=profundidade_ft) em formato de degraus ortogonais (step-plot)
    representando a densidade dos fluidos em cada cota do espaço anular do poço (Lama -> Lead -> Tail)
    e lista de interfaces para anotações operacionais.
    """
    x_step: List[float] = []
    y_step: List[float] = []
    interfaces: List[Dict[str, Any]] = []

    # 1. Intervalo de Lama de Perfuração (da superfície até o Topo de Cimento)
    if z_toc > 0:
        x_step.extend([dens_lama, dens_lama])
        y_step.extend([0.0, z_toc])
        interfaces.append({'tipo': 'TOC', 'prof_ft': z_toc, 'texto': f"TOC ({z_toc:.0f} ft)"})
    else:
        x_step.append(dens_lama)
        y_step.append(0.0)

    # 2. Intervalos de Pastas de Cimento (do TOC até o fundo do poço)
    z_cursor = z_toc
    for idx, p in enumerate(pastas_topo_base):
        dens_p = float(p.get('densidade', 15.80))
        h_p = float(p.get('altura', 500.0))
        z_prox = min(z_cursor + h_p, z_max)

        # Salto horizontal na interface entre fluidos de densidades distintas
        if len(x_step) > 0 and abs(x_step[-1] - dens_p) > 0.001:
            x_step.append(dens_p)
            y_step.append(z_cursor)

        # Patamar vertical constante da pasta no seu intervalo
        x_step.extend([dens_p, dens_p])
        y_step.extend([z_cursor, z_prox])

        # Se houver mudança de pasta e não for a última, registra interface
        if idx < len(pastas_topo_base) - 1:
            interfaces.append({'tipo': 'PASTA', 'prof_ft': z_prox, 'texto': f"Interface ({z_prox:.0f} ft)"})

        z_cursor = z_prox

    # Se ainda sobrar profundidade até a base por tolerância numérica, estende o último patamar
    if z_cursor < z_max and len(x_step) > 0:
        x_step.extend([x_step[-1], x_step[-1]])
        y_step.extend([z_cursor, z_max])

    return x_step, y_step, interfaces


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
            c_sub_pw, c_tog_pw = st.columns([1.5, 1.0], vertical_alignment="center")
            with c_sub_pw:
                st.caption(f"Perfil: **{fonte_geomec}**" if st.session_state.get("tog_curvas_reais_dash", True) else "Perfil dinâmico analítico (Aba 3):")
            with c_tog_pw:
                usar_curvas_reais = st.toggle("🌐 Curvas Reais", value=True, key="tog_curvas_reais_dash")
        else:
            usar_curvas_reais = False
            st.caption("Perfil dinâmico da coluna hidrostática versus limites geomecânicos (Aba 3):")

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

            # EMW da coluna de cimento superposta no intervalo de fundo do poço real
            z_toc = max(0.0, z_max - total_altura_ft)
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
                        h = p['altura']
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
                z_ini = depth_steps[idx_viol[0]]
                z_fim = depth_steps[idx_viol[-1]]
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE FRATURA REAL:</b> EMW excede a fratura de campo entre <b>{z_ini:.0f} ft e {z_fim:.0f} ft</b> (excesso de até <b>{abs(min_margem_frac):.2f} ppg</b>).
                    <br><span style="font-size: 0.78rem; color: #cbd5e1;">💡 <i>Ajuste operacional:</i> Reduza a densidade da pasta de topo (Lead) ou diminua a altura da coluna de cimento.</span>
                </div>"""
            elif min_margem_poro < 0:
                idx_viol = np.where(emw_curve - lim_inf_curve < 0)[0]
                z_ini = depth_steps[idx_viol[0]]
                z_fim = depth_steps[idx_viol[-1]]
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE INSTABILIDADE/KICK:</b> EMW abaixo do limite inferior (Poro/Colapso) entre <b>{z_ini:.0f} ft e {z_fim:.0f} ft</b> (déficit de até <b>{abs(min_margem_poro):.2f} ppg</b>).
                </div>"""
            else:
                badge_html = f"""<div style="background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #a7f3d0; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between;">
                    <span><b>🟢 COLUNA 100% CONFORME COM PERFIL REAL</b> ({fonte_geomec})</span>
                    <span>Margem Mín. Poro/Colapso: <b>+{min_margem_poro:.2f} ppg</b> │ Fratura: <b>+{min_margem_frac:.2f} ppg</b></span>
                </div>"""
            st.html(badge_html)

            fig_window = go.Figure()

            # Curva de Sobrecarga (se houver)
            if sobrecarga_curve is not None and not np.all(np.isnan(sobrecarga_curve)):
                fig_window.add_trace(go.Scatter(
                    x=sobrecarga_curve, y=depth_steps, mode='lines',
                    line=dict(color='#a855f7', width=1.5, dash='dot'),
                    name='Sobrecarga (Govb)'
                ))

            # Curva de Fratura Real
            fig_window.add_trace(go.Scatter(
                x=frac_curve, y=depth_steps, mode='lines',
                line=dict(color='#ef4444', width=2.5),
                name='Fratura Real (Gf)'
            ))

            # Curva de Poro Real
            fig_window.add_trace(go.Scatter(
                x=poro_curve, y=depth_steps, mode='lines',
                line=dict(color='#f59e0b', width=2, dash='dash'),
                name='Poro Real (Gp)'
            ))

            # Curva de Colapso Real (se houver)
            if colapso_curve is not None and not np.all(np.isnan(colapso_curve)):
                fig_window.add_trace(go.Scatter(
                    x=colapso_curve, y=depth_steps, mode='lines',
                    line=dict(color='#ec4899', width=1.8, dash='dashdot'),
                    name='Colapso Real (Gc)'
                ))

            # Preenchimento do Corredor Seguro Real
            if lim_inf_curve is not None and not np.all(np.isnan(lim_inf_curve)):
                fig_window.add_trace(go.Scatter(
                    x=lim_inf_curve, y=depth_steps, mode='lines',
                    line=dict(color='rgba(16, 185, 129, 0.4)', width=1),
                    showlegend=False, hoverinfo="skip"
                ))
                fig_window.add_trace(go.Scatter(
                    x=frac_curve, y=depth_steps, mode='lines',
                    fill='tonexty', fillcolor='rgba(16, 185, 129, 0.08)',
                    line=dict(color='rgba(16, 185, 129, 0.4)', width=1),
                    name='Janela Segura Real'
                ))

            # Curva 1: Degraus da Densidade dos Fluidos no Anular (A "Escada")
            x_escada, y_escada, _ = _gerar_perfil_escada_fluidos(
                z_max=z_max,
                z_toc=z_toc,
                pastas_topo_base=pastas_topo_base,
                dens_lama=dens_lama
            )
            fig_window.add_trace(go.Scatter(
                x=x_escada, y=y_escada, mode='lines',
                line=dict(color='#06b6d4', width=3.0),
                name='🪜 Peso dos Fluidos (Escada)'
            ))

            # Curva 2: EMW Real Integrado da Coluna de Cimento
            fig_window.add_trace(go.Scatter(
                x=emw_curve, y=depth_steps, mode='lines',
                line=dict(color='#38bdf8', width=2.5, dash='dash'),
                name=f'🌊 EMW Acumulado ({emw_curve[0]:.2f} ➔ {emw_curve[-1]:.2f} ppg)'
            ))

            # Anotações sutis de cotas operacionais (TOC e Sapata)
            if z_toc > 0:
                fig_window.add_hline(
                    y=z_toc, line_dash="dashdot", line_color="#64748b", line_width=1.2,
                    annotation_text=f"📍 TOC ({z_toc:.0f} ft)",
                    annotation_position="top left",
                    annotation_font=dict(size=10, color="#94a3b8")
                )
            h_sapata = params_poco.get('dist_sapata', 40.0)
            z_sapata = max(0.0, z_max - h_sapata)
            if z_sapata > z_toc:
                fig_window.add_hline(
                    y=z_sapata, line_dash="dot", line_color="#a855f7", line_width=1.0,
                    annotation_text=f"⚓ Sapata ({z_sapata:.0f} ft)",
                    annotation_position="bottom left",
                    annotation_font=dict(size=10, color="#c084fc")
                )

        else:
            # ── MODO 2: GRADIENTE ANALÍTICO TEÓRICO REFINADO COM COMPACTAÇÃO FÍSICA ──
            prof_base_m = float(st.session_state.get('ia_base', 2800.0))
            prof_base_ft = prof_base_m * 3.28084
            z_max = max(prof_base_ft, total_altura_ft * 1.25, 4000.0)
            depth_steps = np.linspace(0, z_max, 150)

            # Compactação física realista de bacia sedimentar (curvatura suave sem retas rígidas)
            grad_poro_topo = min(grad_poro_alvo, 8.80)
            grad_frac_topo = max(grad_frac_alvo - 2.0, 13.50)

            fator_comp_poro = (depth_steps / z_max) ** 0.70
            fator_comp_frac = (depth_steps / z_max) ** 0.60
            poro_curve = grad_poro_topo + (grad_poro_alvo - grad_poro_topo) * fator_comp_poro
            frac_curve = grad_frac_topo + (grad_frac_alvo - grad_frac_topo) * fator_comp_frac
            lama_curve = np.full_like(depth_steps, dens_lama)

            # Posição das pastas na base com lama até a superfície (TOC realista)
            z_toc = max(0.0, z_max - total_altura_ft)
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
                        h = p['altura']
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
                z_ini_frac = depth_steps[idx_viol_frac[0]]
                z_fim_frac = depth_steps[idx_viol_frac[-1]]
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE FRATURA:</b> EMW excede a fratura entre <b>{z_ini_frac:.0f} ft e {z_fim_frac:.0f} ft</b> (excesso de até <b>{abs(min_margem_frac):.2f} ppg</b>).
                    <br><span style="font-size: 0.78rem; color: #cbd5e1;">💡 <i>Solução:</i> Utilize uma pasta de preenchimento mais leve (<b>Lead Slurry</b>) na seção superior.</span>
                </div>"""
            elif min_margem_poro < 0:
                idx_viol_poro = np.where(diff_poro < 0)[0]
                z_ini_poro = depth_steps[idx_viol_poro[0]]
                z_fim_poro = depth_steps[idx_viol_poro[-1]]
                badge_html = f"""<div style="background-color: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #fca5a5; font-family: 'JetBrains Mono';">
                    <b>🔴 ALERTA DE KICK:</b> Coluna subbalanceada entre <b>{z_ini_poro:.0f} ft e {z_fim_poro:.0f} ft</b> (déficit de até <b>{abs(min_margem_poro):.2f} ppg</b> abaixo do poro).
                </div>"""
            else:
                badge_html = f"""<div style="background-color: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.82rem; color: #a7f3d0; font-family: 'JetBrains Mono'; display: flex; justify-content: space-between;">
                    <span><b>🟢 COLUNA 100% CONFORME</b> (Janela Segura)</span>
                    <span>Margem Mín. Poro: <b>+{min_margem_poro:.2f} ppg</b> │ Fratura: <b>+{min_margem_frac:.2f} ppg</b></span>
                </div>"""
            
            st.html(badge_html)

            fig_window = go.Figure()
            fig_window.add_trace(go.Scatter(
                x=frac_curve, y=depth_steps, mode='lines',
                line=dict(color='#ef4444', width=2),
                name=f'Fratura ({grad_frac_alvo:.1f} ppg no Fundo)'
            ))
            fig_window.add_trace(go.Scatter(
                x=poro_curve, y=depth_steps, mode='lines',
                line=dict(color='#f59e0b', width=2, dash='dash'),
                name=f'Poro ({grad_poro_alvo:.1f} ppg no Fundo)'
            ))
            fig_window.add_trace(go.Scatter(
                x=frac_curve, y=depth_steps, mode='lines',
                fill='tonexty', fillcolor='rgba(16, 185, 129, 0.08)',
                line=dict(color='rgba(16, 185, 129, 0.3)', width=1),
                name='Janela Segura'
            ))

            # 1. Escada da Densidade dos Fluidos no Anular
            x_escada, y_escada, _ = _gerar_perfil_escada_fluidos(
                z_max=z_max,
                z_toc=z_toc,
                pastas_topo_base=pastas_topo_base,
                dens_lama=dens_lama
            )
            fig_window.add_trace(go.Scatter(
                x=x_escada, y=y_escada, mode='lines',
                line=dict(color='#06b6d4', width=3.0),
                name='🪜 Peso dos Fluidos (Escada)'
            ))

            # 2. Curva EMW Acumulado
            fig_window.add_trace(go.Scatter(
                x=emw_curve, y=depth_steps, mode='lines',
                line=dict(color='#38bdf8', width=2.5, dash='dash'),
                name=f'🌊 EMW Acumulado ({emw_curve[0]:.2f} ➔ {emw_curve[-1]:.2f} ppg)'
            ))

            # Anotações sutis de cotas operacionais (TOC e Sapata)
            if z_toc > 0:
                fig_window.add_hline(
                    y=z_toc, line_dash="dashdot", line_color="#64748b", line_width=1.2,
                    annotation_text=f"📍 TOC ({z_toc:.0f} ft)",
                    annotation_position="top left",
                    annotation_font=dict(size=10, color="#94a3b8")
                )
            h_sapata = params_poco.get('dist_sapata', 40.0)
            z_sapata = max(0.0, z_max - h_sapata)
            if z_sapata > z_toc:
                fig_window.add_hline(
                    y=z_sapata, line_dash="dot", line_color="#a855f7", line_width=1.0,
                    annotation_text=f"⚓ Sapata ({z_sapata:.0f} ft)",
                    annotation_position="bottom left",
                    annotation_font=dict(size=10, color="#c084fc")
                )

        if usar_curvas_reais and perfil_real_df is not None:
            min_x_val = min(7.5, float(np.nanmin(poro_curve)) - 0.5) if len(poro_curve) > 0 and not np.all(np.isnan(poro_curve)) else 7.5
            max_x_val = max(19.5, float(np.nanmax(frac_curve)) + 0.5) if len(frac_curve) > 0 and not np.all(np.isnan(frac_curve)) else 19.5
        else:
            min_x_val = min(8.0, grad_poro_topo - 0.5)
            max_x_val = max(19.0, grad_frac_alvo + 1.0)

        fig_window.update_layout(
            height=460,
            yaxis=dict(
                autorange="reversed",
                title="Profundidade TVD (ft)",
                title_font=dict(size=13, color="#94a3b8"),
                tickfont=dict(size=12, family="JetBrains Mono", color="#cbd5e1"),
                gridcolor="#1e293b",
                zeroline=False
            ),
            xaxis=dict(
                title="Densidade Equivalente (ppg)",
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
