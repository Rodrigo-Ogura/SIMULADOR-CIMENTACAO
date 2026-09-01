# 📜 Histórico de Progresso do Projeto: Simulador de Cimentação

Documento de registro contínuo de evolução, alterações de código, testes e próximos passos.
> **Regra:** Este documento é consultado no início de cada sessão e atualizado a cada alteração relevante conforme definido em [`GEMINI.md`](./GEMINI.md).

---

## 🏗️ Visão Geral da Arquitetura do Projeto

- **Linguagem & Frameworks:** Python 3.10+, Streamlit, Plotly, NumPy, Pandas, Pydantic, Groq Cloud API, Ollama Local.
- **Design System:** Estilo industrial de alta fidelidade inspirado no **OpenLab Drilling (NORCE)** (Dark Slate Theme `#0b0f19`, Cartões Digitais SCADA de Telemetria via `st.html`, Esquemático 2D Didático, Janela de Pressão Geomecânica e Recomendador de Programa Completo Multi-Pasta).
- **Repositório & Deploy:** GitHub oficial ([github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO](https://github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO)) integrado com deploy contínuo no **Streamlit Community Cloud** ([simulador-cimentacao-usp.streamlit.app](https://simulador-cimentacao-usp.streamlit.app)).
- **Estrutura de Pastas:**
  - `app.py`: Ponto de entrada do simulador Streamlit integrando cabeçalho de telemetria, abas e tema OpenLab.
  - `config.py`: Constantes físicas API, configurações de ambiente (`.env` local ou `st.secrets` na nuvem), catálogo padrão de aditivos e parâmetros de IA.
  - `data/`: Banco de dados persistente em JSON ([`aditivos_db.json`](./data/aditivos_db.json)).
  - `docs/`: Base pedagógica e normativa estruturada em 3 níveis (Fundamentos, Sistema/IA, Acadêmico/Normativo), guia de deploy e anexos em PDF.
  - `src/models/`: Modelos de dados de aditivos ([`aditivo.py`](./src/models/aditivo.py)) e pastas de cimento ([`pasta.py`](./src/models/pasta.py)).
  - `src/services/`: Motores matemáticos, persistência e IA (`calculadora.py`, `aditivo_service.py`, `groq_agent_service.py`, `ollama_agent_service.py`, `requisitos_ia.py`).
  - `src/ui/`: Telas e componentes visuais (`sidebar.py`, `tab_parametros_poco.py`, `tabs_pastas.py`, `tab_agente_ia.py`, `dashboard.py`).
  - `src/utils/`: Logger estruturado ([`logger.py`](./src/utils/logger.py)).

---

## 📅 Linha do Tempo e Registro de Sessões

### [Sessão 1 a 6] - Estruturação Base, Balanço de Massas, IA e Trilha Pedagógica
- Modularização inicial, balanço de massas rigoroso, integração Groq/Ollama com guardrails e documentação em 3 níveis.

### [Sessão 7 e 8] - Modernização Visual OpenLab, Deploy Online e Guardrails de Lama
- **Recomendação de Programa Completo Bi-Pasta (Lead + Tail Slurry)** com aplicação mestre em 1 clique.
- **Integração Total da Densidade da Lama de Perfuração ($\rho_{lama}$)** com validação de overbalance e hierarquia de deslocamento hidrostático.
- **Deploy Online Seguro no Streamlit Cloud & GitHub** ([simulador-cimentacao-usp.streamlit.app](https://simulador-cimentacao-usp.streamlit.app)).
- **Tradução da Barra de Status para Português:** *"Simulador de Cimentação & Engenharia de Poço"*.
- **Correção em `AditivoService` (`aditivo_service.py`):**
  - Implementação dos métodos `obter_dataframe()`, `salvar_banco()` e `restaurar_padrao()` com verificações defensivas completas.
- **Correção de Ciclo de Vida de Estado do Streamlit (`StreamlitWidgetAlreadyInstantiatedError`):**
  - Centralização da inicialização das variáveis de sessão no topo de `app.py` antes da criação de widgets.
  - Eliminação de duplicidade de chaves de widgets entre a Aba 1 e Aba 3.
  - Enviado para o GitHub (`git push`) e sincronizado no Streamlit Cloud.

---

## 🎯 Estado Atual do Projeto

- **Status Geral:** ✅ Simulador de cimentação completo, online no GitHub e Streamlit Cloud, livre de erros de execução e pronto para uso imediato via web.

---

## 🚀 Próximos Passos Sugeridos / Backlog

1. **Exportação de Relatórios de Engenharia (PDF/Excel):**
   - Gerar memorial de cálculo em PDF/Excel com o esquemático 2D, ficha de traço operacional e parecer da IA.
2. **Eficiência de Deslocamento e Centralização (Standoff):**
   - Modelar o perfil de centralização da coluna no poço e o cálculo analítico da taxa de remoção do fluido de perfuração.
