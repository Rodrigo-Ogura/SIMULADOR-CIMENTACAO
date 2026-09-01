# 📜 Histórico de Progresso do Projeto: Simulador de Cimentação

Documento de registro contínuo de evolução, alterações de código, testes e próximos passos.
> **Regra:** Este documento é consultado no início de cada sessão e atualizado a cada alteração relevante conforme definido em [`GEMINI.md`](./GEMINI.md).

---

## 🏗️ Visão Geral da Arquitetura do Projeto

- **Linguagem & Frameworks:** Python 3.10+, Streamlit, Plotly, NumPy, Pandas, Pydantic, Groq Cloud API, Ollama Local.
- **Design System:** Estilo industrial de alta fidelidade inspirado no **OpenLab Drilling (NORCE)** (Dark Slate Theme `#0b0f19`, Cartões Digitais SCADA de Telemetria via `st.html`, Esquemático 2D Didático, Janela de Pressão Geomecânica e Recomendador de Programa Completo Multi-Pasta).
- **Repositório & Deploy:** GitHub oficial ([github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO](https://github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO)) integrado com deploy contínuo no **Streamlit Community Cloud** ([simulador-cimentacao-usp.streamlit.app](https://simulador-cimentacao-usp.streamlit.app)).
- **Estrutura de Pastas:**
  - `app.py`: Ponto de entrada do simulador Streamlit integrando cabeçalho de telemetria traduzido em português, abas e tema OpenLab.
  - `config.py`: Constantes físicas API, configurações de ambiente (`.env` local ou `st.secrets` na nuvem), catálogo padrão de aditivos e parâmetros de IA.
  - `data/`: Banco de dados persistente em JSON ([`aditivos_db.json`](./data/aditivos_db.json)).
  - `docs/`: Base pedagógica e normativa estruturada em 3 níveis (Fundamentos, Sistema/IA, Acadêmico/Normativo), guia de deploy e anexos em PDF.
  - `src/models/`: Modelos de dados de aditivos ([`aditivo.py`](./src/models/aditivo.py)) e pastas de cimento ([`pasta.py`](./src/models/pasta.py)).
  - `src/services/`: Motores matemáticos, persistência e IA (`calculadora.py`, `aditivo_service.py`, `groq_agent_service.py`, `ollama_agent_service.py`, `requisitos_ia.py`).
  - `src/ui/`: Telas e componentes visuais (`sidebar.py`, `tab_parametros_poco.py`, `tabs_pastas.py`, `tab_agente_ia.py`, `dashboard.py`).
  - `src/utils/`: Logger estruturado ([`logger.py`](./src/utils/logger.py)).

---

## 📅 Linha do Tempo e Registro de Sessões

### [Sessões Anteriores 1 a 6] - Fundamentos, Balanço de Massas e Módulo de IA
- Modularização da arquitetura, equações estequiométricas rigorosas, persistência em JSON, agente híbrido (Groq + Ollama) e governança em `docs/`.

### [Sessão 7 e 8] - Deploy em Nuvem, Guardrails de Lama, Resolução de Erros e Polimento Visual (Sessão Atual)
- **Data/Hora de Encerramento:** 2026-09-01 16:22
- **Principais Entregas e Correções:**
  1. **Publicação Online e Deploy no Streamlit Cloud:**
     - Aplicação publicada com sucesso no link oficial: [**simulador-cimentacao-usp.streamlit.app**](https://simulador-cimentacao-usp.streamlit.app).
     - Integração com `st.secrets` para proteção criptografada da chave `GROQ_API_KEY`.
     - Atualização do [`README.md`](./README.md) destacando o link oficial direto e o botão de acesso instantâneo para orientadores e alunos.
  2. **Configuração de Autoria do Git:**
     - Reatribuição de todo o histórico de commits do repositório para o perfil oficial: `Rodrigo-Ogura <rodrigokcogura@gmail.com>`.
  3. **Integração Total da Densidade da Lama de Perfuração ($\rho_{lama}$):**
     - Campo de densidade de lama adicionado à **Aba 3 (Módulo Especialista)** e sincronizado com a **Aba 1 (Geometria)** e **Aba 4 (Dashboard)**.
     - Guardrails determinísticos baseados em **Bourgoyne et al. (Cap. 3)** e **Nelson & Guillot (Cap. 10)** para validação de overbalance ($\rho_{lama} \ge Grad_{poro} + 0{,}3\text{ ppg}$) e contraste de deslocamento hidrostático ($\rho_{lama} < \rho_{lead} \le \rho_{tail}$).
  4. **Correções de Compatibilidade e Ciclo de Vida do Streamlit Cloud:**
     - Implementação dos métodos `obter_dataframe()`, `salvar_banco()` e `restaurar_padrao()` em `AditivoService` com tratamento defensivo de erros (`AttributeError` resolvido).
     - Centralização da inicialização do `st.session_state` no topo do `app.py` eliminando conflito de chaves e `StreamlitWidgetAlreadyInstantiatedError`.
  5. **Tradução e Polimento Visual:**
     - Barra de status superior (*rig-header*) e `page_title` traduzidos para o português: *"Simulador de Cimentação & Engenharia de Poço | Poli-USP"*.
  6. **Validação & Teste de Compilação:**
     - Todos os 14 módulos Python verificados com sucesso (`python -m py_compile`).

---

## 🎯 Estado Atual do Projeto

- **Status Geral:** ✅ Simulador 100% funcional, estável, online no Streamlit Cloud e sincronizado com o GitHub oficial.

---

## 🚀 Próximos Passos Sugeridos / Backlog

1. **Exportação de Relatórios de Engenharia (PDF/Excel):**
   - Implementar a geração de memorial descritivo em PDF/Excel com dados da geometria, ficha de traço das pastas, gráfico da janela operacional e parecer de IA.
2. **Eficiência de Deslocamento e Centralização (Standoff):**
   - Incorporar o perfil de centralização do revestimento (*standoff ratio*) e o cálculo analítico da eficiência volumétrica de remoção do reboco/lama no anular.
