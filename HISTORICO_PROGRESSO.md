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

### [Sessão 9] - Módulo de Janelas Operacionais: Sandbox, Benchmark e 5ª Aba de Curvas Reais
- **Data/Hora:** 2026-09-24 08:20
- **Principais Entregas e Validações:**
  1. **Ambiente Isolado de Incubação (`sandbox/janela_operacional/`):**
     - Criação da área de staging para recepção de módulos externos e subprojetos de pesquisa.
     - Extração, engenharia reversa e auditoria completa do Jupyter Notebook (`Simulador_Geopressões__versao_mar_do_norte (1).ipynb`).
  2. **Auditoria e Benchmark Numérico com Coincidência de 100%:**
     - Criação do script de validação [`sandbox/janela_operacional/validador_benchmark.py`](./sandbox/janela_operacional/validador_benchmark.py).
     - Execução do motor físico (Sobrecarga por Gardner, Poro por Eaton sônico, Fratura por LOT e Colapso por Mohr-Coulomb) confrontando os 5 poços do Bloco 15/9 (Mar do Norte) e suas 3 variantes (A, B e K).
     - Validação contra os CSVs da pasta `resultados/`: **erro máximo = 0.000000 em todas as colunas**.
  3. **Criação do Serviço de Geomecânica ([`src/services/geomecanica_service.py`](./src/services/geomecanica_service.py)):**
     - Módulo de serviço independente para carregar presets de poços e realizar o parsing flexível de qualquer CSV enviado pelo usuário.
  4. **Implementação da 5ª Aba ([`src/ui/tab_geomecanica.py`](./src/ui/tab_geomecanica.py)):**
     - Interface de alta fidelidade para selecionar poços históricos do Mar do Norte ou subir CSV próprio.
     - Telemetria de gargalo da janela, profundidade máxima e gráfico dedicado contínuo.
  5. **Integração Segura e Não-Invasiva no Dashboard ([`src/ui/dashboard.py`](./src/ui/dashboard.py)):**
     - Adição do toggle para alternar entre "Curvas Reais de Campo" e a aproximação analítica original.
     - Superposição da curva de EMW da coluna de cimento sobre as curvas reais com detecção automática de violações de fratura ou influxo/colapso.
  6. **Validação & Testes:**
     - Todos os 21 módulos Python compilados com 100% de sucesso (`py_compile`).
     - Testes de renderização executados com sucesso tanto no modo com perfil real ativo quanto no modo de fallback original.

### [Sessão 10] - Pipeline Linear de Engenharia de Poço (5 Abas Integradas)
- **Data/Hora:** 2026-09-24 08:58
- **Principais Entregas e Reestruturação Arquitetural:**
  1. **Reestruturação Linear das Abas (`app.py`):**
     - O simulador foi transformado em uma esteira sequencial e intuitiva de engenharia de cimentação:
       - `🌐 1. Janela Geomecânica & Perfis`
       - `📐 2. Geometria & Banco de Aditivos`
       - `🧠 3. Módulo Especialista (IA)`
       - `🧪 4. Configuração das Pastas`
       - `📊 5. Telemetria & Dashboard Final`
  2. **Aba 1 - Janela Geomecânica & Perfis (`tab_geomecanica.py`):**
     - Ponto inicial do poço: permite carregar presets do Mar do Norte (Bloco 15/9) ou fazer upload de CSVs customizados.
     - Métricas industriais (TD, gargalo mínimo, profundidade crítica, poro e fratura de fundo).
     - Gráfico de curvas removido da Aba 1 (centralizado exclusivamente no Dashboard final) e tabela de dados com download CSV.
  3. **Aba 2 - Geometria & Banco de Aditivos (`tab_parametros_poco.py`):**
     - Conexão nativa com a Aba 1: botão `🪄 Puxar Dados do Poço` preenche automaticamente diâmetros e densidade de lama, permitindo total edição manual.
     - Inicialização limpa no `st.session_state` sem conflito ou warnings de valores padrão.
  4. **Aba 3 - Módulo Especialista IA (`tab_agente_ia.py`):**
     - Exibição de resumo executivo dos dados extraídos da Aba 1 (TD, Poro, Fratura, Lama, BHCT previsto).
     - Botão `🪄 Sincronizar com Perfil da Aba 1` que ajusta automaticamente os limites de pressão, estimativa térmica e riscos geológicos.
     - Tratamento seguro de credenciais via `_obter_secret_seguro()` eliminando erro `StreamlitSecretNotFoundError` no Streamlit Cloud e local.
     - Aplicação de formulação redirecionada diretamente para a Aba 4 (ajustando `num_pastas_anular = 2` no caso de programa completo Lead + Tail).
  5. **Aba 4 - Configuração das Pastas (`tabs_pastas.py`):**
     - Banner de continuidade indicando formulação pré-carregada pela IA.
     - Controle reativo do número de pastas anulares (`key="num_pastas_anular"`).
     - Interface de calibração fina de dosagens (% BWOC), alturas e volumes.
  6. **Aba 5 - Telemetria & Dashboard Final (`dashboard.py`):**
     - SCADA cards executivos, esquemático 2D do poço em corte.
     - Plot contínuo das curvas geomecânicas reais (Sobrecarga, Fratura, Poro, Colapso, Lama e EMW da Coluna de Cimento).
     - Auditoria em tempo real com identificação de profundidades com risco de fratura ou perda de integridade/kick.
     - Balanço de massa e ficha de traço de campo (batch sheet).
  7. **Validação & Testes:**
     - Todos os módulos do simulador compilados com 100% de sucesso (`py_compile`).
     - Teste unitário de execução do pipeline completo (geomecânica -> geometria -> IA -> pastas -> hidráulica -> dashboard) sem regressões.

### [Sessão 11] - Arquitetura Multi-Pasta (Bi, Tri e Tetra-Pastas) & Guardrails Estritos Anti-Alucinação
- **Data/Hora:** 2026-09-24 09:34 (Sessão Encerrada com Sucesso)
- **Principais Entregas e Engenharia de Prompt & Guardrails:**
  1. **Expansão Arquitetural Multi-Pasta (Aba 3 & Aba 4):**
     - Atendimento à diretriz acadêmica e de campo (Poli-USP): suporte completo a programas de **Bi-pasta** (Lead + Tail), **Tri-pasta** (Lead + Middle/Reservatório + Tail), **Tetra-pasta** (Scavenger/Varredura + Lead + Middle + Tail) e **Pastas Individuais Customizadas** (1 a 4).
     - Dimensionamento térmico e geomecânico refinado por intervalos específicos:
       - *Scavenger Slurry:* Pasta ultraleve (11.0–12.0 ppg) com alta dispersão para lavagem de poço e remoção de reboco sob regime turbulento.
       - *Lead Slurry:* Pasta de preenchimento leve (12.0–13.8 ppg) com baixo empuxo para proteção de zonas rasas e alívio do gradiente de fratura.
       - *Middle Slurry:* Pasta intermediária de isolamento (14.0–15.2 ppg) com controlador de filtrado mandatório (< 50 mL API RP 10B) para vedação de hidrocarbonetos e proteção do reservatório.
       - *Tail Slurry:* Pasta de alta densidade e resistência mecânica (15.5–16.5 ppg) com estabilizador térmico mandatório (Flor de Sílica SSA-1 30–35% BWOC) para $BHST > 110^\circ\text{C}$.
  2. **Guardrails Determinísticos Invioláveis contra Alucinações de LLM ([`src/services/requisitos_ia.py`](./src/services/requisitos_ia.py)):**
     - Criação da matriz `LIMITES_FISICOS_DOSAGEM` com limites absolutos de campo (% BWOC) por categoria funcional (Retardador: 0.05–2.0%, Dispersante: 0.05–1.5%, Filtrado: 0.1–2.5%, Extensor: 0.5–15.0%, Densificante: 5.0–50.0%, Estabilizador Térmico: 30.0–35.0%).
     - Rejeição e bloqueio imediato com autocorreção determinística de dosagens negativas, nulas ou fisicamente absurdas (ex: alucinação de 15% de dispersante é bloqueada).
     - Catálogo fechado rigorosamente mantido: qualquer aditivo fora de [`data/aditivos_db.json`](./data/aditivos_db.json) é sumariamente rejeitado.
  3. **Verificação Hidrodinâmica de Inversão de Empuxo (Rayleigh-Taylor):**
     - Implementação da função `validar_hierarquia_programa(pastas, dens_lama)`:
       - Garante a progressão crescente e segura de densidades: $\rho_{lama} < \rho_{scavenger} \le \rho_{lead} < \rho_{middle} < \rho_{tail} < \text{Fratura}$.
       - Detecção e alerta imediato de inversão de densidades que poderiam causar instabilidade ou canalização anular.
  4. **Atualização Dinâmica da Aba 4 (Configuração de Pastas - [`src/ui/tabs_pastas.py`](./src/ui/tabs_pastas.py)):**
     - Rotulagem semântica adaptativa das abas internas (`_rotulo_pasta`) de 1 a 4 pastas (ex: Sapata/Tail, Intermediária/Reservatório, Preenchimento/Lead, Varredura/Scavenger).
     - Sincronização via `st.session_state["num_pastas_anular"]` permitindo que a IA configure com 1 clique a quantidade exata de pastas na Aba 4.
  5. **Painel de Telemetria de Trem de Fluidos (Aba 3 - [`src/ui/tab_agente_ia.py`](./src/ui/tab_agente_ia.py)):**
     - Seletor de estratégia multi-pasta (Bi, Tri, Tetra ou Pasta Individual).
     - Visualização em tempo real do trem de fluidos com contrastes de densidade passo a passo ($\Delta \rho$).
     - Botão de aplicação direta com redirecionamento de estado para a Aba 4.
  6. **Validação & Testes:**
     - Compilação sem erros em todos os módulos (`src/` e `app.py`).
     - Testes unitários com sucesso para 1, 2, 3 e 4 pastas no motor de cálculo (`calculadora.py`), requisitos e hierarquia.

---

## 🎯 Estado Atual do Projeto

- **Status Geral:** ✅ Simulador 100% atualizado, operando com arquitetura multi-pasta (1 a 4 pastas: Tail, Intermediária, Lead e Scavenger), blindagem determinística contra alucinações de LLM e pipeline linear integrado de 5 abas.

---

## 🚀 Próximos Passos Sugeridos / Backlog

1. **Validação Visual do Usuário no Servidor Local:**
   - Conferir a navegação entre as 5 abas no `localhost:8501`.
2. **Deploy Contínuo no Streamlit Cloud:**
   - Realizar o commit e push para o repositório remoto para publicação online em `simulador-cimentacao-usp.streamlit.app`.
3. **Exportação de Relatórios de Engenharia (PDF/Excel):**
   - Implementação do motor de relatórios especificado em [`docs/plano_exportacao_relatorio.md`](./docs/plano_exportacao_relatorio.md).


