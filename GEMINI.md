# Regras e Diretrizes do Projeto - Simulador de Cimentação

Este projeto é um **Simulador Numérico e Especialista de Cimentação de Poços de Petróleo** desenvolvido em Python com interface Streamlit, com suporte a cálculos de balanço de massa, reologia, hidráulica de poço e recomendações de formulação com Inteligência Artificial Multi-Provedor (**Groq Cloud API** para nuvem de alta velocidade e **Ollama** para execução local offline).

---

## 📌 Regra de Continuidade e Registro (OBRIGATÓRIA)

1. **Início de Sessão:**
   - Ao iniciar qualquer nova conversa ou ao ser questionado sobre o estado do projeto, consulte imediatamente o arquivo [`HISTORICO_PROGRESSO.md`](./HISTORICO_PROGRESSO.md) para recuperar o contexto exato de onde o trabalho parou.

2. **Registro Contínuo de Alterações:**
   - Ao concluir qualquer alteração de código, correção de bugs, refatoração ou adição de novas funcionalidades, **atualize obrigatoriamente** o arquivo [`HISTORICO_PROGRESSO.md`](./HISTORICO_PROGRESSO.md).
   - Registre a data, descrição das mudanças, arquivos criados/modificados, testes realizados e o status atualizado dos próximos passos.

---

## 🛑 Protocolo de Encerramento / Comando "Logoff" (AUTOMÁTICO)

Sempre que o usuário digitar `logoff`, `/logoff`, `salvar sessão`, `fim de sessão` ou similar, o agente **DEVE executar automaticamente e de forma autônoma o seguinte protocolo de encerramento**:

1. **Auditoria e Atualização do [`HISTORICO_PROGRESSO.md`](./HISTORICO_PROGRESSO.md):**
   - Registrar a data/hora, resumo técnico das alterações feitas na sessão, lista de arquivos criados/modificados, testes realizados e o status atualizado dos próximos passos.
2. **Atualização da Documentação Técnica & Pedagógica ([`docs/`](./docs/) e [`README.md`](./README.md)):**
   - Sincronizar todos os manuais, arquiteturas e benchmarks afetados pelas mudanças da sessão.
3. **Validação & Teste de Compilação:**
   - Executar a verificação de compilação de todos os módulos Python (`python -m py_compile ...`) para garantir zero erros residuais.
4. **Relatório de Fechamento de Sessão:**
   - Emitir um resumo de encerramento informando que o projeto está 100% salvo, consistente e pronto para ser retomado a qualquer momento.

---

## 🤖 Arquitetura de Inteligência Artificial & Engenharia

1. **Provedores Suportados:**
   - **Groq Cloud API (`src/services/groq_agent_service.py`):** Modelos de ponta em nuvem de alta performance (ex: `qwen/qwen3.8-27b`, `openai/gpt-oss-120b`, `llama-3.3-70b`, `groq/compound`). Utiliza `GROQ_API_KEY` do `.env` ou informada na UI.
   - **Ollama Local (`src/services/ollama_agent_service.py`):** Execução local 100% offline via API REST (`http://localhost:11434`), padrão `llama3.1:latest`.

2. **Guardrails Determinísticos & Validação (`src/services/requisitos_ia.py`):**
   - Nenhuma recomendação de IA é aplicada sem passar pela validação determinística de engenharia.
   - Os requisitos críticos são derivados das condições do poço (BHST, BHCT, Poro, Fratura, Permeabilidade, Risco de Gás, LCM, Reologia Crítica).
   - O modelo opera sob **Catálogo Fechado de Aditivos** ([`data/aditivos_db.json`](./data/aditivos_db.json)). Aditivos fora do catálogo são rejeitados.
   - Se houver desconformidade técnica, o sistema executa um loop de autocorreção em 2 tentativas. Caso persista o erro, a formulação é bloqueada para aplicação.

---

## 📐 Diretrizes Técnicas e de Arquitetura de Código

1. **Modularidade Estrita em `src/`:**
   - `src/models/`: Dataclasses e modelos de domínio (`aditivo.py`, `pasta.py`).
   - `src/services/`: Motores de cálculo de balanço de massa, aditivos e serviços de IA (`calculadora.py`, `aditivo_service.py`, `groq_agent_service.py`, `ollama_agent_service.py`, `requisitos_ia.py`).
   - `src/ui/`: Componentes visuais modulares Streamlit (`dashboard.py`, `sidebar.py`, `tab_agente_ia.py`, `tab_parametros_poco.py`, `tabs_pastas.py`).
   - `src/utils/`: Funções utilitárias e logger (`logger.py`).
   - `config.py`: Variáveis de ambiente, constantes físicas API, configurações de IA e catálogo padrão de aditivos.
   - `data/`: Base de dados persistente em JSON (`aditivos_db.json`).

2. **Rigor Técnico e Normas da Indústria:**
   - Respeitar estritamente as normas **API Spec 10A / API RP 10B** e a literatura clássica (**Bourgoyne et al. - Cap. 3**, Nelson & Guillot).
   - Manter precisão nas conversões de unidades de campo de petróleo ($ppg$, $lb/sk$, $gal/sk$, $ft^3/sk$, $m^3$, $^{\circ}C$, $^{\circ}F$).

3. **Compatibilidade e Execução:**
   - Aplicação executada via `streamlit run app.py`.
   - Compatibilidade multiplataforma (Windows/Linux) e tolerância a falhas quando serviços externos ou bibliotecas opcionais (ex: `groq`) não estiverem disponíveis.
