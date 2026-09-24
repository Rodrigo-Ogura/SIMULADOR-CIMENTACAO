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

    # Inicialização de estado seguro para parâmetros geométricos
    if "param_d_broca" not in st.session_state:
        st.session_state["param_d_broca"] = 17.000
    if "param_d_ext" not in st.session_state:
        st.session_state["param_d_ext"] = 13.375
    if "param_d_int" not in st.session_state:
        st.session_state["param_d_int"] = 12.415
    if "param_fator_excesso" not in st.session_state:
        st.session_state["param_fator_excesso"] = 1.75
    if "param_dist_sapata" not in st.session_state:
        st.session_state["param_dist_sapata"] = 40.0

    col_geom, col_banco = st.columns([1.1, 1], gap="large")

    with col_geom:
        # Sincronização Inteligente com o Perfil da Aba 1 (Janela Geomecânica)
        perfil_ativo = st.session_state.get("perfil_geomecanico_ativo", None)
        meta_ativo = st.session_state.get("metadados_geomecanicos_ativos", None)
        fonte_nome = st.session_state.get("fonte_geomecanica_ativa", "Perfil Ativo")

        if perfil_ativo is not None:
            with st.container(border=True):
                c_snc1, c_snc2 = st.columns([1.8, 1.2])
                with c_snc1:
                    st.caption(f"🌐 **Perfil Conectado da Aba 1:** `{fonte_nome}`")
                with c_snc2:
                    if meta_ativo:
                        if st.button("🪄 Puxar Dados do Poço", key="btn_sync_geom", help="Preenche diâmetros e lama com base no histórico do poço carregado na Aba 1.", use_container_width=True):
                            st.session_state["param_d_broca"] = float(meta_ativo.get("d_broca_in", 17.0))
                            st.session_state["param_d_ext"] = float(meta_ativo.get("d_ext_in", 13.375))
                            st.session_state["param_d_int"] = float(meta_ativo.get("d_int_in", 12.415))
                            st.session_state["ia_dens_lama"] = float(meta_ativo.get("dens_lama_fundo_ppg", 10.60))
                            st.rerun()
                    else:
                        st.caption("ℹ️ CSV Customizado ativo. Diâmetros nominais mantidos para preenchimento manual.")

        # 1. Parâmetros Geométricos
        with st.container(border=True):
            st.markdown("##### ⚙️ Parâmetros Geométricos de Perfuração")
            
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                d_broca = st.number_input(
                    "Diâmetro da Broca / Poço Aberto (in):",
                    format="%.3f",
                    step=0.125,
                    key="param_d_broca",
                    help="Diâmetro nominal do poço aberto (Open Hole Bit Diameter)."
                )
                d_ext = st.number_input(
                    "Diâmetro Externo Revestimento OD (in):",
                    format="%.3f",
                    step=0.125,
                    key="param_d_ext",
                    help="Diâmetro externo nominal do casing de aço."
                )
            with c_g2:
                d_int = st.number_input(
                    "Diâmetro Interno Revestimento ID (in):",
                    format="%.3f",
                    step=0.125,
                    key="param_d_int",
                    help="Diâmetro interno do casing para cálculo do bolsão de sapata."
                )
                fator_excesso = st.number_input(
                    "Fator de Excesso Anular (Washout):",
                    format="%.2f",
                    step=0.05,
                    key="param_fator_excesso",
                    help="Ex: 1.75 = 75% de excesso volumétrico para compensação de cavernas e arrombamentos."
                )

            dist_sapata = st.number_input(
                "Distância Colar Flutuador até a Sapata (ft):",
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

        # 2. Resumo da Janela Geomecânica (Integrada dinamicamente com a Aba 3 - Módulo Especialista)
        with st.container(border=True):
            st.markdown("##### 🛡️ Janela Geomecânica & Fluido no Poço")
            st.caption("Limites geomecânicos e densidade da lama integrados em tempo real com o **Módulo Especialista (Aba 3)**:")

            poro_atual = float(st.session_state.get("ia_poro", 10.20))
            frac_atual = float(st.session_state.get("ia_frac", 16.80))
            dens_lama = float(st.session_state.get("ia_dens_lama", 10.60))

            corredor_fundo = frac_atual - poro_atual
            overbalance_lama = dens_lama - poro_atual
            margem_fratura_lama = frac_atual - dens_lama

            st.markdown(f"""
            <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 12px 14px; margin-top: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.83rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #f59e0b;">Grad. Poro (Base): <b>{poro_atual:.2f} ppg</b></span>
                    <span style="color: #ef4444;">Grad. Fratura (Base): <b>{frac_atual:.2f} ppg</b></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; color: #cbd5e1;">
                    <span>Lama no Poço: <b>{dens_lama:.2f} ppg</b></span>
                    <span style="color: {'#10b981' if overbalance_lama >= 0.3 else '#ef4444'};">Overbalance: <b>{'+' if overbalance_lama>=0 else ''}{overbalance_lama:.2f} ppg</b></span>
                </div>
                <div style="display: flex; justify-content: space-between; color: #64748b; font-size: 0.76rem;">
                    <span>Corredor Geomecânico: <b>{corredor_fundo:.2f} ppg</b></span>
                    <span>Margem Frat. Lama: <b>+{margem_fratura_lama:.2f} ppg</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("💡 *Para ajustar as pressões de poro, fratura ou densidade da lama, utilize o painel da **Aba 3 (Módulo Especialista)**.*")

    with col_banco:
        # 3. Gestão e Auditoria do Catálogo de Aditivos
        with st.container(border=True):
            st.markdown("##### 🧪 Catálogo de Aditivos Homologados")
            st.caption("Base de dados com gravidades específicas ($SG$), tipos e categorias funcionais (Bourgoyne et al., Cap. 3):")

            df_aditivos = AditivoService.obter_dataframe(aditivos_db)
            st.dataframe(
                df_aditivos,
                hide_index=True,
                width="stretch",
                height=265
            )

            with st.expander("➕ Homologar Novo Aditivo no Catálogo"):
                with st.form("form_novo_aditivo"):
                    c_n1, c_n2 = st.columns(2)
                    with c_n1:
                        nome_novo = st.text_input("Nome Comercial do Aditivo:")
                        dens_nova = st.number_input("Gravidade Específica (SG):", min_value=0.5, max_value=6.0, value=2.5, step=0.01)
                    with c_n2:
                        tipo_novo = st.selectbox("Tipo Físico:", ["solido", "liquido", "salmoura"])
                        cat_nova = st.selectbox("Categoria Funcional:", CATEGORIAS_ADITIVOS)
                    
                    dosagem_nova = st.text_input("Dosagem Típica:", placeholder="Ex: 0.2 a 0.5% BWOC")
                    indicacao_nova = st.text_input("Indicação Operacional:", placeholder="Ex: Controle de reologia e perda de carga")
                    
                    submitted = st.form_submit_button("Cadastrar Aditivo", type="primary")
                    if submitted and nome_novo:
                        aditivos_db[nome_novo] = {
                            'densidade': dens_nova,
                            'tipo': tipo_novo,
                            'categoria': cat_nova,
                            'dosagem_tipica': dosagem_nova,
                            'indicacao': indicacao_nova
                        }
                        AditivoService.salvar_banco(aditivos_db)
                        st.success(f"Aditivo '{nome_novo}' cadastrado com sucesso!")
                        st.rerun()

            col_rst, _ = st.columns([1.5, 1])
            with col_rst:
                if st.button("🔄 Restaurar Catálogo Padrão", help="Restaura os 26 aditivos canônicos do Bourgoyne et al."):
                    aditivos_db = AditivoService.restaurar_padrao()
                    st.success("Catálogo padrão restaurado com sucesso!")
                    st.rerun()

    parametros = {
        'd_broca': d_broca,
        'd_ext': d_ext,
        'd_int': d_int,
        'fator_excesso': fator_excesso,
        'dist_sapata': dist_sapata,
        'dens_lama': dens_lama
    }

    return parametros, aditivos_db
