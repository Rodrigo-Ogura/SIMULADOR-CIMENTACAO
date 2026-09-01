"""
Componente visual para configuração das pastas de cimento e dosagem de aditivos (% BWOC).
Estilo OpenLab Drilling (NORCE).
"""

import streamlit as st
from typing import List, Dict
from config import VOLUME_AGUA_POR_CLASSE, CATEGORIAS_ADITIVOS
from src.models.pasta import ConfigPasta


def render_config_pastas(aditivos_db: Dict[str, dict]) -> List[ConfigPasta]:
    """
    Renderiza o formulário de engenharia para configuração de pastas múltiplas e dosagem estequiométrica.
    """
    st.markdown("### 🧪 Formulação & Configuração das Pastas de Cimento")
    st.caption("Especifique a classe API do cimento, altura anular e dosagens percentuais em relação ao peso de cimento (% BWOC):")
    
    col_qp, col_info = st.columns([1.2, 2.8])
    with col_qp:
        quantidade_pastas = st.number_input(
            "Número de Pastas no Anular:",
            min_value=1,
            max_value=4,
            value=1,
            step=1,
            help="1 = Pasta Única; 2 = Lead e Tail; 3 ou 4 = Múltiplos estágios."
        )

    with col_info:
        if quantidade_pastas > 1:
            st.markdown("""
            <div style="background-color: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 8px 14px; margin-top: 18px;">
                <span style="color: #38bdf8; font-weight: 600; font-size: 0.85rem;">ℹ️ CONVENÇÃO DE POÇO:</span>
                <span style="color: #94a3b8; font-size: 0.85rem;">As pastas são empilhadas de baixo para cima (Pasta 1 = Sapata/Fundo; Pasta N = Topo/Superfície).</span>
            </div>
            """, unsafe_allow_html=True)

    abas = st.tabs([f"📦 Pasta {i} ({'Sapata / Tail' if i == 1 else f'Lead {i-1}'})" for i in range(1, quantidade_pastas + 1)])
    pastas_configuradas = []

    # Cores funcionais por categoria
    cores_categorias = {
        "Densificante": "🟢",
        "Extensor": "🟡",
        "Acelerador": "🔵",
        "Retardador": "🔴",
        "Dispersante": "🟣",
        "Controlador de Filtrado": "🟤",
        "Perda de Circulação (LCM)": "🟠",
        "Especial / Outro": "⚪"
    }

    # Callback para manter a persistência ao trocar de filtro
    def toggle_aditivo_estado(pasta_id: int, adit_nome: str, chave_widget: str):
        if st.session_state.get(chave_widget, False):
            st.session_state[f"aditivos_selecionados_{pasta_id}"].add(adit_nome)
        else:
            st.session_state[f"aditivos_selecionados_{pasta_id}"].discard(adit_nome)

    for idx, aba in enumerate(abas, start=1):
        if f"aditivos_selecionados_{idx}" not in st.session_state:
            st.session_state[f"aditivos_selecionados_{idx}"] = set()

        with aba:
            with st.container(border=True):
                st.markdown(f"##### ⚙️ Parâmetros Básicos — Pasta {idx}")
                
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    dist_fundo = st.number_input(
                        "Altura da Seção no Anular (ft):",
                        value=1000.0 if idx == 1 else 500.0,
                        format="%.1f",
                        step=100.0,
                        key=f"dist_{idx}",
                        help="Comprimento vertical preenchido por esta pasta no anular."
                    )
                with c_p2:
                    classe_cimento = st.selectbox(
                        "Classe do Cimento API (Spec 10A):",
                        list(VOLUME_AGUA_POR_CLASSE.keys()),
                        index=7 if idx == 1 else 2,
                        key=f"classe_{idx}",
                        help="Classe Portland homologada para poços (Classe G é o padrão internacional)."
                    )

                fator_agua_padrao = VOLUME_AGUA_POR_CLASSE[classe_cimento]
                c_chk, c_ag = st.columns([1.2, 1])
                with c_chk:
                    usar_custom_agua = st.checkbox("Personalizar fator Água-Cimento?", value=False, key=f"chk_agua_{idx}")

                if usar_custom_agua:
                    with c_ag:
                        fator_agua_cimento = st.number_input(
                            "Água por Saco (gal/sk):",
                            min_value=0.1,
                            value=float(fator_agua_padrao),
                            format="%.2f",
                            step=0.1,
                            key=f"agua_{idx}"
                        )
                else:
                    fator_agua_cimento = 0.0
                    st.caption(f"Água padrão API para Classe {classe_cimento}: **{fator_agua_padrao:.2f} gal/sk** ({fator_agua_padrao*8.33/94*100:.1f}% w/c)")

            # --- SELEÇÃO DE ADITIVOS ---
            st.markdown(f"##### 🧪 Seleção de Aditivos Químicos — Pasta {idx}")

            # Filtro por categoria
            opcoes_filtro = ["🌟 Todos"] + [f"{cores_categorias.get(c, '📁')} {c}" for c in CATEGORIAS_ADITIVOS]
            filtro_selecionado = st.pills(
                "Filtrar por Categoria:",
                opcoes_filtro,
                default="🌟 Todos",
                key=f"pills_filtro_{idx}"
            )

            if filtro_selecionado == "🌟 Todos":
                cat_alvo = None
                sufixo_filtro = "todos"
            else:
                cat_alvo = filtro_selecionado.split(" ", 1)[1] if " " in filtro_selecionado else filtro_selecionado
                sufixo_filtro = cat_alvo.replace(" ", "_").replace("/", "_")

            if cat_alvo:
                aditivos_visiveis = {k: v for k, v in aditivos_db.items() if v.get("categoria") == cat_alvo}
            else:
                aditivos_visiveis = aditivos_db

            with st.container(border=True):
                cols_adit = st.columns(2)
                for i, (nome_adit, info_adit) in enumerate(aditivos_visiveis.items()):
                    cat = info_adit.get("categoria", "Especial / Outro")
                    icone = cores_categorias.get(cat, "📁")
                    dens = info_adit.get("densidade", 1.0)
                    tipo = info_adit.get("tipo", "solido")
                    
                    esta_selecionado = nome_adit in st.session_state[f"aditivos_selecionados_{idx}"]
                    chave_chk = f"chk_adit_{idx}_{sufixo_filtro}_{nome_adit}"

                    with cols_adit[i % 2]:
                        st.checkbox(
                            f"{icone} **{nome_adit}** (`SG {dens:.2f}` · {tipo})",
                            value=esta_selecionado,
                            key=chave_chk,
                            on_change=toggle_aditivo_estado,
                            args=(idx, nome_adit, chave_chk),
                            help=f"Categoria: {cat} | Gravidade Específica: {dens:.2f} | Tipo: {tipo}"
                        )

            # --- DOSAGENS ---
            aditivos_ativos = [
                nome for nome in aditivos_db.keys() if nome in st.session_state[f"aditivos_selecionados_{idx}"]
            ]

            porcentagens = {}
            if aditivos_ativos:
                st.markdown(f"##### 📋 Dosagem Estequiométrica (% BWOC) — {len(aditivos_ativos)} aditivo(s) ativo(s)")
                cols_dosagem = st.columns(min(len(aditivos_ativos), 2))
                
                for i, aditivo in enumerate(aditivos_ativos):
                    info = aditivos_db[aditivo]
                    cat = info.get("categoria", "Outro")
                    icone = cores_categorias.get(cat, "📁")

                    with cols_dosagem[i % 2]:
                        c_num, c_btn = st.columns([5, 1])
                        with c_num:
                            porcentagens[aditivo] = st.number_input(
                                f"{icone} {aditivo} (% BWOC):",
                                min_value=0.0,
                                value=st.session_state.get(f"pct_{aditivo}_{idx}", 2.0),
                                format="%.2f",
                                step=0.5,
                                key=f"pct_{aditivo}_{idx}"
                            )
                        with c_btn:
                            st.write("")
                            st.write("")
                            if st.button("🗑️", key=f"btn_remover_{idx}_{aditivo}", help=f"Remover {aditivo}"):
                                st.session_state[f"aditivos_selecionados_{idx}"].discard(aditivo)
                                st.rerun()
            else:
                st.info("Nenhum aditivo selecionado para esta seção (Pasta de cimento puro).")

            pastas_configuradas.append(ConfigPasta(
                numero=idx,
                dist_fundo=dist_fundo,
                classe=classe_cimento,
                fator_agua_cimento=fator_agua_cimento,
                porcentagens=porcentagens
            ))

    return pastas_configuradas
