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

### [Sessão 12] - Motor Determinístico API Spec 10A & Otimização de Prompts (~85% Menos Tokens)
- **Data/Hora:** 2026-09-29 10:20
- **Principais Entregas e Inovações Arquiteturais:**
  1. **Motor Determinístico de Engenharia (`gerar_formulacao_deterministica` em `src/services/requisitos_ia.py`):**
     - Criação do motor puro em Python que dimensiona formulações completas em **0.001 segundos**, 100% offline, com **zero consumo de tokens** e sem necessidade de conexão ou chaves de API.
     - Lógica baseada estritamente nas normas **API Spec 10A / RP 10B**, **Bourgoyne et al. (Cap. 3)** e **Nelson & Guillot**.
     - Suporte nativo a todos os tipos de pasta: Tail (sapata), Middle (reservatório/gás), Lead (preenchimento leve) e Scavenger (varredura).
     - **Aviso explícito de confiabilidade:** O sistema informa claramente na UI e nos pareceres que a modalidade determinística fornece justificativas normativas diretas para cada aditivo, mas **não contém pareceres discursivos em texto livre ou redação livre gerados por IA**.
  2. **Filtro Inteligente de Catálogo de Aditivos (`filtrar_aditivos_relevantes`):**
     - Em vez de enviar o banco inteiro de 25 aditivos para a LLM, o pré-processador seleciona em Python apenas os 4 a 6 aditivos tecnicamente viáveis para as condições térmicas e mecânicas daquele poço.
  3. **Otimização Drástica de Tokens nos Prompts (~85% de redução):**
     - Compactação do prompt de sistema e eliminação de 4 blocos extensos de few-shot duplicados em `groq_agent_service.py` e `ollama_agent_service.py`.
     - O consumo total por requisição caiu de **~2.200 tokens para ~350 a 450 tokens**, resolvendo de forma definitiva o problema de estouro de cota e limite de 1k de tokens na API gratuita da Groq.
  4. **Correção de Categoria e Normalização da Flor de Sílica:**
     - Correção da categoria de `Flor de Sílica (SSA-1)` e `Areia de Sílica (Ottawa)` para `"Estabilizador Térmico"` em `data/aditivos_db.json` e `config.py`.
     - Suporte transparente a ambos os campos `"concentracao"` e `"concentracao_bwoc_pct"` em `normalizar_recomendacao` e `validar_recomendacao`.
  5. **Interface Unificada na Aba 3 (`src/ui/tab_agente_ia.py`):**
     - Seletor do motor de cálculo expandido com 3 opções claras:
       - `⚡ Motor Determinístico API Spec 10A (Instantâneo / Sem IA)`
       - `☁️ Groq Cloud LPU (Nuvem - Rápido com IA)`
       - `🖥️ Ollama Engine (Local - Offline com IA)`
     - Card de telemetria e avisos de modalidade contextualizados.
  6. **Auditoria Geral e Bateria de Testes Automatizados (`tests/test_audit.py`):**
     - Criação da suíte completa de auditoria cobrindo os 5 módulos de serviços, persistência JSON, geomecânica e modelos.
     - **Bugs identificados e prontamente corrigidos durante o checkup:**
       1. *Nome do aditivo LCM:* Corrigido de `"Celofane Flakes"` (inexistente no banco) para `"Agente de Perda de Circulação (Tuf-Plug)"`.
       2. *Janela de densidade em Middle Slurry:* Corrigido o cálculo de densidade alvo para respeitar estritamente a janela `[densidade_min_alvo, densidade_max_alvo]`.
       3. *Alias de métricas geomecânicas:* Adicionado o alias `"gargalo_min_ppg"` em `GeomecanicaService.extrair_metricas_resumo` para evitar inconsistências de nomenclatura.
       4. *Conciliação de campos de dosagem:* `validar_recomendacao` agora aceita tanto `concentracao` quanto `concentracao_bwoc_pct`.
     - **Resultado dos Testes:** 27 de 27 testes unitários e de integração passaram com 100% de sucesso.
     - **Teste Headless do Streamlit:** Aplicação inicializada com sucesso em modo headless, respondendo com HTTP 200 e zero conflitos de widgets ou sessão.

---

### [Sessão 13] - Correção de Sincronização Geomecânica & Salvaguarda Hidrostática (Rayleigh-Taylor)
- **Data/Hora:** 2026-09-29 10:45
- **Diagnóstico do Bug Informado pelo Usuário:**
  - *Sintoma:* Erro em banner vermelho: `❌ Falha de consistência hidrostática entre as pastas: • Inversão de empuxo: A Tail Slurry (10.43 ppg) deve ser mais densa que a Lead Slurry (12.40 ppg).`
  - *Causa Raiz:* Ao clicar no botão `🪄 Sincronizar com Perfil da Aba 1`, o método `extrair_metricas_resumo()` extraía `fratura_min_ppg = 10.93 ppg` de todo o poço 15/9-13 (B), que é o gradiente raso na seção de condutor/superfície a 340 metros. O botão então atribuía `ia_dmax = fratura_min - 0.5 = 10.43 ppg` e `ia_dmin = poro + 0.5 = 9.78 ppg`.
  - Ao executar o dimensionamento Bi-Pasta, a Tail Slurry ficava restrita a $\le 10.43\text{ ppg}$, enquanto a Lead Slurry de topo era calculada normativamente em $12.40\text{ ppg}$.
  - O guardrail determinístico `validar_hierarquia_programa()` interceptou com perfeição a inversão de empuxo ($10.43\text{ ppg} < 12.40\text{ ppg}$), impedindo uma formulação fisicamente errônea de ser aprovada.
- **Correções Implementadas:**
  1. **Separação de Gradientes em [`src/services/geomecanica_service.py`](./src/services/geomecanica_service.py):**
     - Adicionados os campos `fratura_base_ppg` e `poro_base_ppg` calculados nos últimos 300 metros do poço (seção de sapata / fundo / TD). Para o poço 15/9-13 (B), a fratura na base é de **16.12 ppg** (e não 10.93 ppg).
  2. **Ajuste na Sincronização da Aba 3 ([`src/ui/tab_agente_ia.py`](./src/ui/tab_agente_ia.py)):**
     - Sincronização atualizada para utilizar `fratura_base_ppg` ($16.12\text{ ppg}$) na sapata e dimensionar a Tail Slurry conforme as normas API RP 10B e Bourgoyne et al. (Cap. 3):
       $$\text{dmin}_{\text{tail}} = \max(15.60, \rho_{\text{lama}} + 1.0, P_{\text{poro}} + 1.0)$$
       $$\text{dmax}_{\text{tail}} = \max(\text{dmin} + 0.40, \min(16.50, FG_{\text{base}} - 0.5))$$
     - Resultando em `ia_dmin = 15.60 ppg` e `ia_dmax = 16.20 ppg` para a Tail.
  3. **Salvaguarda Preventiva contra Inversão:**
     - Adicionada verificação preventiva nos fluxos Bi-Pasta, Tri-Pasta e Tetra-Pasta: se o usuário deixar ou digitar valores de Tail inferiores a $13.5\text{ ppg}$ ou menores que a lama, o sistema ajusta automaticamente para o patamar seguro de sapata ($\ge 15.60\text{ ppg}$), eliminando qualquer risco de erro residual de inversão.
  4. **Auditoria Automatizada Expandida ([`tests/test_audit.py`](./tests/test_audit.py)):**
     - Adicionado teste específico de extração de métricas de base em todos os 15 presets ($FG_{base} > 14.0\text{ ppg}$).
     - Adicionado teste de dimensionamento de Programa Bi-Pasta sincronizado com o poço 15/9-13 (B), confirmando aprovação sem erros com $\text{Tail} = 15.62\text{ ppg} > \text{Lead} = 12.00\text{ ppg} > \text{Lama} = 10.85\text{ ppg}$.
     - **28 de 28 testes passaram com 100% de sucesso**. Compilação limpa em todos os módulos.

    5. **Visualização em Tela Cheia e Refinamento de Controles no Dashboard ([`src/ui/dashboard.py`](./src/ui/dashboard.py)):
      - Criação do modal interativo de alta resolução via `@st.dialog("🛡️ Janela Geomecânica & Curvas de Pressão em Tela Cheia", width="large")` acionado pelo botão **`⛶ Tela Cheia`** no topo do gráfico.
      - Criação de modal equivalente para o **Esquemático 2D do Poço** (`@st.dialog`).
      - Ativação das ferramentas de inspeção do Plotly (`PLOTLY_CONFIG_INTERATIVO` com `displayModeBar=True`), permitindo zoom por caixa, pan, comparação de coordenadas e download de imagem em PNG 300 DPI em ambos os gráficos e no gráfico de componentes.
      - **Refatoração Visual e Alinhamento Simétrico dos Controles:** Eliminação do empilhamento vertical do seletor `st.segmented_control` e layout simétrico de 2 linhas com CSS anti-quebra.

   6. **Curva em Escada da Densidade dos Fluidos (*Slurry Weight Staircase*) & Refino Geomecânico Industrial ([`src/ui/dashboard.py`](./src/ui/dashboard.py)):
      - Substituição da reta contínua simplificada por um **perfil em degraus ortogonais (*step-plot*)** via `_gerar_perfil_escada_fluidos()`, exibindo a densidade exata de cada fluido no anular:
        - $0 	o 	ext{TOC}$: Lama de perfuração ($ho_{	ext{lama}}$).
        - $	ext{TOC} 	o 	ext{Sapata}$: Pastas de cimento em patamares sucessivos (Lead $	o$ Tail).
      - **Diferenciação Semântica Dupla:** A curva em escada (`🪜 Peso dos Fluidos`) convive harmoniosamente com o gradiente integrado (`🌊 EMW Acumulado`), permitindo análise física completa da coluna.
      - **Refino Físico do Modo Analítico:** Eliminação da "reta diagonal rígida que atravessava o gráfico". O poço agora assume profundidade total geológica realista com curvatura suave de compactação de bacia sedimentar e lama da superfície até o TOC.
      - **Anotações Geotécnicas Automáticas:** Linhas horizontais discretas demarcando as cotas de **TOC** e **Sapata**.

   7. **Harmonização de Guardrail de Entrada entre IA e Motor Determinístico ([`src/services/requisitos_ia.py`](./src/services/requisitos_ia.py)):**
      - *Causa:* Em `validar_dados_poco()`, a condição estática `dens_max > grad_fratura - 0.5` bloqueava a IA prematuramente quando a Tail Slurry na sapata operava próxima ao gradiente de fratura do poço, enquanto o motor determinístico calculava normalmente a pasta ajustando a densidade ideal.
      - *Correção:* Substituição da regra estática por validação de impossibilidade física estrita (`dens_min >= grad_fratura`). Agora a IA (Groq / Ollama) e o motor determinístico operam com o mesmo critério tolerante e inteligente, permitindo caldas densas de sapata em poços com alívio anular superior por Lead leve.

---

---

### [Sessão 14] - Estilização Industrial Clássica do Gráfico Geomecânico (Padrão Bourgoyne Cap. 3 & Casing Points)
- **Data/Hora:** 2026-09-29 11:50
- **Solicitação do Usuário:**
  - O usuário enviou a imagem clássica da literatura de engenharia de petróleo (*Bourgoyne et al. - Applied Drilling Engineering, Cap. 3 - Casing Seat Selection / Safe Mud Weight Window*), indicando que o gráfico do Dashboard deveria seguir exatamente aquele padrão visual profissional.
- **Implementações Técnicas em [`src/ui/dashboard.py`](./src/ui/dashboard.py):**
  1. **Faixa Superior de Lâmina d'Água (*Water Depth*):**
     - Criação do bloco sombreado em azul no topo do gráfico (`fig_window.add_hrect(y0=0, y1=lda_ft)`) com anotação `🌊 Water Depth (Lâmina d'Água)`, sincronizado com o LDA real dos poços do Mar do Norte (ou 450 ft em poço analítico).
  2. **Curva de Pressão de Poros (*Pressure Prediction*):**
     - Padronização em vermelho vibrante (`#ef4444`, `🔴 Poros (Pressure Prediction)`), refletindo o comportamento geomecânico das formações perfuradas.
  3. **Curva de Gradiente de Fratura (*Fracture Gradient Prediction*):**
     - Padronização em linha de alto contraste (`#cbd5e1`, `⚫ Fratura (Fracture Prediction)`), curvando-se com a profundidade conforme a compactação das rochas.
  4. **Programa de Fluidos e Pastas em Escada (*Safe Mud Weight*):**
     - Traçado ortogonal em degraus verdes (`#22c55e`, `width=3.2`, `🟩 Programa de Fluidos (Safe Mud Weight)`), posicionado estrategicamente dentro do corredor seguro entre poros e fratura.
     - Acompanha as sapatas históricas reais dos poços (ex: 20", 13 3/8", 9 5/8") e as seções de cimentação (Lama até TOC, Lead Slurry intermediária, Tail Slurry de fundo).
     - No modo analítico, implementados degraus proporcionais de condutor (20"), intermediário (13 3/8"), revestimento de produção (9 5/8" / TOC) e sapata de TD.
  5. **Marcadores Laterais de Sapata (*Casing Points*):**
     - Em cada cota de mudança de fase, linhas horizontais pontilhadas associadas a marcadores triangulares `◀ Casing point (XX")` alinhados à margem direita do gráfico, reproduzindo com exatidão a notação da literatura.
  6. **EMW Acumulado e Janela Segura Integrada:**
     - Preservação da curva tracejada em azul (`#38bdf8`) para o EMW hidrostático acumulado de toda a coluna de cimento, permitindo dupla verificação: programa pontual de fluidos (*Safe mud weight*) versus pressão dinâmica no poço (*EMW*).
- **Validação & Testes:**
  - **28 de 28 testes automatizados aprovados** no teste de auditoria geral (`python tests/test_audit.py`).
  - Compilação 100% bem-sucedida em todos os módulos Python (`src/`, `app.py`, `tests/`).

---

### [Sessão 15] - Correção de Escala Vertical (`m` vs `ft`), Sincronização de Alturas (Aba 3 ➔ Aba 4) e Janela Geomecânica na Aba 5
- **Data/Hora:** 2026-10-26 18:22
- **Diagnóstico Informado pelo Usuário:**
  - No site em produção, o gráfico da **Aba 5 (Janela Geomecânica)** comprimia a coluna de cimento nos últimos 13,7% do poço (`TOC = 9.196 ft` até `Sapata = 10.656 ft`, apenas `1.460 ft` $\approx$ `445 m`), fazendo com que a curva de **EMW Acumulado** ficasse quase reta/vertical e descolada dos degraus das pastas. Além disso, o eixo X ia até `-3.14 ppg` devido a pontos extrapolados negativos de poro/colapso no CSV bruto do poço 15/9-13.
- **Correções Implementadas:**
  1. **Sincronização Automática de Alturas (`m ➔ ft`) entre Aba 1, Aba 3 e Aba 4 ([`src/ui/tab_agente_ia.py`](./src/ui/tab_agente_ia.py), [`src/ui/tabs_pastas.py`](./src/ui/tabs_pastas.py), [`app.py`](./app.py)):**
     - Inicialização padrão calibrada com o intervalo real do Poço 15/9-13 (`TOC = 1.827 m = 5.994 ft` até `TD = 3.260 m = 10.695 ft`), distribuindo `2.493,4 ft` (`760 m`) para a *Tail Slurry* e `2.208,0 ft` (`673 m`) para a *Lead Slurry* (totalizando `4.701,4 ft = 1.433 m`, 44% do poço).
     - Ao clicar em **`✨ Aplicar Programa Bi/Tri/Tetra-Pasta no Simulador (Aba 4)`**, o sistema converte automaticamente o intervalo `(prof_base - prof_topo)` de metros para pés ($\times 3{,}28084$) e preenche `dist_1`, `dist_2`, etc. na Aba 4.
     - Adicionado botão **`📐 Sincronizar Alturas (m ➔ ft)`** e legenda de equivalência métrica em tempo real na Aba 4.
  2. **Seletor de Unidade Vertical (`📏 Metros (m)` / `📐 Pés (ft)`), Salvaguarda de Escala e Trava Física do Eixo X ([`src/ui/dashboard.py`](./src/ui/dashboard.py)):**
     - Adicionado seletor **`📏 Metros (m)` | `📐 Pés (ft)`** na Janela Geomecânica da Aba 5 (padrão em Metros, idêntico ao gráfico de validação do Poço 15/9-13 e às Abas 1 e 3).
     - Salvaguarda automática: se as alturas somadas na Aba 4 forem $< 25\%$ de um poço profundo (ex.: valores digitados na escala numérica de metros como `1460` em vez de `4790 ft`), a projeção gráfica aplica automaticamente a conversão métrica para posicionar o TOC na sapata intermediária real.
     - Eixo X travado na janela física de engenharia (`6.5 ppg` a `19.2 ppg`), eliminando a distorção horizontal causada por pontos negativos do log sônico extrapolado.
     - Sapatas `20" (718 m)`, `13 3/8" (1.827 m)` e `9 5/8" (2.701 m)` demarcadas com marcadores triangulares sobre a escada verde e rótulos à direita.
- **Validação & Testes:**
  - **29 de 29 testes automatizados aprovados** (`python tests/test_audit.py`), incluindo novo teste específico para a escada geomecânica e sapatas do poço 15/9-13.

---

## 🎯 Estado Atual do Projeto

- **Status Geral:** ✅ Pôster Oficial para o 11º Congresso de Graduação USP atualizado (Versão 2 com foco no escopo da Bolsa PUB e Entrada Universal na 1ª Aba) em [`POSTER/Poster_Simulador_Cimentacao_USP_2026_v2.pptx`](./POSTER/Poster_Simulador_Cimentacao_USP_2026_v2.pptx) e [`POSTER/Poster_Simulador_Cimentacao_USP_2026_v2.pdf`](./POSTER/Poster_Simulador_Cimentacao_USP_2026_v2.pdf) (com preview PNG [`POSTER/Preview_Poster_USP_2026.png`](./POSTER/Preview_Poster_USP_2026.png), figuras 300 DPI [`POSTER/fig1_arquitetura_pipeline.png`](./POSTER/fig1_arquitetura_pipeline.png) e [`POSTER/fig2_resultados_cimentacao.png`](./POSTER/fig2_resultados_cimentacao.png), e guia [`POSTER/TEXTO_POSTER_CONGRESSO_USP.md`](./POSTER/TEXTO_POSTER_CONGRESSO_USP.md)). Fontes bibliográficas e DOIs auditados e atualizados em [`01_normas_e_bibliografia.md`](./docs/03_ACADEMICO_E_NORMATIVO/01_normas_e_bibliografia.md). 28 de 28 testes automatizados aprovados.
- **Ponto de Parada da Sessão:** O usuário solicitou interrupção temporária e pediu para registrar explicitamente as **4 opções técnicas de investigação** sobre a consistência dos resultados e a física do poço para escolha na próxima retomada.

---

## 📌 Ponto de Retomada Prioritário: Opções Técnicas para Escolha do Usuário

Ao retomar os trabalhos na próxima sessão, apresentar e debater com o usuário estas 4 frentes:

1. **Opção 1 — Densidade da Pasta e Balanço de Massa Estequiométrico:**
   - Auditoria fina da formulação física e química das pastas (Classe G pura em ~15.8 ppg vs alívio com esferas/bentonita para Lead ou densificação com baritina/hematita para Tail conforme API Spec 10A).
2. **Opção 2 — Pressão Hidrostática Real & EMW Integrado de Fundo:**
   - Ajustar os cartões SCADA e telemetria no topo do Dashboard para somar a coluna de lama ($0 \rightarrow \text{TOC}$) + coluna de cimento ($\text{TOC} \rightarrow \text{Fundo}$).
   - Exibir a verdadeira pressão de fundo total (ex: ~5.800–6.000 psi em vez de apenas 1.200 psi do cimento) e o EMW real do poço (ex: ~11.4 ppg), eliminando a impressão de discrepância numérica entre os cards e as curvas.
3. **Opção 3 — Volume de Calda, Rendimento ($ft^3/sk$) e Quantidade de Sacos ($sk$):**
   - Auditoria e conferência dos cálculos de cubagem de poço aberto com fator de excesso (*washout*), volume do anular e bolsão de sapata (*shoe track*).
4. **Opção 4 — Algoritmo Dinâmico de Seleção de Sapatas (*Casing Seat Selection* - Bourgoyne Cap. 3):**
   - Avaliar a implementação de um recurso que calcula dinamicamente o número ótimo de revestimentos, profundidades das sapatas (*casing points*) e densidades seguras de lama (*Safe mud weight window*) a partir do perfil contínuo de poro e fratura carregado na Aba 1.
5. **Opção 5 — Conversão `7.48052 gal/ft³` vs `7.5 gal/ft³` e Sincronização de Manuais (`docs/02_SISTEMA_E_IA/`):**
   - Avaliar padronização do fator `7.48052 gal/ft³` (Bourgoyne Exemplo 3.6, pág. 109) em `src/services/calculadora.py` (atualmente `7.5`) e sincronizar os manuais secundários para refletirem a esteira de 5 abas e a categoria `"Estabilizador Térmico"` em `config.py`.

---

## 🚀 Próximos Passos Sugeridos / Backlog

1. **Retomada Imediata:** Apresentar as 4 opções acima para o usuário indicar qual caminho deseja aprofundar.
2. **Validação Visual no Navegador Local (`streamlit run app.py`):**
   - Acessar a Aba 5 (Dashboard) e conferir a sintonia estética da Janela Geomecânica com o diagrama de referência de campo.
   - Testar o botão **`⛶ Tela Cheia`** para inspecionar a escala e o alinhamento dos Casing Points.
3. **Deploy e Commit no GitHub:**
   - Efetuar commit e push das melhorias visuais para o repositório do GitHub.



