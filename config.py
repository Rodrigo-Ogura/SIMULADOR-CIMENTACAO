"""
Configurações e constantes do Simulador de Cimentação de Poços.
Compatível com Execução Local (.env) e Nuvem / Streamlit Cloud (st.secrets).
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env se existir localmente
load_dotenv()

# Caminhos base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Arquivo do banco de dados de aditivos
DB_FILE = os.path.join(DATA_DIR, "aditivos_db.json")

# Arquivo de log
LOG_FILE = os.path.join(LOGS_DIR, "cimentacao.log")

# Função auxiliar para extrair chave Groq com suporte híbrido (.env + st.secrets)
def _obter_groq_api_key() -> str:
    # 1. Tenta variável de ambiente local (.env ou sistema)
    chave = os.getenv("GROQ_API_KEY", "").strip()
    if chave:
        return chave
    
    # 2. Tenta Streamlit Secrets (Nuvem / Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass
    
    return ""

# Configurações do Groq Cloud API (Nuvem - Rápido, sem instalação local)
GROQ_API_KEY = _obter_groq_api_key()
GROQ_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "groq/compound",
    "groq/compound-mini",
    "qwen/qwen3.6-27b",
    "allam-2-7b"
]
GROQ_TEMPERATURE = 0.0

# Configurações do Ollama Local (Offline)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_TIMEOUT = 120  # segundos
OLLAMA_TEMPERATURE = 0.0  # prioriza reprodutibilidade nos cenários de engenharia

# Constantes Físicas e API
M_SACO = 94.0  # lb por saco de cimento
RO_AGUA = 8.33  # lb/gal (densidade da água)
D_CIMENTO = 3.14  # Gravidade específica (densidade relativa do cimento)

# Volume padrão de água por classe de cimento (gal/saco)
VOLUME_AGUA_POR_CLASSE = {
    'A': 5.2,
    'B': 5.2,
    'C': 6.3,
    'D': 4.3,
    'E': 4.3,
    'F': 4.3,
    'H': 4.3,
    'G': 5.0
}

# Categorias de aditivos reconhecidas
CATEGORIAS_ADITIVOS = [
    "Densificante",
    "Extensor",
    "Acelerador",
    "Retardador",
    "Dispersante",
    "Controlador de Filtrado",
    "Perda de Circulação (LCM)",
    "Especial / Outro"
]

# Aditivos padrão para inicialização do banco (extraídos do Bourgoyne et al., Tabela 3.8 em Português)
ADITIVOS_PADRAO = {
    'Bentonita (Gel)': {'densidade': 2.6500, 'tipo': 'solido', 'categoria': 'Extensor', 'dosagem_tipica': '1.0 a 4.0% BWOC', 'indicacao': 'Redução de densidade (< 15.0 ppg) e controle de água livre'},
    'Barita': {'densidade': 4.2300, 'tipo': 'solido', 'categoria': 'Densificante', 'dosagem_tipica': '10.0 a 40.0% BWOC', 'indicacao': 'Elevação de densidade (16.2 a 18.5 ppg)'},
    'Hematita': {'densidade': 5.0200, 'tipo': 'solido', 'categoria': 'Densificante', 'dosagem_tipica': '10.0 a 50.0% BWOC', 'indicacao': 'Densificação severa (> 17.5 ppg)'},
    'Cloreto de Cálcio (Salmoura)': {'densidade': 1.0329, 'tipo': 'salmoura', 'categoria': 'Acelerador', 'bhct_max_c': 25.0, 'dosagem_tipica': '1.0 a 2.0% BWOC', 'indicacao': 'Aceleração de pega em seções frias/rasas (BHCT < 25 °C)'},
    'Cloreto de Cálcio (Flocos)': {'densidade': 1.9600, 'tipo': 'solido', 'categoria': 'Acelerador', 'bhct_max_c': 25.0, 'dosagem_tipica': '1.0 a 2.0% BWOC', 'indicacao': 'Aceleração de resistência inicial (BHCT < 25 °C)'},
    'Cloreto de Sódio (Salmoura)': {'densidade': 1.0279, 'tipo': 'salmoura', 'categoria': 'Acelerador', 'dosagem_tipica': '2.0 a 4.0% BWOC'},
    'Cloreto de Sódio (Seco)': {'densidade': 2.1700, 'tipo': 'solido', 'categoria': 'Acelerador', 'dosagem_tipica': '2.0 a 4.0% BWOC'},
    'Gilsonita': {'densidade': 1.0700, 'tipo': 'solido', 'categoria': 'Extensor', 'dosagem_tipica': '3.0 a 10.0% BWOC'},
    'Perlita Regular': {'densidade': 2.2000, 'tipo': 'solido', 'categoria': 'Extensor', 'dosagem_tipica': '2.0 a 6.0% BWOC'},
    'Diatomita (Diacel D)': {'densidade': 2.1000, 'tipo': 'solido', 'categoria': 'Extensor', 'dosagem_tipica': '10.0 a 30.0% BWOC'},
    'Pozolana Pozmix A': {'densidade': 2.4600, 'tipo': 'solido', 'categoria': 'Extensor', 'dosagem_tipica': '20.0 a 40.0% BWOC'},
    'Pozolana Pozmix D': {'densidade': 2.5000, 'tipo': 'solido', 'categoria': 'Extensor', 'dosagem_tipica': '20.0 a 40.0% BWOC'},
    'Flor de Sílica (SSA-1)': {'densidade': 2.6300, 'tipo': 'solido', 'categoria': 'Especial / Outro', 'bhst_min_c': 110.0, 'dosagem_tipica': '30.0 a 35.0% BWOC', 'indicacao': 'Estabilizador mandatório contra regressão de resistência (BHST > 110 °C)'},
    'Areia de Sílica (Ottawa)': {'densidade': 2.6300, 'tipo': 'solido', 'categoria': 'Especial / Outro', 'bhst_min_c': 110.0, 'dosagem_tipica': '30.0 a 40.0% BWOC'},
    'Cal Hidratada': {'densidade': 2.2000, 'tipo': 'solido', 'categoria': 'Acelerador', 'dosagem_tipica': '2.0 a 4.0% BWOC'},
    'Gesso (Cal-Seal)': {'densidade': 2.7000, 'tipo': 'solido', 'categoria': 'Acelerador', 'dosagem_tipica': '5.0 a 15.0% BWOC'},
    'Dispersante CFR-1': {'densidade': 1.6300, 'tipo': 'solido', 'categoria': 'Dispersante', 'dosagem_tipica': '0.20 a 0.50% BWOC', 'indicacao': 'Redução de atrito e viscosidade'},
    'Dispersante CFR-2': {'densidade': 1.3000, 'tipo': 'solido', 'categoria': 'Dispersante', 'dosagem_tipica': '0.20 a 0.50% BWOC', 'indicacao': 'Dispersante de alta performance para reologia crítica'},
    'Retardador HR-4': {'densidade': 1.5600, 'tipo': 'solido', 'categoria': 'Retardador', 'bhct_min_c': 50.0, 'bhct_max_c': 75.0, 'dosagem_tipica': '0.15 a 0.40% BWOC', 'indicacao': 'Temperaturas amenas a moderadas (BHCT 50 a 75 °C)'},
    'Retardador HR-7': {'densidade': 1.3000, 'tipo': 'solido', 'categoria': 'Retardador', 'bhct_min_c': 65.0, 'bhct_max_c': 105.0, 'dosagem_tipica': '0.20 a 0.60% BWOC', 'indicacao': 'Temperaturas intermediárias (BHCT 65 a 105 °C)'},
    'Retardador HR-12': {'densidade': 1.2200, 'tipo': 'solido', 'categoria': 'Retardador', 'bhct_min_c': 75.0, 'bhct_max_c': 140.0, 'dosagem_tipica': '0.30 a 0.90% BWOC', 'indicacao': 'Poços profundos e quentes (BHCT > 75 °C)'},
    'Controlador de Filtrado HALDAD-9': {'densidade': 1.2200, 'tipo': 'solido', 'categoria': 'Controlador de Filtrado', 'dosagem_tipica': '0.30 a 0.70% BWOC', 'indicacao': 'Controle de filtrado API (< 50 mL/30min)'},
    'Controlador de Filtrado HALDAD-14': {'densidade': 1.3100, 'tipo': 'solido', 'categoria': 'Controlador de Filtrado', 'dosagem_tipica': '0.30 a 0.80% BWOC', 'indicacao': 'Controle de filtrado em alta temperatura e gás'},
    'Controlador de Filtrado Diacel LWL': {'densidade': 1.3600, 'tipo': 'solido', 'categoria': 'Controlador de Filtrado', 'dosagem_tipica': '0.20 a 0.50% BWOC'},
    'Agente de Perda de Circulação (Tuf-Plug)': {'densidade': 1.2800, 'tipo': 'solido', 'categoria': 'Perda de Circulação (LCM)', 'dosagem_tipica': '1.0 a 4.0% BWOC', 'indicacao': 'Vedação física de perdas de circulação'},
    'Carvão Ativado': {'densidade': 1.5700, 'tipo': 'solido', 'categoria': 'Especial / Outro', 'dosagem_tipica': '0.5 a 2.0% BWOC'}
}
