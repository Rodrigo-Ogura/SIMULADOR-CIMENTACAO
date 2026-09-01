"""
Componente visual da barra lateral (Sidebar) do Streamlit.
"""

import streamlit as st
from typing import Dict, Tuple
from src.services.aditivo_service import AditivoService


def render_sidebar() -> Tuple[Dict[str, float], Dict[str, dict]]:
    """
    Renderiza os parâmetros do poço e o cadastro de aditivos na barra lateral.
    Retorna uma tupla contendo os parâmetros do poço e o dicionário de aditivos atualizado.
    """
    with st.sidebar:
        st.header("⚙️ Parâmetros do Poço")
        d_broca = st.number_input("Diâmetro da Broca (in)", value=12.250, format="%.3f", step=0.125)
        d_ext = st.number_input("Diâmetro Externo Revestimento (in)", value=9.625, format="%.3f", step=0.125)
        d_int = st.number_input("Diâmetro Interno Revestimento (in)", value=8.835, format="%.3f", step=0.125)
        fator_excesso = st.number_input("Fator de Excesso (ex: 1.20 para 20%)", value=1.20, format="%.2f", step=0.05)
        dist_sapata = st.number_input("Distância Colar-Sapata (ft)", value=40.0, format="%.1f", step=5.0)

        st.divider()

        st.header("🧪 Criar Novo Aditivo")
        novo_nome = st.text_input("Nome do Aditivo")
        nova_categoria = st.selectbox("Categoria Funcional", [
            "Densificante",
            "Extensor",
            "Acelerador",
            "Retardador",
            "Dispersante",
            "Controlador de Filtrado",
            "Perda de Circulação (LCM)",
            "Especial / Outro"
        ])
        nova_densidade = st.number_input("Densidade Relativa", value=1.00, format="%.2f", step=0.05)
        novo_tipo = st.selectbox("Tipo de Mistura", ["solido", "salmoura"])

        if st.button("Adicionar ao Banco (Salvar Permanente)"):
            if novo_nome:
                st.session_state.aditivos_db = AditivoService.salvar_aditivo(
                    novo_nome, nova_densidade, novo_tipo, nova_categoria
                )
                st.success(f"'{novo_nome}' salvo permanentemente no banco!")
                st.rerun()
            else:
                st.warning("Preencha o nome do aditivo.")

    params_poco = {
        'd_broca': d_broca,
        'd_ext': d_ext,
        'd_int': d_int,
        'fator_excesso': fator_excesso,
        'dist_sapata': dist_sapata
    }

    return params_poco, st.session_state.aditivos_db
