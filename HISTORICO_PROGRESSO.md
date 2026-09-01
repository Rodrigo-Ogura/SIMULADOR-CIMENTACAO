# 📜 Histórico de Progresso do Projeto: Simulador de Cimentação

Documento de registro contínuo de evolução, alterações de código, testes e próximos passos.
> **Regra:** Este documento é consultado no início de cada sessão e atualizado a cada alteração relevante conforme definido em [`GEMINI.md`](./GEMINI.md).

---

## 🏗️ Visão Geral da Arquitetura do Projeto

- **Linguagem & Frameworks:** Python 3.10+, Streamlit, Plotly, NumPy, Pandas, Pydantic, Groq Cloud API, Ollama Local.
- **Design System:** Estilo industrial de alta fidelidade inspirado no **OpenLab Drilling (NORCE)** (Dark Slate Theme `#0b0f19`, Cartões Digitais SCADA de Telemetria via `st.html`, Esquemático 2D Didático, Janela de Pressão Geomecânica e Recomendador de Programa Completo Multi-Pasta).
- **Repositório & Deploy:** GitHub oficial ([github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO](https://github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO)) integrado com deploy automático no **Streamlit Community Cloud** com proteção de chave de API (`st.secrets` e `.gitignore`).
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

### [Sessão 7 e 8] - Modernização Visual OpenLab, Deploy Online e Guardrails de Lama (Sessão Atual)
- **Data/Hora de Encerramento:** 2026-09-01 16:05
- **O que foi realizado:**
  1. **Recomendação de Programa Completo Bi-Pasta (Lead + Tail Slurry):**
     - IA projeta de forma autônoma a pasta leve de topo (12.0 a 13.8 ppg) com extensores e a pasta pesada de fundo (15.6 a 16.5 ppg) com retardadores/sílica.
     - Botão mestre de aplicação em 1 clique para preencher a Pasta 1 e Pasta 2 na Aba 2.
  2. **Integração Total da Densidade da Lama de Perfuração ($\rho_{lama}$):**
     - Campo de densidade de lama adicionado à Aba 3 e sincronizado com a Aba 1 e Aba 4.
     - Guardrails determinísticos baseados em Bourgoyne et al. (Cap. 3) e Nelson & Guillot (Cap. 10) validando overbalance e hierarquia de deslocamento hidrostático: $\rho_{lama} < \rho_{lead} \le \rho_{tail}$.
  3. **Esquemático 2D Didático & Janela Operacional Dinâmica:**
     - Seletor dual (*Didático* com cotas verticais/sapata enfatizada vs *Escala Real*).
     - Auditoria ponto a ponto de toda a coluna com alerta de risco de fratura ou kick.
  4. **Deploy Online Seguro no Streamlit Cloud & GitHub:**
     - Criação de `.gitignore` para proteção absoluta de chaves locais (`.env`).
     - Suporte em `config.py` a `st.secrets` criptografados.
     - Configuração de autoria e envio oficial para [github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO](https://github.com/Rodrigo-Ogura/SIMULADOR-CIMENTACAO).
  5. **Atualização Completa do README.md:**
     - Seção dedicada de acesso online e deploy no Streamlit Cloud com diagrama de arquitetura.
     - Todos os módulos Python compilados com zero erros (`python -m py_compile`).

---

## 🎯 Estado Atual do Projeto

- **Status Geral:** ✅ Simulador de cimentação completo, online no GitHub e Streamlit Cloud, testado, consistente e pronto para ser retomado a qualquer momento.

---

## 🚀 Próximos Passos Sugeridos / Backlog

1. **Exportação de Relatórios de Engenharia (PDF/Excel):**
   - Gerar memorial de cálculo em PDF/Excel com o esquemático 2D, ficha de traço operacional e parecer da IA.
2. **Eficiência de Deslocamento e Centralização (Standoff):**
   - Modelar o perfil de centralização da coluna no poço e o cálculo analítico da taxa de remoção do fluido de perfuração.
