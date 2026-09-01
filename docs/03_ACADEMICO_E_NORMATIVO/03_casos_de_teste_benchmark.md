# 📕 Nível 3: Casos Canônicos de Teste & Benchmarks de Validação

> **Objetivo deste documento:** Apresentar os cenários de teste canônicos e o caso de referência acadêmico utilizados para auditar e validar matematicamente as formulações do simulador, o balanço de massas rigoroso e a acurácia dos modelos de Inteligência Artificial.

---

## 1. Cenário 1: Poço Quente e Permeável (V-01)

- **Condições Operacionais:**
  - Profundidade: $2.400\text{ m}$
  - $BHCT$: $75\ ^\circ\text{C}$ | $BHST$: $95\ ^\circ\text{C}$
  - Formação de alta permeabilidade (risco de desidratação da pasta)
  - Densidade Alvo: $15{,}8\text{ ppg}$
- **Gabarito Obrigatório de Engenharia:**
  - ✅ **Classe do Cimento:** Classe G
  - ✅ **Retardador:** `Retardador HR-4` ou `HR-12` ($0{,}20\%$ a $0{,}50\%\text{ BWOC}$)
  - ✅ **Controlador de Filtrado:** `HALDAD-9` ou `HALDAD-14` ($0{,}30\%$ a $0{,}60\%\text{ BWOC}$)
- **Status com Guardrails:** <mark>Aprovado (100%)</mark>

---

## 2. Cenário 2: Poço Profundo HPHT com Degradação Térmica (V-02)

- **Condições Operacionais:**
  - Profundidade: $4.200\text{ m}$
  - $BHCT$: $85\ ^\circ\text{C}$ | $BHST$: $125\ ^\circ\text{C}$ (Temperatura Estática Crítica $> 110\ ^\circ\text{C}$)
  - Janela de Densidade: $16{,}2$ a $16{,}8\text{ ppg}$
- **Gabarito Obrigatório de Engenharia:**
  - ✅ **Estabilizador Térmico Mandatório:** `Flor de Sílica (SSA-1)` rigorosamente em **$35{,}0\%\text{ BWOC}$** (Nelson & Guillot, 2006).
  - ✅ **Retardador de Alta Performance:** `Retardador HR-12` ($0{,}40\%$ a $0{,}80\%\text{ BWOC}$).
  - ✅ **Densificante:** `Barita` para atingir a densidade na janela.
- **Status com Guardrails:** <mark>Aprovado (100%)</mark>

---

## 3. Cenário 3: Seção Rasa / Baixa Temperatura (V-03)

- **Condições Operacionais:**
  - Profundidade: $450\text{ m}$ (Sapata de Condutor/Superfície)
  - $BHCT$: $18\ ^\circ\text{C}$ | $BHST$: $30\ ^\circ\text{C}$
  - Densidade Alvo Baixa: $12{,}8\text{ ppg}$ (formação frágil não consolidada)
- **Gabarito Obrigatório de Engenharia:**
  - ✅ **Extensor Leve:** `Bentonita (Gel)` ($2{,}0\%$ a $3{,}5\%\text{ BWOC}$).
  - ✅ **Acelerador de Pega:** `Cloreto de Cálcio (Flocos)` ($1{,}5\%$ a $2{,}0\%\text{ BWOC}$) para ganho rápido de resistência compressive (WOC).
- **Status com Guardrails:** <mark>Aprovado (100%)</mark>

---

## 4. Cenário 4: Janela Estreita com Alta Densidade & Reologia Crítica (V-04)

- **Condições Operacionais:**
  - Profundidade: $3.100\text{ m}$
  - Janela operacional estreita entre poro e fratura ($16{,}4$ a $16{,}8\text{ ppg}$)
  - Risco de alta perda de carga anular e fraturamento induzido
- **Gabarito Obrigatório de Engenharia:**
  - ✅ **Densificante Principal:** `Barita` ($15\%$ a $30\%\text{ BWOC}$).
  - ✅ **Dispersante / Redutor de Atrito:** `Dispersante CFR-2` ($0{,}30\%$ a $0{,}45\%\text{ BWOC}$).
  - ✅ **Retardador Moderado:** `Retardador HR-4` ou `HR-7`.
- **Status com Guardrails:** <mark>Aprovado (100%)</mark>

---

## 5. Cenário 5: Caso Canônico Acadêmico Bi-Pasta (Profa. Nara Policarpo / Bourgoyne et al.) (V-05)

- **Condições e Geometria do Poço:**
  - Profundidade Total de Cimentação: $2.500\text{ ft}$
  - Diâmetro da Broca: $D_{poço} = 17{,}000\text{ in}$
  - Revestimento: $OD = 13{,}375\text{ in}$ | $ID = 12{,}415\text{ in}$
  - Fator de Excesso Anular: $1{,}75$ ($75\%$ de excesso)
  - Distância Colar Flutuador até Sapata: $40\text{ ft}$
- **Especificação das Pastas:**
  - **Pasta 1 (Tail Slurry / Fundo):**
    - Altura: $500\text{ ft}$
    - Cimento Classe A + $2{,}0\%\text{ CaCl}_2$ + água de $5{,}20\text{ gal/sk}$
    - Resultado: Densidade $\approx 15{,}62\text{ ppg}$, Rendimento $= 1{,}173\text{ ft}^3/\text{sk}$
  - **Pasta 2 (Lead Slurry / Topo):**
    - Altura: $2.000\text{ ft}$
    - Cimento Classe A + $16{,}0\%\text{ Bentonita}$ + $5{,}0\%\text{ NaCl}$ + água de $13{,}00\text{ gal/sk}$
    - Resultado: Densidade $\approx 12{,}60\text{ ppg}$, Rendimento $= 2{,}240\text{ ft}^3/\text{sk}$
- **Validação no Simulador:** <mark>Aprovado com 100% de Aderência Analítica</mark>

---

## 6. Tabela Comparativa de Benchmark

| Modelo / Abordagem | V-01 (Quente) | V-02 (HPHT Sílica) | V-03 (Frio) | V-04 (Reologia) | V-05 (Bi-Pasta) | Aderência Global |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LLM Puro (Sem Guardrails)** | ❌ Falha (sem retard.) | ❌ Falha (sílica 0.32%) | ✅ Aprovado | ❌ Falha (sem disp.) | ❌ Falha (monopasta) | **40,0%** |
| **Simulador com Guardrails & Bi-Pasta** | ✅ Aprovado | ✅ Aprovado (35%) | ✅ Aprovado | ✅ Aprovado | ✅ Aprovado | **100,0%** |
