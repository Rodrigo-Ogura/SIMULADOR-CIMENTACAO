import streamlit as st
import math
import pandas as pd
import plotly.express as px
import json
import os

# --- CONSTANTES E CONFIGURAÇÕES DE ARQUIVO ---
M_SACO = 94  # lb
RO_AGUA = 8.33  # lb/gal
D_CIMENTO = 3.14  # gravidade específica
VOLUME_AGUA_POR_CLASSE = {
    'A': 5.2, 'B': 5.2, 'C': 6.3, 
    'D': 4.3, 'E': 4.3, 'F': 4.3, 'H': 4.3, 'G': 5.0
}

DB_FILE = "aditivos_db.json"
ADITIVOS_PADRAO = {
    'Bentonita': {'densidade': 2.6500, 'tipo': 'solido'},
    'NaCl': {'densidade': 1.0279, 'tipo': 'salmoura'},
    'CaCl2': {'densidade': 1.0329, 'tipo': 'salmoura'}
}

# --- LÓGICA DE PERSISTÊNCIA (BANCO DE DADOS LOCAL) ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(ADITIVOS_PADRAO, f, indent=4, ensure_ascii=False)

if 'aditivos_db' not in st.session_state:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        st.session_state.aditivos_db = json.load(f)

# --- FUNÇÕES DE CÁLCULO ---
def calcular_geometria(d_broca, d_ext, d_int, altura_secao, fator_excesso, dist_sapata, calc_colar):
    vol_anular = (math.pi / 4) * (d_broca**2 - d_ext**2) * altura_secao / 144
    vol_colar = (math.pi / 4) * (d_int**2) * dist_sapata / 144 if calc_colar else 0
    return (vol_anular * fator_excesso) + vol_colar

# --- INTERFACE DO SITE ---
st.set_page_config(page_title="Calculadora de Cimentação Profissional", layout="wide")
st.title("🛢️ Calculadora Visual de Cimentação (Múltiplas Pastas)")

# --- BARRA LATERAL: GERENCIAR ADITIVOS E GEOMETRIA ---
with st.sidebar:
    st.header("⚙️ Parâmetros do Poço")
    d_broca = st.number_input("Diâmetro da Broca (in)", value=12.2500, format="%.4f", step=0.0001)
    d_ext = st.number_input("Diâmetro Externo Revestimento (in)", value=9.6250, format="%.4f", step=0.0001)
    d_int = st.number_input("Diâmetro Interno Revestimento (in)", value=8.8350, format="%.4f", step=0.0001)
    fator_excesso = st.number_input("Fator de Excesso (ex: 1.2 para 20%)", value=1.2000, format="%.4f", step=0.0001)
    dist_sapata = st.number_input("Distância Colar-Sapata (ft)", value=40.0000, format="%.4f", step=0.0001)
    
    st.divider()
    
    st.header("🧪 Criar Novo Aditivo")
    novo_nome = st.text_input("Nome do Aditivo")
    nova_densidade = st.number_input("Densidade Relativa", value=1.0000, format="%.4f", step=0.0001)
    novo_tipo = st.selectbox("Tipo de Mistura", ["solido", "salmoura"])
    
    if st.button("Adicionar ao Banco (Salvar Permanente)"):
        if novo_nome:
            st.session_state.aditivos_db[novo_nome] = {'densidade': nova_densidade, 'tipo': novo_tipo}
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(st.session_state.aditivos_db, f, indent=4, ensure_ascii=False)
            st.success(f"'{novo_nome}' salvo permanentemente no banco!")
            st.rerun()
        else:
            st.warning("Preencha o nome do aditivo.")

# --- ÁREA PRINCIPAL ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🛠️ Configuração das Pastas")
    quantidade_pastas = st.number_input("Quantas pastas serão utilizadas?", min_value=1, max_value=5, value=2)
    
    if quantidade_pastas > 1:
        st.warning("⚠️ AS PASTAS SÃO CONFIGURADAS DE BAIXO PARA CIMA! (A Aba 'Pasta 1' é a do fundo do poço)")

    abas = st.tabs([f"Pasta {i}" for i in range(1, quantidade_pastas + 1)])
    pastas_configuradas = []

    for idx, aba in enumerate(abas, start=1):
        with aba:
            st.markdown(f"### Parâmetros da Pasta {idx}")
            dist_fundo = st.number_input(f"Altura desta seção no anular (ft)", value=1000.0000 if idx == 1 else 500.0000, format="%.4f", step=0.0001, key=f"dist_{idx}")
            classe_cimento = st.selectbox("Classe do Cimento API", list(VOLUME_AGUA_POR_CLASSE.keys()), index=7 if idx == 1 else 2, key=f"classe_{idx}")
            
            fator_agua_padrao = VOLUME_AGUA_POR_CLASSE[classe_cimento]
            usar_custom_agua = st.checkbox("Fator Água-Cimento Personalizado?", value=False, key=f"chk_agua_{idx}")
            
            if usar_custom_agua:
                fator_agua_cimento = st.number_input("Quantos galões por saco (gal/saco):", min_value=0.0001, value=float(fator_agua_padrao), format="%.4f", step=0.0001, key=f"agua_{idx}")
            else:
                fator_agua_cimento = 0.0
            
            st.divider()
            
            aditivos_selecionados = st.multiselect("Aditivos desta pasta:", options=list(st.session_state.aditivos_db.keys()), key=f"adit_{idx}")
            
            porcentagens = {}
            for aditivo in aditivos_selecionados:
                porcentagens[aditivo] = st.number_input(f"Porcentagem de {aditivo} (% BWOC)", min_value=0.0000, value=2.0000, format="%.4f", step=0.0001, key=f"pct_{aditivo}_{idx}")
                
            pastas_configuradas.append({
                'numero': idx,
                'dist_fundo': dist_fundo,
                'classe': classe_cimento,
                'fator_agua_cimento': fator_agua_cimento,
                'porcentagens': porcentagens
            })

with col2:
    st.header("📊 Resumo em Tabela")
    resultados_finais = []
    
    for p in pastas_configuradas:
        num_p = p['numero']
        
        if p['fator_agua_cimento'] > 0:
            vol_agua_gal = p['fator_agua_cimento']
        else:
            vol_agua_gal = VOLUME_AGUA_POR_CLASSE[p['classe']]
            
        massa_agua = vol_agua_gal * RO_AGUA
        massa_cimento = M_SACO
        vol_cimento_gal = massa_cimento / (D_CIMENTO * RO_AGUA)
        
        massa_total = massa_agua + massa_cimento
        vol_total_gal = vol_agua_gal + vol_cimento_gal
        
        composicao_volumes = {"Água": vol_agua_gal, "Cimento": vol_cimento_gal}
        
        for aditivo, pct in p['porcentagens'].items():
            if pct > 0:
                info = st.session_state.aditivos_db[aditivo]
                massa_adit = (pct / 100) * M_SACO
                
                if info['tipo'] == 'solido':
                    vol_adit = massa_adit / (info['densidade'] * RO_AGUA)
                    massa_total += massa_adit
                    vol_total_gal += vol_adit
                    composicao_volumes[aditivo] = vol_adit
                else:
                    vol_adit = max(0, (massa_adit + massa_agua) / (info['densidade'] * RO_AGUA) - vol_agua_gal)
                    massa_total += massa_adit
                    vol_total_gal += vol_adit
                    composicao_volumes[aditivo] = vol_adit

        rendimento = vol_total_gal / 7.5
        densidade = massa_total / vol_total_gal if vol_total_gal > 0 else 0
        
        considerar_colar = (num_p == 1)
        vol_necessario_ft3 = calcular_geometria(d_broca, d_ext, d_int, p['dist_fundo'], fator_excesso, dist_sapata, considerar_colar)
        num_sacos = math.ceil(vol_necessario_ft3 / rendimento) if rendimento > 0 else 0
        
        resultados_finais.append({
            'numero': num_p,
            'densidade': densidade,
            'rendimento': rendimento,
            'volume': vol_necessario_ft3,
            'sacos': num_sacos,
            'altura': p['dist_fundo'],
            'composicao': composicao_volumes
        })
    
    # Exibe a tabela principal de resumo
    dados_tabela = [{
        'Pasta': f"Pasta {r['numero']}",
        'Sacos': r['sacos'],
        'Vol Seção (ft³)': f"{r['volume']:.4f}",
        'Rend (ft³/sk)': f"{r['rendimento']:.4f}",
        'Dens (lbm/gal)': f"{r['densidade']:.4f}"
    } for r in resultados_finais]
    
    df_resumo = pd.DataFrame(dados_tabela)
    st.dataframe(df_resumo, hide_index=True, width="stretch")

    st.divider()

    # --- PANORAMA GERAL DO POÇO (ABAIXO DA TABELA) ---
    st.subheader("🌎 Panorama Geral e Perfil do Poço")
    
    total_sacos_poco = sum(r['sacos'] for r in resultados_finais)
    total_volume_poco = sum(r['volume'] for r in resultados_finais)
    
    # Métricas compactadas para caber na coluna
    c_met1, c_met2 = st.columns(2)
    c_met1.metric(label="Vol. Total Poço", value=f"{total_volume_poco:.2f} ft³")
    c_met2.metric(label="Total de Sacos", value=f"{total_sacos_poco} sk")
    
    # Preparação dos dados do Perfil Vertical
    dados_perfil = []
    for r in resultados_finais:
        dados_perfil.append({
            'Poço': 'Perfil Anular',
            'Pasta': f"Pasta {r['numero']}",
            'Altura da Seção (ft)': r['altura'],
            'Densidade (ppg)': r['densidade']
        })
    df_perfil = pd.DataFrame(dados_perfil)
    
    # Gráfico do Perfil Vertical (CORRIGIDO yaxis_title)
    fig_poco = px.bar(
        df_perfil, x="Poço", y="Altura da Seção (ft)", color="Pasta",
        text=df_perfil.apply(lambda r: f"<b>{r['Pasta']}</b><br>{r['Altura da Seção (ft)']:.1f} ft<br>{r['Densidade (ppg)']:.2f} ppg", axis=1),
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_poco.update_traces(textposition='inside')
    fig_poco.update_layout(
        xaxis_title="", yaxis_title="Altura Total (ft)",  # CORRIGIDO AQUI
        barmode='stack',
        bargap=0.5,       
        height=480,       
        showlegend=False,  
        margin=dict(l=40, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_poco, width="stretch")
    
    # Menu retrátil com a tabela detalhada de cubagem espacial
    with st.expander("📋 Detalhes Espaciais das Seções"):
        df_espacial = pd.DataFrame([{
            'Pasta': f"Pasta {r['numero']}",
            'Altura (ft)': f"{r['altura']:.2f}",
            'Volume (ft³)': f"{r['volume']:.2f}"
        } for r in resultados_finais])
        st.dataframe(df_espacial, hide_index=True, width="stretch")

st.divider()

# --- ANÁLISE INDIVIDUAL ---
st.subheader("🔍 Análise Individual da Pasta (Fração por Saco)")
pasta_selecionada = st.selectbox(
    "Selecione qual pasta deseja analisar detalhadamente no gráfico de pizza:", 
    options=[f"Pasta {r['numero']}" for r in resultados_finais]
)

idx_grafico = int(pasta_selecionada.split(" ")[1]) - 1
pasta_alvo = resultados_finais[idx_grafico]

df_comp = pd.DataFrame(list(pasta_alvo['composicao'].items()), columns=['Componente', 'Volume (gal/saco)'])
fig_pizza = px.pie(
    df_comp, values='Volume (gal/saco)', names='Componente', 
    title=f'Proporção de Mistura por Saco — {pasta_selecionada}', hole=0.4, 
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_pizza, width="stretch")