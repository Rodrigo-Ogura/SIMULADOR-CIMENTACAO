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


def _obter_secret_seguro(chave: str) -> str:
    """Extrai chave de st.secrets de forma segura, tolerante a ausência do arquivo local secrets.toml."""
    try:
        if hasattr(st, "secrets") and chave in st.secrets:
            return str(st.secrets[chave]).strip()
    except Exception:
        return ""
    return ""


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
            st.markdown("##### 🔌 Motor de Cálculo / Inferência")
            provedor_ia = st.radio(
                "Selecione o Motor:",
                [
                    "⚡ Motor Determinístico API Spec 10A (Instantâneo / Sem IA)",
                    "☁️ Groq Cloud LPU (Nuvem - Rápido com IA)",
                    "🖥️ Ollama Engine (Local - Offline com IA)"
                ],
                key="radio_provedor_ia",
                help="O Motor Determinístico calcula a formulação em milissegundos via regras físicas da API Spec 10A sem gastar tokens nem usar internet. Os modos Groq e Ollama utilizam IA generativa para sugerir formulações e redigir pareceres técnicos detalhados."
            )
        
        with col_prov2:
            st.markdown("##### 📊 Telemetria de Conexão & Modelo")
            if "Determinístico" in provedor_ia:
                st.markdown("""
                <div style="background-color: #0f172a; border: 1px solid #1e3a8a; border-radius: 6px; padding: 10px 14px; margin-top: 5px;">
                    <span style="color: #60a5fa; font-weight: 700; font-size: 0.85rem; font-family: 'JetBrains Mono';">⚡ MOTOR DETERMINÍSTICO DE ENGENHARIA ATIVO</span>
                    <p style="color: #94a3b8; font-size: 0.80rem; margin: 4px 0 0 0; line-height: 1.4;">
                        Cálculo estequiométrico e dosagem física direta pelas normas API Spec 10A / RP 10B e Bourgoyne Cap. 3. Zero consumo de tokens e sem dependência de internet.<br>
                        <span style="color: #fbbf24;"><b>⚠️ Aviso:</b> Justificativas normativas diretas incluídas. Pareceres discursivos em texto livre gerados por IA <b>não existem</b> nesta modalidade.</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                modelo_selecionado = "Motor Determinístico (API Spec 10A)"
            elif "Groq" in provedor_ia:
                # Obtém chave configurada via st.secrets, .env ou digitada na UI
                chave_configurada = (
                    st.session_state.get("user_groq_api_key", "")
                    or getattr(config, "GROQ_API_KEY", "")
                )
                secret_groq = _obter_secret_seguro("GROQ_API_KEY")
                if secret_groq:
                    chave_configurada = chave_configurada or secret_groq
                
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

    # Sincronização Inteligente com o Perfil Geomecânico da Aba 1
    perfil_ativo = st.session_state.get("perfil_geomecanico_ativo", None)
    meta_ativo = st.session_state.get("metadados_geomecanicos_ativos", None)
    fonte_nome = st.session_state.get("fonte_geomecanica_ativa", "Perfil Ativo")

    if perfil_ativo is not None:
        from src.services.geomecanica_service import GeomecanicaService
        metr = GeomecanicaService.extrair_metricas_resumo(perfil_ativo)
        p_base_est = float(metr.get("prof_max_m", 3200.0))
        g_poro_est = float(metr.get("poro_base_ppg", metr.get("poro_max_ppg", 10.20)))
        g_frac_est = float(metr.get("fratura_base_ppg", 16.50))
        g_frac_min_poco = float(metr.get("fratura_min_ppg", 11.0))
        bhst_prev = round(15.0 + 0.030 * p_base_est, 1)
        bhct_prev = round(max(25.0, bhst_prev * 0.65), 1)

        with st.container(border=True):
            c_ia_s1, c_ia_s2 = st.columns([2.2, 1.3])
            with c_ia_s1:
                st.markdown(f"🌐 **Perfil Geomecânico Conectado (Aba 1):** `{fonte_nome}`")
                st.caption(
                    f"Dados extraídos: **TD:** {p_base_est:.0f} m · "
                    f"**Poro Base:** {g_poro_est:.2f} ppg · **Fratura Base (Sapata):** {g_frac_est:.2f} ppg "
                    f"(Mín. Rasa: {g_frac_min_poco:.2f} ppg) · **BHCT Est.:** {bhct_prev:.0f} °C"
                )
            with c_ia_s2:
                if st.button("🪄 Sincronizar com Perfil da Aba 1", key="btn_sync_ia_profile", type="primary", use_container_width=True):
                    p_base = p_base_est
                    p_topo = 1827.0 if abs(p_base - 3260.0) < 50.0 else float(round(p_base * 0.56, 0))
                    g_poro = g_poro_est
                    g_frac = g_frac_est
                    
                    st.session_state["ia_base"] = p_base
                    st.session_state["ia_topo"] = p_topo
                    st.session_state["ia_poro"] = g_poro
                    st.session_state["ia_frac"] = g_frac
                    
                    # Densidade da lama no fundo
                    dens_lama_val = 10.60
                    if meta_ativo:
                        dens_lama_val = float(meta_ativo.get("dens_lama_fundo_ppg", 10.60))
                    st.session_state["ia_dens_lama"] = dens_lama_val
                    
                    # Tail Slurry: pasta de alta resistência na sapata (API RP 10B / Bourgoyne et al. Cap. 3)
                    # Deve respeitar overbalance sobre o poro e exceder a densidade da lama para eficiência de deslocamento
                    dmin_tail = max(15.60, round(dens_lama_val + 1.0, 2), round(g_poro + 1.0, 2))
                    dmax_tail = max(dmin_tail + 0.40, min(16.50, round(g_frac - 0.5, 2)))
                    
                    st.session_state["ia_dmin"] = dmin_tail
                    st.session_state["ia_dmax"] = dmax_tail
                    
                    st.session_state["ia_bhst"] = bhst_prev
                    st.session_state["ia_bhct"] = bhct_prev
                    
                    # Inferência de riscos geomecânicos
                    largura_min = float(metr.get("largura_min_ppg", 4.0))
                    st.session_state["ia_reologia"] = (largura_min < 2.0)
                    st.session_state["ia_perm"] = True
                    st.session_state["ia_obs"] = f"Poço {fonte_nome}. Perfil geomecânico contínuo carregado da Aba 1 (TD: {p_base:.0f}m, Frat. Base: {g_frac:.2f} ppg, BHCT: {bhct_prev:.0f}°C)."
                    st.rerun()

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
                "🎯 Programa Bi-Pasta Clássico: Lead (Topo) + Tail (Sapata)",
                "🏆 Programa Tri-Pasta Avançado: Lead (Topo) + Intermediária (Reservatório) + Tail (Sapata)",
                "⚡ Programa Tetra-Pasta: Scavenger (Varredura) + Lead + Intermediária + Tail",
                "🧪 Pasta Individual Customizada"
            ],
            key="ia_estrategia_selecionada"
        )
        if "Pasta Individual" in estrategia_ia:
            st.selectbox(
                "Função da Pasta Alvo:",
                [
                    "Tail Slurry (Sapata / Fundo)",
                    "Middle Slurry (Intermediária / Reservatório / Gás)",
                    "Lead Slurry (Preenchimento / Topo)",
                    "Scavenger Slurry (Varredura)"
                ],
                key="ia_tipo_pasta_ind"
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

    # Botão de Execução
    is_deterministico = "Determinístico" in provedor_ia
    st.write("")
    col_btn1, _ = st.columns([1.8, 1.7])
    with col_btn1:
        btn_label = "⚡ **Executar Dimensionamento Determinístico (API Spec 10A)**" if is_deterministico else "🧠 **Executar Dimensionamento Especialista**"
        gerar_clicked = st.button(btn_label, type="primary", use_container_width=True)

    def _executar_ia(dados_entrada: dict, tipo_alvo: str) -> Tuple[bool, Optional[dict], str]:
        if is_deterministico:
            from src.services.requisitos_ia import gerar_formulacao_deterministica
            res = gerar_formulacao_deterministica(dados_entrada, tipo_alvo, aditivos_db)
            if res.get("sucesso"):
                return True, res["recomendacao"], "Formulação determinística gerada com sucesso."
            return False, None, "Erro no cálculo determinístico da formulação."
        elif "Groq" in provedor_ia:
            chave_usada = (
                st.session_state.get("user_groq_api_key", "")
                or getattr(config, "GROQ_API_KEY", "")
            )
            secret_groq = _obter_secret_seguro("GROQ_API_KEY")
            if secret_groq:
                chave_usada = chave_usada or secret_groq

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
        if "Bi-Pasta" in estrategia_ia:
            with st.spinner(f"Dimensionando Programa Bi-Pasta (Lead + Tail) com {modelo_selecionado}..."):
                # 1. Tail Slurry (Sapata / Fundo)
                # Salvaguarda hidrostática: em programa bi-pasta, Tail deve ter peso de sapata (> Lead e > lama)
                tail_dmin = max(dens_min, 15.60, round(dens_lama + 1.0, 2)) if dens_max <= 13.5 or dens_max <= dens_lama else dens_min
                tail_dmax = max(dens_max, tail_dmin + 0.40, 16.20) if dens_max <= 13.5 or dens_max <= dens_lama else dens_max

                dados_tail = {
                    'prof_topo': prof_topo + (prof_base - prof_topo) * 0.70 if prof_base > prof_topo else prof_topo,
                    'prof_base': prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': tail_dmin,
                    'densidade_max_alvo': tail_dmax,
                    'bhst_c': bhst,
                    'bhct_c': bhct,
                    'tempo_bombeio_min': tempo_bombeio,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': chk_gas,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Tail Slurry (Sapata): isolamento mecânico de fundo. Lama: {dens_lama:.2f} ppg. {obs_texto}"
                }
                suc_tail, res_tail, msg_tail = _executar_ia(dados_tail, "Tail Slurry (Sapata / Fundo)")

                # 2. Lead Slurry (Preenchimento / Topo)
                lead_grad_frac = max(14.0, grad_frac - 1.5)
                lead_grad_poro = min(max(8.5, grad_poro - 1.2), 9.0)
                lead_dmax = min(13.5, lead_grad_frac - 0.6)
                lead_dmin = max(11.8, min(12.5, lead_dmax - 1.0))

                dados_lead = {
                    'prof_topo': prof_topo,
                    'prof_base': prof_topo + (prof_base - prof_topo) * 0.70 if prof_base > prof_topo else prof_topo + 500.0,
                    'grad_poro': lead_grad_poro,
                    'grad_fratura': lead_grad_frac,
                    'dens_lama': min(dens_lama, lead_dmin - 0.5),
                    'densidade_min_alvo': lead_dmin,
                    'densidade_max_alvo': lead_dmax,
                    'bhst_c': max(35.0, round(bhst * 0.70, 1)),
                    'bhct_c': max(25.0, round(bhct * 0.65, 1)),
                    'tempo_bombeio_min': tempo_bombeio + 30,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': False,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Lead Slurry: pasta leve para proteger topo contra fratura. {obs_texto}"
                }
                suc_lead, res_lead, msg_lead = _executar_ia(dados_lead, "Lead Slurry (Preenchimento / Topo)")

            if suc_tail and suc_lead:
                from src.services.requisitos_ia import validar_hierarquia_programa
                hier_ok, hier_erros = validar_hierarquia_programa({"tail": res_tail, "lead": res_lead}, dens_lama)
                if not hier_ok:
                    st.error("❌ Falha de consistência hidrostática entre as pastas:\n" + "\n".join(f"• {e}" for e in hier_erros))
                else:
                    st.session_state["programa_completo_ia"] = {"tipo": "bi", "tail": res_tail, "lead": res_lead}
                    st.session_state.pop("ultima_recomendacao_ia", None)
                    st.success("✅ **Programa Bi-Pasta (Lead + Tail) Aprovado com 100% de Conformidade nos Guardrails!**")
            else:
                erros = []
                if not suc_tail: erros.append(f"• **Tail Slurry:** {msg_tail}")
                if not suc_lead: erros.append(f"• **Lead Slurry:** {msg_lead}")
                st.error("❌ Falha no dimensionamento do Programa Bi-Pasta:\n\n" + "\n".join(erros))

        elif "Tri-Pasta" in estrategia_ia:
            with st.spinner(f"Dimensionando Programa Tri-Pasta Avançado (Lead + Intermediária + Tail) com {modelo_selecionado}..."):
                # 1. Tail Slurry (Sapata / Fundo - 25% inferior)
                tail_dmin = max(dens_min, 15.60, round(dens_lama + 1.0, 2)) if dens_max <= 13.5 or dens_max <= dens_lama else dens_min
                tail_dmax = max(dens_max, tail_dmin + 0.40, 16.20) if dens_max <= 13.5 or dens_max <= dens_lama else dens_max

                dados_tail = {
                    'prof_topo': prof_topo + (prof_base - prof_topo) * 0.75 if prof_base > prof_topo else prof_topo,
                    'prof_base': prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': tail_dmin,
                    'densidade_max_alvo': tail_dmax,
                    'bhst_c': bhst,
                    'bhct_c': bhct,
                    'tempo_bombeio_min': tempo_bombeio,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': chk_gas,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Tail Slurry (Sapata): máxima resistência mecânica e isolamento da sapata. {obs_texto}"
                }
                suc_tail, res_tail, msg_tail = _executar_ia(dados_tail, "Tail Slurry (Sapata / Fundo)")

                # 2. Middle Slurry (Intermediária / Reservatório & Gás - 40% intermediário)
                mid_dmin = round(max(dens_lama + 0.60, min(14.5, dens_min - 1.2)), 2)
                mid_dmax = round(min(dens_max - 0.40, max(15.6, dens_min - 0.2)), 2)
                dados_mid = {
                    'prof_topo': prof_topo + (prof_base - prof_topo) * 0.35 if prof_base > prof_topo else prof_topo,
                    'prof_base': prof_topo + (prof_base - prof_topo) * 0.75 if prof_base > prof_topo else prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': mid_dmin,
                    'densidade_max_alvo': mid_dmax,
                    'bhst_c': max(35.0, round(bhst * 0.85, 1)),
                    'bhct_c': max(25.0, round(bhct * 0.80, 1)),
                    'tempo_bombeio_min': tempo_bombeio + 20,
                    'zona_permeavel': True,
                    'presenca_gas': True if chk_gas else False,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Middle Slurry (Intermediária): vedação da zona de reservatório/gás e controle estrito de filtrado API. {obs_texto}"
                }
                suc_mid, res_mid, msg_mid = _executar_ia(dados_mid, "Middle Slurry (Intermediária / Reservatório / Gás)")

                # 3. Lead Slurry (Preenchimento / Topo - 35% superior)
                lead_dmax = round(min(13.5, mid_dmin - 0.40), 2)
                lead_dmin = round(max(11.8, dens_lama + 0.30), 2)
                dados_lead = {
                    'prof_topo': prof_topo,
                    'prof_base': prof_topo + (prof_base - prof_topo) * 0.35 if prof_base > prof_topo else prof_topo + 500.0,
                    'grad_poro': min(max(8.5, grad_poro - 1.2), 9.0),
                    'grad_fratura': max(14.0, grad_frac - 1.5),
                    'dens_lama': min(dens_lama, lead_dmin - 0.5),
                    'densidade_min_alvo': lead_dmin,
                    'densidade_max_alvo': lead_dmax,
                    'bhst_c': max(30.0, round(bhst * 0.65, 1)),
                    'bhct_c': max(20.0, round(bhct * 0.55, 1)),
                    'tempo_bombeio_min': tempo_bombeio + 40,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': False,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Lead Slurry: pasta leve para alívio hidrostático e proteção contra fratura. {obs_texto}"
                }
                suc_lead, res_lead, msg_lead = _executar_ia(dados_lead, "Lead Slurry (Preenchimento / Topo)")

            if suc_tail and suc_mid and suc_lead:
                from src.services.requisitos_ia import validar_hierarquia_programa
                hier_ok, hier_erros = validar_hierarquia_programa({"tail": res_tail, "middle": res_mid, "lead": res_lead}, dens_lama)
                if not hier_ok:
                    st.error("❌ Falha de consistência hidrostática entre as 3 pastas:\n" + "\n".join(f"• {e}" for e in hier_erros))
                else:
                    st.session_state["programa_completo_ia"] = {"tipo": "tri", "tail": res_tail, "middle": res_mid, "lead": res_lead}
                    st.session_state.pop("ultima_recomendacao_ia", None)
                    st.success("✅ **Programa Tri-Pasta Avançado (Lead + Intermediária + Tail) Aprovado com 100% de Conformidade nos Guardrails!**")
            else:
                erros = []
                if not suc_tail: erros.append(f"• **Tail Slurry (Sapata):** {msg_tail}")
                if not suc_mid: erros.append(f"• **Middle Slurry (Intermediária):** {msg_mid}")
                if not suc_lead: erros.append(f"• **Lead Slurry (Preenchimento):** {msg_lead}")
                st.error("❌ Falha no dimensionamento do Programa Tri-Pasta:\n\n" + "\n".join(erros))

        elif "Tetra-Pasta" in estrategia_ia:
            with st.spinner(f"Dimensionando Programa Tetra-Pasta com Varredura com {modelo_selecionado}..."):
                # Tail Slurry
                tail_dmin = max(dens_min, 15.60, round(dens_lama + 1.0, 2)) if dens_max <= 13.5 or dens_max <= dens_lama else dens_min
                tail_dmax = max(dens_max, tail_dmin + 0.40, 16.20) if dens_max <= 13.5 or dens_max <= dens_lama else dens_max

                dados_tail = {
                    'prof_topo': prof_topo + (prof_base - prof_topo) * 0.75 if prof_base > prof_topo else prof_topo,
                    'prof_base': prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': tail_dmin,
                    'densidade_max_alvo': tail_dmax,
                    'bhst_c': bhst,
                    'bhct_c': bhct,
                    'tempo_bombeio_min': tempo_bombeio,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': chk_gas,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Tail Slurry (Sapata): máxima resistência mecânica. {obs_texto}"
                }
                suc_tail, res_tail, msg_tail = _executar_ia(dados_tail, "Tail Slurry (Sapata / Fundo)")

                # Middle Slurry
                mid_dmin = round(max(dens_lama + 0.60, min(14.5, dens_min - 1.2)), 2)
                mid_dmax = round(min(dens_max - 0.40, max(15.6, dens_min - 0.2)), 2)
                dados_mid = {
                    'prof_topo': prof_topo + (prof_base - prof_topo) * 0.40 if prof_base > prof_topo else prof_topo,
                    'prof_base': prof_topo + (prof_base - prof_topo) * 0.75 if prof_base > prof_topo else prof_base,
                    'grad_poro': grad_poro,
                    'grad_fratura': grad_frac,
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': mid_dmin,
                    'densidade_max_alvo': mid_dmax,
                    'bhst_c': max(35.0, round(bhst * 0.85, 1)),
                    'bhct_c': max(25.0, round(bhct * 0.80, 1)),
                    'tempo_bombeio_min': tempo_bombeio + 20,
                    'zona_permeavel': True,
                    'presenca_gas': True,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Middle Slurry (Reservatório): vedação de hidrocarbonetos e filtrado API. {obs_texto}"
                }
                suc_mid, res_mid, msg_mid = _executar_ia(dados_mid, "Middle Slurry (Intermediária / Reservatório / Gás)")

                # Lead Slurry
                lead_dmax = round(min(13.5, mid_dmin - 0.40), 2)
                lead_dmin = round(max(11.8, dens_lama + 0.30), 2)
                dados_lead = {
                    'prof_topo': prof_topo + 200.0,
                    'prof_base': prof_topo + (prof_base - prof_topo) * 0.40 if prof_base > prof_topo else prof_topo + 500.0,
                    'grad_poro': min(max(8.5, grad_poro - 1.2), 9.0),
                    'grad_fratura': max(14.0, grad_frac - 1.5),
                    'dens_lama': min(dens_lama, lead_dmin - 0.5),
                    'densidade_min_alvo': lead_dmin,
                    'densidade_max_alvo': lead_dmax,
                    'bhst_c': max(30.0, round(bhst * 0.65, 1)),
                    'bhct_c': max(20.0, round(bhct * 0.55, 1)),
                    'tempo_bombeio_min': tempo_bombeio + 35,
                    'zona_permeavel': chk_perm,
                    'presenca_gas': False,
                    'perda_circulacao': chk_lcm,
                    'reologia_critica': chk_reologia,
                    'observacoes': f"Lead Slurry: pasta leve para alívio anular. {obs_texto}"
                }
                suc_lead, res_lead, msg_lead = _executar_ia(dados_lead, "Lead Slurry (Preenchimento / Topo)")

                # Scavenger Slurry
                scav_dmin = round(max(10.5, dens_lama - 0.2), 2)
                scav_dmax = round(min(11.8, lead_dmin - 0.1), 2)
                dados_scav = {
                    'prof_topo': prof_topo,
                    'prof_base': prof_topo + 200.0,
                    'grad_poro': min(8.6, grad_poro),
                    'grad_fratura': max(13.5, grad_frac - 2.0),
                    'dens_lama': dens_lama,
                    'densidade_min_alvo': scav_dmin,
                    'densidade_max_alvo': scav_dmax,
                    'bhst_c': 25.0,
                    'bhct_c': 20.0,
                    'tempo_bombeio_min': 60,
                    'zona_permeavel': False,
                    'presenca_gas': False,
                    'perda_circulacao': False,
                    'reologia_critica': True,
                    'observacoes': f"Scavenger Slurry: pasta de varredura ultraleve com alto teor de dispersante para limpeza de reboco. {obs_texto}"
                }
                suc_scav, res_scav, msg_scav = _executar_ia(dados_scav, "Scavenger Slurry (Varredura)")

            if suc_tail and suc_mid and suc_lead and suc_scav:
                from src.services.requisitos_ia import validar_hierarquia_programa
                hier_ok, hier_erros = validar_hierarquia_programa({"tail": res_tail, "middle": res_mid, "lead": res_lead, "scavenger": res_scav}, dens_lama)
                if not hier_ok:
                    st.error("❌ Falha de consistência hidrostática entre as 4 pastas:\n" + "\n".join(f"• {e}" for e in hier_erros))
                else:
                    st.session_state["programa_completo_ia"] = {"tipo": "tetra", "tail": res_tail, "middle": res_mid, "lead": res_lead, "scavenger": res_scav}
                    st.session_state.pop("ultima_recomendacao_ia", None)
                    st.success("✅ **Programa Tetra-Pasta (Scavenger + Lead + Middle + Tail) Aprovado com 100% de Conformidade nos Guardrails!**")
            else:
                erros = []
                if not suc_tail: erros.append(f"• **Tail Slurry:** {msg_tail}")
                if not suc_mid: erros.append(f"• **Middle Slurry:** {msg_mid}")
                if not suc_lead: erros.append(f"• **Lead Slurry:** {msg_lead}")
                if not suc_scav: erros.append(f"• **Scavenger Slurry:** {msg_scav}")
                st.error("❌ Falha no dimensionamento do Programa Tetra-Pasta:\n\n" + "\n".join(erros))

        else:
            # Pasta Individual Selecionada
            tipo_alvo = st.session_state.get("ia_tipo_pasta_ind", "Tail Slurry (Sapata / Fundo)")
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

    # 3. EXIBIÇÃO DE PROGRAMAS COMPLETOS (BI, TRI OU TETRA-PASTA)
    if "programa_completo_ia" in st.session_state:
        prog = st.session_state["programa_completo_ia"]
        tipo_prog = prog.get("tipo", "bi")
        res_tail = prog.get("tail", {})
        res_mid = prog.get("middle", {})
        res_lead = prog.get("lead", {})
        res_scav = prog.get("scavenger", {})

        st.markdown("---")
        if is_deterministico:
            st.info(
                "⚙️ **Modalidade Determinística (Regras API Spec 10A / RP 10B):** "
                "Formulação calculada deterministicamente. As dosagens e seleção de aditivos seguem regras estritas de engenharia de campo. "
                "**Nota:** Justificativas normativas diretas foram aplicadas para cada aditivo; pareceres discursivos em texto livre e redação livre gerados por IA **não estão presentes** nesta modalidade."
            )
        if tipo_prog == "tetra":
            st.markdown("#### ⚡ Programa Tetra-Pasta Completo com Varredura (Scavenger + Lead + Middle + Tail)")
            st.caption("Estratégia avançada de 4 estágios: varredura e limpeza anular, preenchimento leve, isolamento de reservatório e sapata estrutural.")
            cols = st.columns(4, gap="medium")
            col_list = [
                (cols[0], "⚪ Pasta 4: Scavenger Slurry (Varredura)", res_scav),
                (cols[1], "📘 Pasta 3: Lead Slurry (Preenchimento)", res_lead),
                (cols[2], "📗 Pasta 2: Middle Slurry (Reservatório)", res_mid),
                (cols[3], "📙 Pasta 1: Tail Slurry (Sapata)", res_tail)
            ]
        elif tipo_prog == "tri":
            st.markdown("#### 🏆 Programa Tri-Pasta Avançado (Lead + Intermediária + Tail)")
            st.caption("Estratégia de 3 estágios recomendada para poços complexos: alívio hidrostático de topo, isolamento de gás/reservatório e ancoragem de sapata.")
            cols = st.columns(3, gap="medium")
            col_list = [
                (cols[0], "📘 Pasta 3: Lead Slurry (Preenchimento / Topo)", res_lead),
                (cols[1], "📗 Pasta 2: Middle Slurry (Intermediária / Reservatório)", res_mid),
                (cols[2], "📙 Pasta 1: Tail Slurry (Sapata / Fundo)", res_tail)
            ]
        else: # bi
            st.markdown("#### 🎯 Programa Bi-Pasta Clássico (Lead + Tail)")
            st.caption("Estratégia convencional de 2 estágios: preenchimento anular com pasta leve e vedação de sapata com pasta de alta resistência.")
            cols = st.columns(2, gap="large")
            col_list = [
                (cols[0], "📘 Pasta 2: Lead Slurry (Preenchimento / Topo)", res_lead),
                (cols[1], "📙 Pasta 1: Tail Slurry (Sapata / Fundo)", res_tail)
            ]

        # Renderização dos Cards das Pastas
        for col_card, titulo_card, dados_pasta in col_list:
            with col_card:
                with st.container(border=True):
                    st.markdown(f"##### {titulo_card}")
                    c_m1, c_m2, c_m3 = st.columns(3)
                    c_m1.metric("Densidade", f"{dados_pasta.get('densidade_alvo_ppg', 15.0):.2f} ppg")
                    c_m2.metric("Classe API", f"Classe {dados_pasta.get('classe_cimento', 'G')}")
                    c_m3.metric("Água", f"{dados_pasta.get('agua_gal_sk', 5.0):.2f} gal/sk")
                    
                    st.markdown(f"**Parecer:**\n> *{dados_pasta.get('parecer_tecnico', '')}*")
                    st.markdown("**Aditivos Selecionados:**")
                    for ad in dados_pasta.get("aditivos", []):
                        st.markdown(f"- **{ad.get('nome')}**: `{ad.get('concentracao', 0.0):.2f}% BWOC` — *{ad.get('justificativa', '')}*")

        # Telemetria do Trem de Deslocamento de Fluidos
        d_tail = res_tail.get('densidade_alvo_ppg', 16.0)
        d_mid = res_mid.get('densidade_alvo_ppg', 15.0)
        d_lead = res_lead.get('densidade_alvo_ppg', 12.8)
        d_scav = res_scav.get('densidade_alvo_ppg', 11.2)

        if tipo_prog == "tetra":
            fluxo_html = f"""
            <span style="color: #cbd5e1;">Lama: <b>{dens_lama:.2f} ppg</b></span> ➔ 
            <span style="color: #94a3b8;">Scavenger: <b>{d_scav:.2f} ppg</b> (+{d_scav - dens_lama:.2f})</span> ➔ 
            <span style="color: #38bdf8;">Lead: <b>{d_lead:.2f} ppg</b> (+{d_lead - d_scav:.2f})</span> ➔ 
            <span style="color: #10b981;">Middle: <b>{d_mid:.2f} ppg</b> (+{d_mid - d_lead:.2f})</span> ➔ 
            <span style="color: #f59e0b;">Tail: <b>{d_tail:.2f} ppg</b> (+{d_tail - d_mid:.2f})</span>
            """
        elif tipo_prog == "tri":
            fluxo_html = f"""
            <span style="color: #cbd5e1;">Lama: <b>{dens_lama:.2f} ppg</b></span> ➔ 
            <span style="color: #38bdf8;">Lead Slurry: <b>{d_lead:.2f} ppg</b> (+{d_lead - dens_lama:.2f})</span> ➔ 
            <span style="color: #10b981;">Middle Slurry: <b>{d_mid:.2f} ppg</b> (+{d_mid - d_lead:.2f})</span> ➔ 
            <span style="color: #f59e0b;">Tail Slurry: <b>{d_tail:.2f} ppg</b> (+{d_tail - d_mid:.2f})</span>
            """
        else:
            fluxo_html = f"""
            <span style="color: #cbd5e1;">Lama: <b>{dens_lama:.2f} ppg</b></span> ➔ 
            <span style="color: #38bdf8;">Lead Slurry: <b>{d_lead:.2f} ppg</b> (+{d_lead - dens_lama:.2f})</span> ➔ 
            <span style="color: #f59e0b;">Tail Slurry: <b>{d_tail:.2f} ppg</b> (+{d_tail - d_lead:.2f})</span>
            """

        st.markdown(f"""
        <div style="background-color: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 10px 14px; margin-top: 10px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;">
            <span style="color: #94a3b8; font-weight: 600; text-transform: uppercase;">Trem de Fluidos & Contraste de Deslocamento:</span>
            <span style="margin-left: 10px;">{fluxo_html}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if "msg_sucesso_prog" in st.session_state:
            st.success(st.session_state.pop("msg_sucesso_prog"))

        def _aplicar_programa_multi_callback():
            p_base_m = float(st.session_state.get("ia_base", 3260.0))
            p_topo_m = float(st.session_state.get("ia_topo", 1827.0))
            h_total_m = max(300.0, p_base_m - p_topo_m)
            h_total_ft = round(h_total_m * 3.28084, 1)

            if tipo_prog == "tetra":
                st.session_state["num_pastas_anular"] = 4
                st.session_state["dist_1"] = round(h_total_ft * 0.30, 1)
                st.session_state["dist_2"] = round(h_total_ft * 0.30, 1)
                st.session_state["dist_3"] = round(h_total_ft * 0.25, 1)
                st.session_state["dist_4"] = round(h_total_ft - st.session_state["dist_1"] - st.session_state["dist_2"] - st.session_state["dist_3"], 1)
                _aplicar_formulacao_em_pasta(1, res_tail, aditivos_db)
                _aplicar_formulacao_em_pasta(2, res_mid, aditivos_db)
                _aplicar_formulacao_em_pasta(3, res_lead, aditivos_db)
                _aplicar_formulacao_em_pasta(4, res_scav, aditivos_db)
                st.session_state["msg_sucesso_prog"] = f"✨ Programa Tetra-Pasta Aplicado! Alturas sincronizadas ({h_total_m:.0f} m = {h_total_ft:,.0f} ft) e Pastas 1 a 4 configuradas na Aba 4."
            elif tipo_prog == "tri":
                st.session_state["num_pastas_anular"] = 3
                st.session_state["dist_1"] = round(h_total_ft * 0.30, 1)
                st.session_state["dist_2"] = round(h_total_ft * 0.35, 1)
                st.session_state["dist_3"] = round(h_total_ft - st.session_state["dist_1"] - st.session_state["dist_2"], 1)
                _aplicar_formulacao_em_pasta(1, res_tail, aditivos_db)
                _aplicar_formulacao_em_pasta(2, res_mid, aditivos_db)
                _aplicar_formulacao_em_pasta(3, res_lead, aditivos_db)
                st.session_state["msg_sucesso_prog"] = f"✨ Programa Tri-Pasta Aplicado! Alturas sincronizadas ({h_total_m:.0f} m = {h_total_ft:,.0f} ft) e Pastas 1 a 3 configuradas na Aba 4."
            else:
                st.session_state["num_pastas_anular"] = 2
                st.session_state["dist_1"] = round(h_total_ft * 0.5303, 1)
                st.session_state["dist_2"] = round(h_total_ft - st.session_state["dist_1"], 1)
                _aplicar_formulacao_em_pasta(1, res_tail, aditivos_db)
                _aplicar_formulacao_em_pasta(2, res_lead, aditivos_db)
                st.session_state["msg_sucesso_prog"] = (
                    f"✨ Programa Bi-Pasta Aplicado! Intervalo {p_topo_m:.0f}m–{p_base_m:.0f}m ({h_total_m:.0f} m = {h_total_ft:,.0f} ft) "
                    f"distribuído em Tail ({st.session_state['dist_1']:,.0f} ft) e Lead ({st.session_state['dist_2']:,.0f} ft) na Aba 4."
                )

        col_btn_all, _ = st.columns([2.5, 1.5])
        with col_btn_all:
            nome_botao = f"✨ **Aplicar Programa {tipo_prog.title()}-Pasta no Simulador (Aba 4 - Configuração das Pastas)**"
            st.button(
                nome_botao,
                type="primary",
                use_container_width=True,
                on_click=_aplicar_programa_multi_callback,
                key="btn_aplicar_prog_completo"
            )

    # 4. EXIBIÇÃO DE RECOMENDAÇÃO INDIVIDUAL
    elif "ultima_recomendacao_ia" in st.session_state:
        rec = st.session_state["ultima_recomendacao_ia"]

        st.markdown("---")
        if is_deterministico:
            st.info(
                "⚙️ **Modalidade Determinística (Regras API Spec 10A / RP 10B):** "
                "Formulação calculada deterministicamente. As dosagens e seleção de aditivos seguem regras estritas de campo. "
                "**Nota:** Justificativas normativas diretas foram aplicadas para cada aditivo; pareceres discursivos em texto livre e redação livre gerados por IA **não estão presentes** nesta modalidade."
            )
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
                [f"Pasta {i}" for i in range(1, 5)],
                key="ia_select_pasta_destino"
            )
            pasta_idx = int(pasta_destino.split(" ")[1])

        def _aplicar_ind_callback(idx_alvo: int, recomendacao: dict, banco_aditivos: dict):
            qtd_atual = st.session_state.get("num_pastas_anular", 1)
            if idx_alvo > qtd_atual:
                st.session_state["num_pastas_anular"] = idx_alvo
            _aplicar_formulacao_em_pasta(idx_alvo, recomendacao, banco_aditivos)
            st.session_state["msg_sucesso_aplicacao"] = f"✅ Formulação transferida com sucesso para a Pasta {idx_alvo} na Aba 4 (Configuração das Pastas)!"

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

