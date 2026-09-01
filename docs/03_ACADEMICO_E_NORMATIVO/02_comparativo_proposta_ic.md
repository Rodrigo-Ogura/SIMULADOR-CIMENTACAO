# 📕 Nível 3: Comparativo com a Proposta de Iniciação Científica (Poli-USP)

> **Objetivo deste documento:** Demonstrar formalmente a evolução do projeto frente à proposta original de Iniciação Científica vinculada à Escola Politécnica da USP / PRH-ANP, comprovando o cumprimento integral do escopo e as inovações introduzidas com IA.

---

## 1. Contexto Acadêmico do Projeto

- **Instituição:** Escola Politécnica da Universidade de São Paulo (Poli-USP) — Departamento de Engenharia de Minas e de Petróleo.
- **Orientação:** Prof. Dr. Ronaldo Carrion.
- **Documento Original:** [`docs/anexos/Proposta_IC_Poli_USP.pdf`](../anexos/Proposta_IC_Poli_USP.pdf).

---

## 2. Matriz de Cumprimento de Metas

| Meta Proposta no Plano de Trabalho de IC | Status no Projeto | Implementação Entregue |
| :--- | :---: | :--- |
| **1. Cubagem e Geometria do Poço** | <mark>100% Concluído</mark> | Dimensionamento de volumes anulares com $D_{broca}$, $OD/ID$ de revestimento, fator de excesso (*washout*) e intervalo colar-sapata. |
| **2. Balanço de Massas Rigoroso** | <mark>100% Concluído</mark> | Método dos volumes absolutos para determinação de rendimento ($ft^3/sk$), água requerida ($gal/sk$), densidade ($ppg$) e sacos ($sk$). |
| **3. Classes de Cimento API Spec 10A** | <mark>100% Concluído</mark> | Suporte a todas as classes API (A a H) com água teórica e opção de customização. |
| **4. Banco de Aditivos Químicos** | <mark>100% Concluído</mark> | 26 aditivos cadastrados segundo Bourgoyne et al. com persistência JSON e categorização funcional. |
| **5. Pastas Múltiplas (*Lead* e *Tail*)** | <mark>100% Concluído</mark> | Configuração individual de até 4 pastas empilhadas no anular com cálculo hidrostático acumulado. |
| **6. Visualização Gráfica e Interface** | <mark>Superado (Inovação)</mark>| Interface visual interativa e reativa desenvolvida em Streamlit com gráficos dinâmicos Plotly e Ficha de Traço (*Batch Sheet*). |
| **7. Sistema Especialista / Assistência Inteligente** | <mark>Superado (Inovação)</mark>| Integração de Agente IA Multi-Provedor (**Groq Cloud + Ollama Local**) com **Guardrails Determinísticos** que garantem 100% de precisão sem alucinações. |

---

## 3. Principais Inovações além da Proposta Original

1. **Camada de Guardrails Determinísticos ([`src/services/requisitos_ia.py`](../../src/services/requisitos_ia.py)):**
   - Transforma o simulador em uma plataforma de pesquisa pioneira em *Deterministic LLM Guardrails* aplicados à engenharia de poços.
2. **Arquitetura Híbrida de IA:**
   - Permite executar modelos tanto em nuvem ultra-rápida (Groq LPU) quanto em computadores de campo 100% offline (Ollama).
3. **Ficha de Traço Operacional (*Batch Sheet*):**
   - Gera na hora a tabela de pesagem e mistura para os químicos e operadores na sonda de perfuração.
