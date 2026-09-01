# 📜 Histórico de Progresso do Projeto: Simulador de Cimentação

Documento de registro contínuo de evolução, alterações de código, testes e próximos passos.
> **Regra:** Este documento é consultado no início de cada sessão e atualizado a cada alteração relevante conforme definido em [`GEMINI.md`](./GEMINI.md).

---

## 🏗️ Visão Geral da Arquitetura do Projeto

- **Linguagem & Frameworks:** Python 3.10+, Streamlit, Plotly, NumPy, Pandas, Pydantic, Groq Cloud API, Ollama Local.
- **Design System:** Estilo industrial de alta fidelidade inspirado no **OpenLab Drilling (NORCE)** (Dark Slate Theme `#0b0f19`, Cartões Digitais SCADA de Telemetria via `st.html`, Esquemático 2D Didático, Janela de Pressão Geomecânica e Recomendador de Programa Completo Multi-Pasta).
- **Segurança & Deploy em Nuvem:** Suporte a segredos criptografados via `st.secrets` para publicação segura no **Streamlit Community Cloud** e proteção estrita de credenciais com `.gitignore`.
- **Estrutura de Pastas:**
  - `app.py`: Ponto de entrada do simulador Streamlit integrando cabeçalho de telemetria, abas e tema OpenLab com escala tipográfica calibrada.
  - `config.py`: Constantes físicas API, configurações de ambiente (`.env` local ou `st.secrets` na nuvem), catálogo padrão de aditivos e parâmetros de IA.
  - `data/`: Banco de dados persistente em JSON ([`aditivos_db.json`](./data/aditivos_db.json)).
  - `docs/`: Base pedagógica e normativa estruturada em 3 níveis (Fundamentos, Sistema/IA, Acadêmico/Normativo), guia de deploy e anexos em PDF.
  - `src/models/`: Modelos de dados de aditivos ([`aditivo.py`](./src/models/aditivo.py)) e pastas de cimento ([`pasta.py`](./src/models/pasta.py)).
  - `src/services/`: Motores matemáticos, persistência e IA (`calculadora.py`, `aditivo_service.py`, `groq_agent_service.py`, `ollama_agent_service.py`, `requisitos_ia.py`).
  - `src/ui/`: Telas e componentes visuais (`sidebar.py`, `tab_parametros_poco.py`, `tabs_pastas.py`, `tab_agente_ia.py`, `dashboard.py`).
  - `src/utils/`: Logger estruturado ([`logger.py`](./src/utils/logger.py)).

---

## 📅 Linha do Tempo e Registro de Sessões

### [Sessão 1 a 3] - Estruturação Base, Geometria e Hidráulica
- Modularização do simulador a partir dos protótipos legados.
- Criação dos módulos de geometria, modelos de fluxo reológico (Bingham, Power Law) e perfis operacionais de pressão.

### [Sessão 4] - Banco de Aditivos e Balanço de Massas Rigoroso
- Criação da base de dados [`data/aditivos_db.json`](./data/aditivos_db.json).
- Algoritmo de balanço de massas rigoroso para rendimento da pasta ($ft^3/sk$), água requerida ($gal/sk$), densidade ($ppg$) e volume de sacos.

### [Sessão 5] - Agente IA Multi-Provedor (Groq Cloud + Ollama Local) e Guardrails Determinísticos
- Integração da Groq Cloud API e Ollama Local com motor de validação determinística de engenharia ([`src/services/requisitos_ia.py`](./src/services/requisitos_ia.py)) para 100% de conformidade técnica.

### [Sessão 6] - Governança Antigravity e Trilha Pedagógica em 3 Níveis
- Criação do [`GEMINI.md`](./GEMINI.md) e reorganização total da pasta `docs/` em 3 níveis de profundidade (Fundamentos, Sistema/IA, Acadêmico/Normativo).

### [Sessão 7] - Modernização Visual, Esquemático 2D Didático e Programa Completo de IA
- **O que foi feito:**
  - **Recomendação Autônoma de Programa Completo (Lead + Tail Slurry) na Aba 3 (`tab_agente_ia.py`):** Dimensionamento bi-pasta com aplicação mestre em 1 clique.
  - **Auditoria Ponto a Ponto da Janela Operacional:** Varredura em toda a profundidade ($0 \le z \le z_{max}$), identificando exatamente intervalos de fratura e kick.
  - **Esquemático 2D Didático:** Sapata enfatizada e cotas dimensionais completas no padrão do exercício.
  - **Protocolo de Encerramento Automático (`logoff`):** Regra no `GEMINI.md` para fechamento e auditoria com um único comando.

### [Sessão 8] - Preparação para Deploy Online & Proteção de Chaves de API (Data Atual)
- **O que foi feito:**
  - **Suporte Híbrido a Segredos em `config.py`:** Função `_obter_groq_api_key()` lê tanto de `.env` (local) quanto de `st.secrets` (Streamlit Cloud na nuvem).
  - **Proteção Total contra Vazamentos ([`.gitignore`](./.gitignore)):** Bloqueio estrito de arquivos `.env`, `logs/`, caches e arquivos temporários.
  - **Atualização do `requirements.txt`:** Inclusão explícita de `numpy` e dependências para deploy limpo em nuvem.
  - **Criação do Guia de Deploy Online ([`docs/02_SISTEMA_E_IA/04_guia_deploy_online.md`](./docs/02_SISTEMA_E_IA/04_guia_deploy_online.md)):** Passo a passo para publicação no Streamlit Community Cloud com chave criptografada.

---

## 🎯 Estado Atual do Projeto

- **Status Geral:** ✅ Simulador de cimentação 100% pronto para publicação na web (Streamlit Community Cloud), com suporte a chave Groq criptografada nos servidores da nuvem, sem risco de vazamento no código.

---

## 🚀 Próximos Passos Sugeridos / Backlog

1. **Deploy no Streamlit Community Cloud:**
   - Criar o repositório no GitHub e conectar ao Streamlit Cloud seguindo o guia.
2. **Exportação de Relatórios de Engenharia (PDF/Excel):**
   - Gerar memorial de cálculo para entrega operacional ou acadêmica.
3. **Eficiência de Deslocamento e Centralização (Standoff):**
   - Modelar o perfil de standoff da coluna no poço e a taxa de remoção do fluido de perfuração.
