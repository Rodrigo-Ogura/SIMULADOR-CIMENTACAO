"""
Componente visual para Gestão e Visualização da Janela Geomecânica com Perfis Reais.
Interface de Alta Fidelidade — Estilo OpenLab Drilling (NORCE).
Permite carregar poços históricos do Mar do Norte ou importar arquivos CSV personalizados.
"""

import streamlit as st
import pandas as pd
from src.services.geomecanica_service import GeomecanicaService
from src.utils.logger import logger


def render_tab_geomecanica():
    """
    Renderiza a 1ª Aba: Módulo de Janela Geomecânica e Dados de Entrada.
    """
    st.markdown("### 🌐 Janela Geomecânica & Dados de Entrada do Poço")
    st.caption(
        "Ponto de partida do planejamento de poço: importe um perfil contínuo via CSV "
        "ou selecione um dos poços históricos calibrados para alimentar a Geometria (Aba 2), "
        "o Módulo Especialista de IA (Aba 3) e o Dashboard Final (Aba 5)."
    )

    # 1. Painel de Entrada de Dados (Presets ou Upload de CSV)
    with st.container(border=True):
        col_opc1, col_opc2 = st.columns([1.1, 1], gap="large")

        with col_opc1:
            st.markdown("##### 📚 1. Poços Históricos Calibrados (Mar do Norte)")
            st.caption("Perfis geomecânicos completos do Bloco 15/9 (Equinor / Sodir FactPages):")

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                pocos_disp = GeomecanicaService.listar_pocos_presets()
                poco_selecionado = st.selectbox(
                    "Selecione o Poço:",
                    options=pocos_disp,
                    index=0,
                    key="sb_geomec_poco",
                    help="Poços offshore da bacia do Mar do Norte (Noruega)."
                )
            with c_p2:
                variantes_dict = GeomecanicaService.listar_variantes()
                var_keys = list(variantes_dict.keys())
                variante_selecionada = st.selectbox(
                    "Variante de Modelagem:",
                    options=var_keys,
                    format_func=lambda k: variantes_dict[k],
                    index=0,
                    key="sb_geomec_variante",
                    help="B = Calibrada com histórico de lama; A = Teórica; K = Calibração regional sintética."
                )

            btn_carregar_preset = st.button("📥 Carregar Poço Histórico", key="btn_load_preset", type="primary")

            if btn_carregar_preset:
                df_preset = GeomecanicaService.carregar_preset(poco_selecionado, variante_selecionada)
                if df_preset is not None:
                    st.session_state["perfil_geomecanico_ativo"] = df_preset
                    st.session_state["fonte_geomecanica_ativa"] = f"Poço {poco_selecionado} (Var. {variante_selecionada})"
                    st.session_state["metadados_geomecanicos_ativos"] = GeomecanicaService.obter_metadados_poco_preset(poco_selecionado)
                    st.success(f"✅ Perfil do **Poço {poco_selecionado} ({variante_selecionada})** carregado e ativo no simulador!")
                else:
                    st.error("Não foi possível carregar o arquivo do poço selecionado.")

        with col_opc2:
            st.markdown("##### 📤 2. Importar Arquivo CSV Personalizado")
            st.caption("Suba um arquivo CSV contendo profundidades e gradientes (ppg):")

            arquivo_csv = st.file_uploader(
                "Selecione o CSV do perfil geomecânico:",
                type=["csv", "txt"],
                key="uploader_csv_geomecanica",
                help="O arquivo deve conter colunas de Profundidade e ao menos um gradiente (Poro, Fratura, Colapso ou Sobrecarga)."
            )

            c_u1, c_u2 = st.columns(2)
            with c_u1:
                unidade_prof = st.radio(
                    "Unidade de Profundidade no CSV:",
                    options=["Metros (m)", "Pés (ft)"],
                    index=0,
                    horizontal=True,
                    key="radio_unidade_prof_csv"
                )
            with c_u2:
                btn_processar_upload = st.button("🚀 Processar & Ativar CSV", key="btn_process_csv", type="secondary", use_container_width=True)

            if btn_processar_upload and arquivo_csv is not None:
                unidade_str = "ft" if "Pés" in unidade_prof else "m"
                sucesso, df_upload, msg = GeomecanicaService.processar_csv_upload(
                    arquivo_csv,
                    unidade_prof_entrada=unidade_str,
                    nome_arquivo=arquivo_csv.name
                )
                if sucesso and df_upload is not None:
                    st.session_state["perfil_geomecanico_ativo"] = df_upload
                    st.session_state["fonte_geomecanica_ativa"] = f"Upload: {arquivo_csv.name}"
                    st.session_state.pop("metadados_geomecanicos_ativos", None)
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

            # Botão para baixar modelo pronto e formatado para testes
            df_modelo = GeomecanicaService.carregar_preset("15/9-13", "B")
            if df_modelo is not None:
                cols_modelo = [c for c in ["prof_m", "poro_ppg", "fratura_ppg", "colapso_ppg", "sobrecarga_ppg"] if c in df_modelo.columns]
                df_exemplo = df_modelo[cols_modelo].rename(columns={
                    "prof_m": "Profundidade_m",
                    "poro_ppg": "Gradiente_Poros_ppg",
                    "fratura_ppg": "Gradiente_Fratura_ppg",
                    "colapso_ppg": "Gradiente_Colapso_ppg",
                    "sobrecarga_ppg": "Gradiente_Sobrecarga_ppg"
                })
                csv_buffer = df_exemplo.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📄 Baixar Modelo CSV de Exemplo",
                    data=csv_buffer,
                    file_name="modelo_perfil_geomecanico.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="Baixe este modelo pré-formatado para abrir no Excel, inspecionar as colunas e testar o upload."
                )

    # 2. Verificação do Perfil Ativo
    perfil_ativo: pd.DataFrame = st.session_state.get("perfil_geomecanico_ativo", None)

    if perfil_ativo is None:
        st.info("ℹ️ Nenhum perfil geomecânico real ativo no momento. Selecione um dos poços do Mar do Norte acima ou faça o upload de um CSV para iniciar.")
        return

    # Extrai métricas
    metricas = GeomecanicaService.extrair_metricas_resumo(perfil_ativo)
    fonte_nome = st.session_state.get("fonte_geomecanica_ativa", perfil_ativo.attrs.get("nome_fonte", "Perfil"))
    meta_extra = st.session_state.get("metadados_geomecanicos_ativos", {})

    st.markdown("---")
    st.markdown(f"#### 📊 Resumo Executivo do Perfil Ativo: `{fonte_nome}`")

    # 3. Cartões de Métricas Industriais (SCADA)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Profundidade Máxima (TD)",
            f"{metricas['prof_max_m']:,.0f} m",
            f"{metricas['prof_max_ft']:,.0f} ft (TVD)"
        )
    with c2:
        st.metric(
            "Janela Mínima (Gargalo)",
            f"{metricas['largura_min_ppg']:.2f} ppg",
            f"Prof: {metricas['ponto_critico'].get('prof_m', 0):.0f} m"
        )
    with c3:
        st.metric(
            "Largura Média da Janela",
            f"{metricas['largura_media_ppg']:.2f} ppg",
            f"{metricas['total_pontos']} profundidades"
        )
    with c4:
        st.metric(
            "Limites no Fundo",
            f"Frat: {metricas.get('fratura_min_ppg', 0):.2f} ppg",
            f"Poro: {metricas.get('poro_max_ppg', 0):.2f} ppg"
        )

    # 4. Banner explicativo do pipeline
    st.markdown(f"""
    <div style="background-color: #0f172a; border: 1px solid #1e293b; border-left: 4px solid #38bdf8; border-radius: 6px; padding: 12px 18px; margin: 15px 0;">
        <div style="font-weight: 700; color: #38bdf8; font-size: 0.92rem; margin-bottom: 3px;">
            📍 PIPELINE DE ENGENHARIA CONECTADO
        </div>
        <div style="color: #cbd5e1; font-size: 0.86rem; line-height: 1.5;">
            Os dados deste perfil (TD: <b>{metricas['prof_max_m']:.0f} m</b>, Poro: <b>{metricas['poro_max_ppg']:.2f} ppg</b>, Fratura: <b>{metricas['fratura_min_ppg']:.2f} ppg</b>) 
            já estão prontos para abastecer a <b>Aba 2 (Geometria)</b> e a <b>Aba 3 (Módulo Especialista IA)</b>.<br>
            As <b>curvas geomecânicas contínuas</b> serão plotadas em alta resolução na <b>Aba 5 (Dashboard)</b> confrontadas em tempo real com a coluna de cimento.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Tabela de Amostragem dos Dados com Download
    with st.expander("📋 Ver Tabela de Dados e Exportar Perfil"):
        st.dataframe(perfil_ativo, hide_index=True, use_container_width=True)
        csv_bytes = perfil_ativo.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Dados do Perfil (.csv)",
            data=csv_bytes,
            file_name=f"perfil_{fonte_nome.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
