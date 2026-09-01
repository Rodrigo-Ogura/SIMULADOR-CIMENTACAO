"""
Módulo Especialista de Formulação de Pastas & Assistência de Engenharia.
Interface de Alta Fidelidade — Estilo OpenLab Drilling (NORCE).
Suporta Recomendação de Programa Completo (Lead + Tail) e Pastas Individuais
com Groq Cloud LPU API e Ollama Local sob Guardrails Determinísticos e Físico-Químicos
de Deslocamento de Lama (API Spec 10A/10B, Bourgoyne et al. Cap. 3, Nelson & Guillot).
"""

import streamlit as st
from typing import Dict, Any, Tuple, Optional
import config
from config import (
    GROQ_DEFAULT_MODEL,
    GROQ_MODELS,
    OLLAMA_DEFAULT_MODEL,
    OLLAMA_BASE_URL,
)
from src.services.groq_agent_service import verificar_status_groq, recomendar_formulacao_groq
from src.services.ollama_agent_service import verificar_status_ollama, recomendar_formulacao


def render_tab_agente_ia(aditivos_db: Dict[str, dict], total_pastas: int = 2):
    """
    Renderiza o módulo especialista de formulação e auditoria de requisitos de cimentação.
    """
    st.markdown("### 🧠 Módulo Especialista de Formulação & Otimização de Pastas")
    st.caption(
        "Sistema especialista de apoio à decisão operacional baseado em Large Language Models e **Guardrails Determinísticos de Engenharia**, "
        "dimensionando programas completos de cimentação (**Lead Slurry + Tail Slurry**), avaliando a **Lama de Perfuração** e eficiência de deslocamento "
        "sob restrições geomecânicas e térmicas (API Spec 10A/10B, Bourgoyne et al., Nelson & Guillot)."
    )

    # 1. Painel de Conectividade do Motor de Inferência (LPU / Local)
    with st.container(border=True):
        col_prov1, col_prov2 = st.columns([1.3, 2.7])
        with col_prov1:
            st.markdown("##### 🔌 Motor de Inferência")
            provedor_ia = st.radio(
                "Selecione a Infraestrutura de Execução:",
                [
                    "☁️ Groq Cloud LPU (Nuvem - Rápido)",
                    "🖥️ Ollama Engine (Local - Offline)"
                ],
                key="radio_provedor_ia",
                help="Groq Cloud processa via LPUs na nuvem com modelos de ponta em milissegundos. Ollama executa localmente no seu computador sem conexão à internet."
            )
        
        with col_prov2:
            st.markdown("##### 📊 Telemetria de Conexão & Modelo")
            if "Groq" in provedor_ia:
                # Obtém chave configurada via st.secrets, .env ou digitada na UI
                chave_configurada = (
                    st.session_state.get("user_groq_api_key", "")
                    or getattr(config, "GROQ_API_KEY", "")
                )
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    chave_configurada = chave_configurada or str(st.secrets["GROQ_API_KEY"]).strip()
                
                if not chave_configurada:
                    user_key = st.text_input(
                        "🔑 Chave de API Groq (GROQ_API_KEY):",
                        value=st.session_state.get("user_groq_api_key", ""),
                        type="password",
                        placeholder="gsk_...",
                        help="Gere uma chave gratuita em console.groq.com/keys",
                        key="input_groq_key"
                    )
                    if user_key:
                        st.session_state["user_groq_api_key"] = user_key.strip()
                        chave_configurada = user_key.strip()

                online_groq, modelos_groq, msg_groq = verificar_status_groq(chave_configurada)
                
                col_g1, col_g2 = st.columns([1.2, 2])
                with col_g1:
                    if online_groq:
                        st.markdown("""
                        <div style="background-color: #064e3b; border: 1px solid #059669; border-radius: 6px; padding: 8px 12px; margin-top: 5px;">
                            <span style="color: #34d399; font-weight: 700; font-size: 0.85rem; font-family: 'JetBrains Mono';">🟢 GROQ LPU ONLINE</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background-color: #450a0a; border: 1px solid #dc2626; border-radius: 6px; padding: 8px 12px; margin-top: 5px;">
                            <span style="color: #f87171; font-weight: 700; font-size: 0.85rem; font-family: 'JetBrains Mono';">🔴 GROQ OFFLINE</span>
                        </div>
                        """, unsafe_allow_html=True)
                with col_g2:
                    opcoes_modelos = modelos_groq or GROQ_MODELS
                    modelo_atual_salvo = st.session_state.get("select_modelo_groq", "")
                    idx_inicial = opcoes_modelos.index(modelo_atual_salvo) if modelo_atual_salvo in opcoes_modelos else 0
                    
                    modelo_selecionado = st.selectbox(
                        "Modelo LLM Alocado:",
                        opcoes_modelos,
                        index=idx_inicial,
                        key="select_modelo_groq"
                    )
            else:
                online_ollama, modelos_ollama, msg_ollama = verificar_status_ollama()
                
                col_o1, col_o2 = st.columns([1.2, 2])
                with col_o1:
                    if online_ollama:
                        st.markdown("""
                        <div style="background-color: #064e3b; border: 1px solid #059669; border-radius: 6px; padding: 8px 12px; margin-top: 5px;">
                            <span style="color: #34d399; font-weight: 700; font-size: 0.85rem; font-family: 'JetBrains Mono';">🟢 OLLAMA REST ONLINE</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background-color: #450a0a; border: 1px solid #dc2626; border-radius: 6px; padding: 8px 12px; margin-top: 5px;">
                            <span style="color: #f87171; font-weight: 700; font-size: 0.85rem; font-family: 'JetBrains Mono';">🔴 OLLAMA OFFLINE</span>
                        </div>
                        """, unsafe_allow_html=True)
                with col_o2:
                    if online_ollama and modelos_ollama:
                        modelo_selecionado = st.selectbox(
                            "Modelo Local:",
                            modelos_ollama,
                            index=0,
                            key="select_modelo_ollama"
                        )
                    else:
                        st.caption("Inicie o serviço Ollama (`ollama run llama3.1`)")
                        modelo_selecionado = OLLAMA_DEFAULT_MODEL

    # 2. Condições de Contorno e Geomecânica do Poço
    st.markdown("---")
    st.markdown("##### 📋 Condições de Contorno Operacionais, Geomecânica & Perfil Térmico")

    def _atualizar_preset_callback():
        preset_sel = st.session_state.get("preset_cenario_poco", "")
        if preset_sel.startswith("🔥"):
            st.session_state["ia_topo"] = 1800.0
            st.session_state["ia_base"] = 3200.0
            st.session_state["ia_poro"] = 10.2
            st.session_state["ia_frac"] = 16.8
            st.session_state["ia_dens_lama"] = 10.60
            st.session_state["ia_dmin"] = 15.6
            st.session_state["ia_dmax"] = 16.2
            st.session_state["ia_bhst"] = 115.0
            st.session_state["ia_bhct"] = 75.0
            st.session_state["ia_tbomb"] = 150
            st.session_state["ia_perm"] = True
            st.session_state["ia_gas"] = False
            st.session_state["ia_lcm"] = False
            st.session_state["ia_obs"] = "Formação arenosa profunda de alta temperatura com risco de degradação térmica e perda de filtrado."
        elif preset_sel.startswith("⚠️"):
            st.session_state["ia_topo"] = 1200.0
            st.session_state["ia_base"] = 2400.0
            st.session_state["ia_poro"] = 11.5
            st.session_state["ia_frac"] = 14.5
            st.session_state["ia_dens_lama"] = 11.90
            st.session_state["ia_dmin"] = 13.0
            st.session_state["ia_dmax"] = 13.8
            st.session_state["ia_bhst"] = 70.0
            st.session_state["ia_bhct"] = 50.0
            st.session_state["ia_tbomb"] = 120
            st.session_state["ia_perm"] = True
            st.session_state["ia_gas"] = True
            st.session_state["ia_lcm"] = False
            st.session_state["ia_obs"] = "Janela operacional estreita com formação gasífera sob pressão."
        elif preset_sel.startswith("❄️"):
            st.session_state["ia_topo"] = 200.0
            st.session_state["ia_base"] = 900.0
            st.session_state["ia_poro"] = 8.6
            st.session_state["ia_frac"] = 13.5
            st.session_state["ia_dens_lama"] = 9.00
            st.session_state["ia_dmin"] = 12.0
            st.session_state["ia_dmax"] = 13.0
            st.session_state["ia_bhst"] = 30.0
            st.session_state["ia_bhct"] = 18.0
            st.session_state["ia_tbomb"] = 60
            st.session_state["ia_perm"] = False
            st.session_state["ia_gas"] = False
            st.session_state["ia_lcm"] = False
            st.session_state["ia_obs"] = "Cimentação de revestimento condutor/superfície em águas rasas e baixas temperaturas."

    if "ia_topo" not in st.session_state:
        st.session_state["preset_cenario_poco"] = "🔥 Poço Profundo & Alta Temperatura (BHCT 75°C, BHST 115°C, Permeável)"
        _atualizar_preset_callback()

    c_pre, c_alvo = st.columns([1.8, 1.4])
    with c_pre:
        preset = st.selectbox(
            "Carregar Template / Benchmark Canônico:",
            [
                "🔥 Poço Profundo & Alta Temperatura (BHCT 75°C, BHST 115°C, Permeável)",
                "⚠️ Poço com Janela Estreita & Risco de Gás (BHCT 55°C, Gás)",
                "❄️ Seção Rasa / Baixa Temperatura (BHCT 20°C, Baixa Pressão)",
                "Personalizado (Definição Manual)"
            ],
            key="preset_cenario_poco",
            on_change=_atualizar_preset_callback
        )
    with c_alvo:
        estrategia_ia = st.selectbox(
            "Estratégia de Cimentação:",
            [
                "🎯 Programa Completo: Lead Slurry (Topo) + Tail Slurry (Fundo)",
                "🧪 Pasta Individual: Tail Slurry (Sapata / Fundo)",
                "🧪 Pasta Individual: Lead Slurry (Preenchimento / Topo)"
            ],
            key="ia_estrategia_selecionada"
        )

    with st.container(border=True):
        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            prof_topo = st.number_input("Profundidade Topo (m):", step=100.0, key="ia_topo")
            prof_base = st.number_input("Profundidade Base (m):", step=100.0, key="ia_base")
            tempo_bombeio = st.number_input("Tempo de Bombeio Previsto (min):", step=15, key="ia_tbomb")

        with c_d2:
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                grad_poro = st.number_input("Grad. Poro (ppg):", step=0.1, key="ia_poro")
            with c_p2:
                grad_frac = st.number_input("Grad. Fratura (ppg):", step=0.1, key="ia_frac")
            
            dens_lama = st.number_input("Densidade da Lama de Perfuração (ppg):", step=0.1, key="ia_dens_lama", help="Fluido atualmente no poço. Deve garantir overbalance sobre o poro e ser deslocado pelo cimento.")

            c_dmin, c_dmax = st.columns(2)
            with c_dmin:
                dens_min = st.number_input("Dens. Mín Tail (ppg):", step=0.1, key="ia_dmin")
            with c_dmax:
                dens_max = st.number_input("Dens. Máx Tail (ppg):", step=0.1, key="ia_dmax")

        with c_d3:
            bhst = st.number_input("Temp. Estática (BHST °C):", step=5.0, key="ia_bhst")
            bhct = st.number_input("Temp. Circulante (BHCT °C):", step=5.0, key="ia_bhct")
            chk_reologia = st.checkbox("Reologia Crítica / Alta Perda de Carga", key="ia_reologia")

        st.markdown("**Matriz de Riscos & Condições Geológicas:**")
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1:
            chk_perm = st.checkbox("Formação Permeável (Filtrado)", key="ia_perm")
        with c_r2:
            chk_gas = st.checkbox("Potencial de Gás (Migração)", key="ia_gas")
        with c_r3:
            chk_lcm = st.checkbox("Risco de Perda de Circulação Natural", key="ia_lcm")

        obs_texto = st.text_input("Observações Geomecânicas Complementares:", key="ia_obs")

    # Botão de Execução do Agente Especialista
    st.write("")
    col_btn1, _ = st.columns([1.8, 1.7])
    with col_btn1:
        gerar_clicked = st.button("🧠 **Executar Dimensionamento Especialista**", type="primary", use_container_width=True)

    def _executar_ia(dados_entrada: dict, tipo_alvo: str) -> Tuple[bool, Optional[dict], str]:
        if "Groq" in provedor_ia:
            chave_usada = (
                st.session_state.get("user_groq_api_key", "")
                or getattr(config, "GROQ_API_KEY", "")
            )
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                chave_usada = chave_usada or str(st.secrets["GROQ_API_KEY"]).strip()

            return recomendar_formulacao_groq(
                dados_poco=dados_entrada,
                catalogo_aditivos=aditivos_db,
                tipo_pasta=tipo_alvo,
                modelo=modelo_selecionado,
                api_key=chave_usada
            )
        else:
            return recomendar_formulacao(
                dados_poco=dados_entrada,
                catalogo_aditivos=aditivos_db,
                tipo_pasta=tipo_alvo,
                modelo=modelo_selecionado
            )

    if gerar_clicked:
        is_programa_completo = "Programa Completo" in estrategia_ia

        if is_programa_completo:
            with st.spinner(f"Dimensionando Programa Completo (Lead + Tail Slurry) com {modelo_selecionado}..."):
                # 1. Pasta 1: Tail Slurry (Sapata / Fundo)
                dados_tail = {
                    'prof_topo': prof_topo + (prof_base - prof_topo) * 0.7 if prof_base > prof_topo else prof_topo,
                    'prof_base': prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': dens_min,
                    'densidade_max_alvo': dens_max,
                    'bhst_c': bhst,
                    'bhct_c': bhct,
                    'tempo_bombeio_min': tempo_bombeio,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': chk_gas,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Pasta de Sapata/Fundo (Tail). Lama no poço: {dens_lama:.2f} ppg. {obs_texto}"
                }
                suc_tail, res_tail, msg_tail = _executar_ia(dados_tail, "Tail Slurry (Sapata / Fundo)")

                # 2. Pasta 2: Lead Slurry (Preenchimento / Topo)
                lead_grad_frac = max(14.0, grad_frac - 1.5)
                lead_grad_poro = min(max(8.5, grad_poro - 1.2), 9.0)
                lead_dmax = min(13.5, lead_grad_frac - 0.6)
                lead_dmin = max(11.8, min(12.5, lead_dmax - 1.0))

                dados_lead = {
                    'prof_topo': prof_topo,
                    'prof_base': prof_topo + (prof_base - prof_topo) * 0.7 if prof_base > prof_topo else prof_topo + 500.0,
                    'grad_poro': lead_grad_poro,
                    'grad_fratura': lead_grad_frac,
                    'dens_lama': min(dens_lama, lead_dmin - 0.5),
                    'densidade_min_alvo': lead_dmin,
                    'densidade_max_alvo': lead_dmax,
                    'bhst_c': max(35.0, bhst * 0.70),
                    'bhct_c': max(25.0, bhct * 0.65),
                    'tempo_bombeio_min': tempo_bombeio + 30,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': False,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Pasta Leve de Preenchimento (Lead): proteger topo contra fratura. {obs_texto}"
                }
                suc_lead, res_lead, msg_lead = _executar_ia(dados_lead, "Lead Slurry (Preenchimento / Topo)")

            if suc_tail and suc_lead:
                st.session_state["programa_completo_ia"] = {"tail": res_tail, "lead": res_lead}
                st.session_state.pop("ultima_recomendacao_ia", None)
                st.success("✅ **Programa Completo (Lead + Tail Slurry) Aprovado com 100% de Conformidade nos Guardrails!**")
            else:
                erros = []
                if not suc_tail:
                    erros.append(f"• **Tail Slurry (Sapata / Fundo):** {msg_tail}")
                if not suc_lead:
                    erros.append(f"• **Lead Slurry (Preenchimento / Topo):** {msg_lead}")
                st.error("❌ Falha no dimensionamento do Programa Completo:\n\n" + "\n".join(erros))

        else:
            # Pasta Individual Selecionada
            tipo_alvo = "Tail Slurry (Sapata / Fundo)" if "Tail" in estrategia_ia else "Lead Slurry (Preenchimento / Topo)"
            with st.spinner(f"Dimensionando {tipo_alvo} com {modelo_selecionado}..."):
                dados_envio = {
                    'prof_topo': prof_topo,
                    'prof_base': prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': dens_min,
                    'densidade_max_alvo': dens_max,
                    'bhst_c': bhst,
                    'bhct_c': bhct,
                    'tempo_bombeio_min': tempo_bombeio,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': chk_gas,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': obs_texto
                }
                suc_ind, res_ind, msg_ind = _executar_ia(dados_envio, tipo_alvo)

            if suc_ind and res_ind:
                st.session_state["ultima_recomendacao_ia"] = res_ind
                st.session_state.pop("programa_completo_ia", None)
                st.success("✅ **Formulação Aprovada por Guardrails Determinísticos!**")
            else:
                st.error(f"❌ Falha de validação técnica: {msg_ind}")

    # Função Auxiliar de Aplicação de Formulação em uma Pasta
    def _aplicar_formulacao_em_pasta(idx_alvo: int, recomendacao: dict, banco_aditivos: dict):
        classe = recomendacao.get("classe_cimento", "G")
        st.session_state[f"classe_{idx_alvo}"] = classe
        
        if "agua_gal_sk" in recomendacao and recomendacao["agua_gal_sk"]:
            st.session_state[f"chk_agua_{idx_alvo}"] = True
            st.session_state[f"agua_{idx_alvo}"] = float(recomendacao["agua_gal_sk"])
        else:
            st.session_state[f"chk_agua_{idx_alvo}"] = False

        novos_selecionados = set()
        for ad in recomendacao.get("aditivos", []):
            nome_ad = ad.get("nome")
            conc = float(ad.get("concentracao", 0.0))
            if nome_ad in banco_aditivos:
                novos_selecionados.add(nome_ad)
                st.session_state[f"pct_{nome_ad}_{idx_alvo}"] = conc

        st.session_state[f"aditivos_selecionados_{idx_alvo}"] = novos_selecionados

        chaves_checkboxes = [k for k in list(st.session_state.keys()) if k.startswith(f"chk_adit_{idx_alvo}_")]
        for k in chaves_checkboxes:
            st.session_state.pop(k, None)

    # 3. EXIBIÇÃO DE PROGRAMA COMPLETO (LEAD + TAIL)
    if "programa_completo_ia" in st.session_state:
        prog = st.session_state["programa_completo_ia"]
        res_tail = prog["tail"]
        res_lead = prog["lead"]

        st.markdown("---")
        st.markdown("#### 🏆 Programa Completo de Cimentação Recomendado (Lead + Tail)")
        st.caption("Estratégia bi-pasta para isolamento de sapata e alívio da pressão anular sobre formações superiores:")

        col_c_lead, col_c_tail = st.columns(2, gap="large")

        # Card da Lead Slurry (Pasta 2 - Topo)
        with col_c_lead:
            with st.container(border=True):
                st.markdown("##### 📘 Pasta 2: Lead Slurry (Preenchimento / Topo)")
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("Densidade", f"{res_lead.get('densidade_alvo_ppg', 12.8):.2f} ppg")
                c_m2.metric("Classe API", f"Classe {res_lead.get('classe_cimento', 'G')}")
                c_m3.metric("Água Mistura", f"{res_lead.get('agua_gal_sk', 7.5):.2f} gal/sk")
                
                st.markdown(f"**Parecer do Especialista:**\n> *{res_lead.get('parecer_tecnico', '')}*")
                
                st.markdown("**Aditivos Selecionados:**")
                for ad in res_lead.get("aditivos", []):
                    st.markdown(f"- **{ad.get('nome')}**: `{ad.get('concentracao', 0.0):.2f}% BWOC` — *{ad.get('justificativa', '')}*")

        # Card da Tail Slurry (Pasta 1 - Fundo)
        with col_c_tail:
            with st.container(border=True):
                st.markdown("##### 📙 Pasta 1: Tail Slurry (Sapata / Fundo)")
                c_t1, c_t2, c_t3 = st.columns(3)
                c_t1.metric("Densidade", f"{res_tail.get('densidade_alvo_ppg', 16.0):.2f} ppg")
                c_t2.metric("Classe API", f"Classe {res_tail.get('classe_cimento', 'G')}")
                c_t3.metric("Água Mistura", f"{res_tail.get('agua_gal_sk', 5.0):.2f} gal/sk")
                
                st.markdown(f"**Parecer do Especialista:**\n> *{res_tail.get('parecer_tecnico', '')}*")
                
                st.markdown("**Aditivos Selecionados:**")
                for ad in res_tail.get("aditivos", []):
                    st.markdown(f"- **{ad.get('nome')}**: `{ad.get('concentracao', 0.0):.2f}% BWOC` — *{ad.get('justificativa', '')}*")

        # Telemetria do Trem de Deslocamento de Fluidos
        st.markdown(f"""
        <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 10px 14px; margin-top: 10px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;">
            <span style="color: #94a3b8; font-weight: 600; text-transform: uppercase;">Trem de Fluidos & Contraste de Deslocamento:</span>
            <span style="color: #cbd5e1; margin-left: 10px;">Lama: <b>{dens_lama:.2f} ppg</b></span> ➔ 
            <span style="color: #38bdf8;">Lead Slurry: <b>{res_lead.get('densidade_alvo_ppg', 12.8):.2f} ppg</b> (+{res_lead.get('densidade_alvo_ppg', 12.8) - dens_lama:.2f} ppg)</span> ➔ 
            <span style="color: #f59e0b;">Tail Slurry: <b>{res_tail.get('densidade_alvo_ppg', 16.0):.2f} ppg</b> (+{res_tail.get('densidade_alvo_ppg', 16.0) - res_lead.get('densidade_alvo_ppg', 12.8):.2f} ppg)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if "msg_sucesso_prog" in st.session_state:
            st.success(st.session_state.pop("msg_sucesso_prog"))

        def _aplicar_programa_callback():
            # Pasta 1 = Tail (Sapata), Pasta 2 = Lead (Preenchimento)
            _aplicar_formulacao_em_pasta(1, res_tail, aditivos_db)
            _aplicar_formulacao_em_pasta(2, res_lead, aditivos_db)
            st.session_state["msg_sucesso_prog"] = "✨ Programa Completo Aplicado! Pasta 1 (Tail) e Pasta 2 (Lead) foram configuradas na Aba 2."

        col_btn_all, _ = st.columns([2.5, 1.5])
        with col_btn_all:
            st.button(
                "✨ **Aplicar Programa Completo no Simulador (Pasta 1 = Tail + Pasta 2 = Lead)**",
                type="primary",
                use_container_width=True,
                on_click=_aplicar_programa_callback,
                key="btn_aplicar_prog_completo"
            )

    # 4. EXIBIÇÃO DE RECOMENDAÇÃO INDIVIDUAL
    elif "ultima_recomendacao_ia" in st.session_state:
        rec = st.session_state["ultima_recomendacao_ia"]

        st.markdown("---")
        st.markdown("#### 🏆 Parecer Técnico & Receita Química de Campo")

        with st.container(border=True):
            c_res1, c_res2, c_res3, c_res4 = st.columns(4)
            with c_res1:
                st.metric("Classe API", f"Classe {rec.get('classe_cimento', 'G')}")
            with c_res2:
                st.metric("Densidade Alvo", f"{rec.get('densidade_alvo_ppg', 15.8):.2f} ppg")
            with c_res3:
                st.metric("Água de Mistura", f"{rec.get('agua_gal_sk', 5.0):.2f} gal/sk")
            with c_res4:
                st.metric("Lama no Poço", f"{dens_lama:.2f} ppg", f"Overbalance: +{dens_lama - grad_poro:.2f} ppg")

            st.markdown(f"**Parecer do Especialista:**\n> *{rec.get('parecer_tecnico', 'Sem observações.')}*")

        aditivos_sugeridos = rec.get("aditivos", [])
        if aditivos_sugeridos:
            st.markdown("##### 🧪 Aditivos Homologados e Justificativa Técnica:")
            for ad in aditivos_sugeridos:
                nome_ad = ad.get("nome", "")
                conc = ad.get("concentracao", 0.0)
                just = ad.get("justificativa", "")
                info_db = aditivos_db.get(nome_ad, {})
                cat = info_db.get("categoria", "Aditivo")
                tipo = info_db.get("tipo", "solido")

                with st.container(border=True):
                    c_ad1, c_ad2 = st.columns([1.8, 3.2])
                    with c_ad1:
                        st.markdown(f"**{nome_ad}**")
                        st.caption(f"Categoria: {cat} · Tipo: {tipo}")
                        st.markdown(f"📊 **Dosagem:** `{conc:.2f}% BWOC`")
                    with c_ad2:
                        st.markdown(f"💡 **Justificativa:** {just}")

        # Transferência para pasta individual
        st.markdown("---")
        st.markdown("#### ⚡ Transferência Operacional para a Calculadora")

        if "msg_sucesso_aplicacao" in st.session_state:
            st.success(st.session_state.pop("msg_sucesso_aplicacao"))

        col_ap1, col_ap2 = st.columns([2, 2])
        with col_ap1:
            pasta_destino = st.selectbox(
                "Selecione a Pasta de Destino no Simulador:",
                [f"Pasta {i}" for i in range(1, total_pastas + 1)],
                key="ia_select_pasta_destino"
            )
            pasta_idx = int(pasta_destino.split(" ")[1])

        def _aplicar_ind_callback(idx_alvo: int, recomendacao: dict, banco_aditivos: dict):
            _aplicar_formulacao_em_pasta(idx_alvo, recomendacao, banco_aditivos)
            st.session_state["msg_sucesso_aplicacao"] = f"✅ Formulação transferida com sucesso para a Pasta {idx_alvo}!"

        with col_ap2:
            st.write("")
            st.write("")
            st.button(
                f"📥 **Aplicar Formulação na {pasta_destino}**",
                type="primary",
                use_container_width=True,
                on_click=_aplicar_ind_callback,
                args=(pasta_idx, rec, aditivos_db),
                key="btn_aplicar_formulacao_ia"
            )
