# 📙 Nível 2: Manual do Usuário do Simulador

> **Objetivo deste documento:** Servir como um guia prático e visual para operar todas as 4 abas e recursos do Simulador de Cimentação no Streamlit, com padrão visual **OpenLab Drilling (NORCE)**.

---

## 1. Como Iniciar a Aplicação

1. Abra o terminal na pasta do projeto:
   ```bash
   cd SIMULADOR
   ```
2. Execute o comando Streamlit:
   ```bash
   streamlit run app.py
   ```
3. O navegador abrirá automaticamente em `http://localhost:8501`.

---

## 2. Visão Geral das 4 Abas do Simulador

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🛢️ CEMENTING SIMULATOR & ENGINEERING SUITE (API SPEC 10A / 10B)       │
├───────────────────┬───────────────────┬────────────────┬───────────────┤
│ 📐 1. Geometria   │ 🧪 2. Pastas      │ 🧠 3. IA Suite │ 📊 4. Dashboard│
└───────────────────┴───────────────────┴────────────────┴───────────────┘
```

---

### 📐 Aba 1: Geometria do Poço & Gestão de Aditivos
- **Objetivo:** Definir as dimensões dos tubulares, folgas anulares, limites geomecânicos e gerenciar o catálogo de aditivos.
- **Campos de Entrada:**
  - **Diâmetro da Broca ($D_{broca}$ em pol):** Diâmetro nominal do poço aberto.
  - **Diâmetro Externo do Revestimento ($OD$ em pol):** Diâmetro da coluna de aço.
  - **Diâmetro Interno do Revestimento ($ID$ em pol):** Utilizado para o bolsão de cimento colar-sapata (*Shoe Track*).
  - **Fator de Excesso (*Washout*):** Margem volumétrica adicional para compensação de cavernas (ex: $1{,}75 = 75\%$ de excesso).
  - **Distância Colar-Sapata (ft):** Altura do bolsão de cimento remanescente no interior do revestimento.
  - **Densidade da Lama de Perfuração ($ppg$):** Fluido existente no poço antes do bombeio.
- **Painel de Folga Anular:** Telemetria da folga radial e diametral em tempo real.
- **Gestão de Aditivos:** Formulário para homologar novos aditivos e botão de restauração do catálogo oficial do Bourgoyne et al.

---

### 🧪 Aba 2: Configuração das Pastas de Cimento
- **Objetivo:** Parametrizar as características de cada seção de pasta no anular.
- **Passo a Passo:**
  1. Selecione a **Classe API do Cimento** (Classe A até H). A água de mistura padrão API é preenchida automaticamente (ex: $5{,}20\text{ gal/sk}$ para Classe A e $5{,}00\text{ gal/sk}$ para Classe G).
  2. Ajuste a **Altura da Coluna de Cimento no Anular (ft)** (ex: $500\text{ ft}$ para Pasta 1 e $2.000\text{ ft}$ para Pasta 2).
  3. *(Opcional)* Marque a caixa de água customizada para alterar o fator água-cimento.
  4. Selecione os aditivos na grade e informe as dosagens em **% BWOC** (ou use a Aba 3 para preenchimento automático por IA).

---

### 🧠 Aba 3: Módulo Especialista de Formulação IA
- **Objetivo:** Obter recomendações automáticas de aditivos formuladas por Large Language Models e auditadas por **Guardrails Determinísticos**.
- **Estratégias de Cimentação:**
  - **🎯 Programa Completo (Lead + Tail Slurry):** Dimensiona simultaneamente a **Pasta 2 (Lead)** com baixa densidade ($12{,}0\text{ a }13{,}8\text{ ppg}$) para não fraturar o topo da formação e a **Pasta 1 (Tail)** com alta densidade ($15{,}6\text{ a }16{,}5\text{ ppg}$) e alta resistência para selar a sapata.
  - **🧪 Pasta Individual:** Dimensionamento focado exclusivamente na Tail Slurry ou Lead Slurry.
- **Provedores Suportados:**
  - **☁️ Groq Cloud (LPU Nuvem):** Inferência em milissegundos com modelos de ponta (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, `llama-3.3-70b`).
  - **🖥️ Ollama Local (Offline):** Execução 100% local e confidencial via `llama3.1`.
- **Aplicação Mestre com 1 Clique:** O botão *✨ Aplicar Programa Completo no Simulador* transfere automaticamente as classes, águas e aditivos recomendados para a Pasta 1 e Pasta 2 na Aba 2.

---

### 📊 Aba 4: Telemetria, Dashboard & Ficha de Traço
- **Objetivo:** Monitoramento operacional estilo sala de controle OpenLab.
- **Componentes:**
  1. **Cartões Digitais SCADA de Telemetria:**
     - *Pressão Hidrostática no Fundo ($psi$)* com gradiente médio ($psi/ft$).
     - *Densidade Equivalente da Coluna ($EMW$ em $ppg$)* e Gravidade Específica ($SG$).
     - *Volume Total da Calda ($bbl$ e $ft^3$)*.
     - *Total de Sacos de Cimento (94 lb/sk)* e massa total em toneladas métricas.
  2. **Esquemático 2D do Poço (Seletor Dual):**
     - **📘 Modo Didático (Visão Clara):** Inspirado nos diagramas acadêmicos, com anular alargado, sapata (*Shoe Track*) com espessura visual destacada, cotas dimensionais verticais com setas laterais e anotações na base ($DI, DE, D_{poço}$).
     - **📏 Modo Escala Real (in):** Proporções físicas estritas em polegadas.
  3. **Janela de Pressão Operacional Geomecânica ($TVD \times EMW$):**
     - Gráfico dinâmico com limites de **Poro (Amarelo)**, **Fratura (Vermelho)**, **Lama (Cinza)** e **EMW do Cimento (Azul)**.
     - **Auditoria Ponto a Ponto de Fratura/Kick:** Alerta automático com o intervalo exato de profundidade caso a densidade do cimento ultrapasse a fratura no topo ou fique abaixo do poro.
  4. **Ficha de Traço Operacional (*Batch Sheet*):**
     - Tabela de pesagem e mistura para sonda com dosagens por saco e totais no poço.
     - Gráficos de barras por componente (massa por saco, volume ou massa total).

---

➡️ **Próximo passo:** Para consultar os casos de teste e benchmarks de validação, consulte o documento [**03. Casos de Teste e Benchmark**](../03_ACADEMICO_E_NORMATIVO/03_casos_de_teste_benchmark.md).
