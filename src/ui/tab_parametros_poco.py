"""
Componente visual para configuração da Geometria do Poço, Janela Geomecânica e Gestão de Aditivos.
Estilo OpenLab Drilling (NORCE).
"""

import streamlit as st
from typing import Dict, Tuple
import pandas as pd
from src.services.aditivo_service import AditivoService
from config import CATEGORIAS_ADITIVOS


def render_parametros_poco(aditivos_db: Dict[str, dict]) -> Tuple[Dict[str, float], Dict[str, dict]]:
    """
    Renderiza os parâmetros geométricos, limites geomecânicos do poço e gestão de aditivos.
    """
    st.markdown("### 📐 Geometria do Poço, Geomecânica & Banco de Aditivos")
    st.caption("Configuração dimensional da coluna, folgas anulares e limites operacionais de pressão de poro/fratura:")

    col_geom, col_banco = st.columns([1.1, 1], gap="large")

    with col_geom:
        # 1. Parâmetros Geométricos
        with st.container(border=True):
            st.markdown("##### ⚙️ Parâmetros Geométricos de Perfuração")
            
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                d_broca = st.number_input(
                    "Diâmetro da Broca / Poço Aberto (in):",
                    value=17.000,
                    format="%.3f",
                    step=0.125,
                    key="param_d_broca",
                    help="Diâmetro nominal do poço aberto (Open Hole Bit Diameter)."
                )
                d_ext = st.number_input(
                    "Diâmetro Externo Revestimento OD (in):",
                    value=13.375,
                    format="%.3f",
                    step=0.125,
                    key="param_d_ext",
                    help="Diâmetro externo nominal do casing de aço."
                )
            with c_g2:
                d_int = st.number_input(
                    "Diâmetro Interno Revestimento ID (in):",
                    value=12.415,
                    format="%.3f",
                    step=0.125,
                    key="param_d_int",
                    help="Diâmetro interno do casing para cálculo do bolsão de sapata."
                )
                fator_excesso = st.number_input(
                    "Fator de Excesso Anular (Washout):",
                    value=1.75,
                    format="%.2f",
                    step=0.05,
                    key="param_fator_excesso",
                    help="Ex: 1.75 = 75% de excesso volumétrico para compensação de cavernas e arrombamentos."
                )

            dist_sapata = st.number_input(
                "Distância Colar Flutuador até a Sapata (ft):",
                value=40.0,
                format="%.1f",
                step=5.0,
                key="param_dist_sapata",
                help="Comprimento do bolsão de cimento remanescente no interior do revestimento (*Shoe Track*)."
            )

            # Telemetria da folga anular
            folga_diametral = d_broca - d_ext
            folga_radial = folga_diametral / 2.0
            
            st.markdown(f"""
            <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 10px 14px; margin-top: 10px;">
                <span style="color: #94a3b8; font-size: 0.80rem; font-weight: 600; text-transform: uppercase;">Folga Anular Diametral:</span>
                <span style="color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.05rem; margin-left: 8px;">{folga_diametral:.3f} in</span>
                <span style="color: #64748b; font-size: 0.85rem; margin-left: 6px;">({folga_diametral*25.4:.1f} mm · Folga Radial: {folga_radial:.3f} in)</span>
            </div>
            """, unsafe_allow_html=True)

        # 2. Resumo da Janela Geomecânica (Vinculada com a Aba 3 - Módulo Especialista)
        with st.container(border=True):
            st.markdown("##### 🛡️ Janela Geomecânica (Integrada com a Aba 3)")
            st.caption("Os limites de pressão são configurados no **Módulo Especialista (Aba 3)** e alimentam a janela operacional:")

            poro_atual = st.session_state.get("ia_poro", 10.20)
            frac_atual = st.session_state.get("ia_frac", 16.80)
            dens_lama = st.number_input(
                "Densidade da Lama de Perfuração no Poço (ppg):",
                value=9.50,
                format="%.2f",
                step=0.10,
                key="param_dens_lama",
                help="Densidade do fluido de perfuração atualmente no poço antes do bombeio da cimentação."
            )

            corredor_fundo = frac_atual - poro_atual
            st.markdown(f"""
            <div style="background-color: #0f172a; border: 1px solid #1e293b; border-left: 4px solid #10b981; border-radius: 6px; padding: 12px 14px; margin-top: 8px;">
                <div style="color: #94a3b8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase;">Limites Atuais da Formação (Fundo do Poço):</div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono'; margin-top: 6px; font-size: 0.88rem;">
                    <span style="color: #f59e0b;">Poro: <b>{poro_atual:.2f} ppg</b></span>
                    <span style="color: #10b981; font-weight: 700;">Corredor Seguro: ↔ {corredor_fundo:.2f} ppg</span>
                    <span style="color: #ef4444;">Fratura: <b>{frac_atual:.2f} ppg</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_banco:
        with st.container(border=True):
            st.markdown("##### 🧪 Catálogo de Aditivos Químicos")
            st.caption("Base persistente de aditivos homologados (`data/aditivos_db.json`):")

            c_ad1, c_ad2 = st.columns(2)
            with c_ad1:
                novo_nome = st.text_input("Nome do Aditivo:", key="novo_adit_nome", placeholder="Ex: Antiespumante AF-1")
                nova_categoria = st.selectbox("Categoria Funcional:", CATEGORIAS_ADITIVOS, key="novo_adit_cat")
            with c_ad2:
                nova_densidade = st.number_input("Gravidade Específica (SG):", value=1.00, format="%.2f", step=0.05, key="novo_adit_dens")
                novo_tipo = st.selectbox("Estado / Tipo:", ["solido", "salmoura"], key="novo_adit_tipo")

            col_btn_cad, col_btn_rst = st.columns([1.5, 1])
            with col_btn_cad:
                if st.button("💾 Cadastrar Aditivo", type="primary", use_container_width=True, key="btn_salvar_adit"):
                    if novo_nome.strip():
                        st.session_state.aditivos_db = AditivoService.salvar_aditivo(
                            novo_nome.strip(), nova_densidade, novo_tipo, nova_categoria
                        )
                        st.success(f"Aditivo '{novo_nome}' homologado com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Informe o nome comercial para cadastrar.")
            
            with col_btn_rst:
                if st.button("🔄 Resetar Banco", use_container_width=True, help="Restaura o catálogo oficial de 26 aditivos do Bourgoyne et al."):
                    st.session_state.aditivos_db = AditivoService.inicializar_banco()
                    st.info("Catálogo padrão restaurado!")
                    st.rerun()

        # Tabela expansível com visualização rápida
        with st.expander(f"📚 Ver Catálogo Homologado ({len(aditivos_db)} aditivos)", expanded=False):
            dados_cat = [{
                'Aditivo': k,
                'Categoria': v.get('categoria', 'Geral'),
                'Gravidade Específica (SG)': f"{v.get('densidade', 1.0):.2f}",
                'Tipo': v.get('tipo', 'solido')
            } for k, v in sorted(aditivos_db.items())]
            st.dataframe(pd.DataFrame(dados_cat), hide_index=True, width="stretch")

    params_poco = {
        'd_broca': d_broca,
        'd_ext': d_ext,
        'd_int': d_int,
        'fator_excesso': fator_excesso,
        'dist_sapata': dist_sapata,
        'dens_lama': dens_lama
    }

    return params_poco, st.session_state.aditivos_db
