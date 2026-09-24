# 🧪 Sandbox & Laboratório de Incubação de Módulos

Esta pasta atua como uma **área de isolamento (*staging / sandbox*)** para recepção, auditoria, engenharia reversa e validação numérica de módulos externos desenvolvidos por outros pesquisadores e alunos do projeto antes de serem integrados oficialmente ao núcleo do simulador (`src/`).

---

## 🎯 Por que usamos este padrão?

1. **Blindagem do Núcleo Principal:** O simulador oficial (online no Streamlit Cloud) permanece 100% estável e funcional enquanto novos recursos são dissecados.
2. **Engenharia Reversa Sem Ruído:** Módulos em Jupyter Notebooks (`.ipynb`) ou protótipos experimentais podem ser analisados, limpos e refatorados sem poluir a arquitetura do projeto.
3. **Validação Numérica Rígida (Benchmark):** Todo novo cálculo é comparado com os gabaritos numéricos (CSVs) para assegurar conformidade com as normas API Spec 10A/10B e a literatura clássica.

---

## 📂 Subprojetos em Andamento

| Subpasta | Descrição do Módulo | Status |
| :--- | :--- | :--- |
| [`janela_operacional/`](./janela_operacional/) | Cálculo e importação de janelas operacionais reais (Poro, Colapso e Fratura) | 🟡 Em Preparação |
