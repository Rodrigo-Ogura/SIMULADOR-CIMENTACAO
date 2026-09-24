# 📐 Subprojeto: Módulo de Janela Operacional de Poço (Geomecânica)

Área dedicada ao estudo, engenharia reversa e validação do módulo desenvolvido por outro aluno do projeto para cálculo e importação de **Janelas Operacionais** (Pressão de Poro, Colapso/Breakout e Fratura).

---

## 📥 Arquivos Esperados Nesta Pasta

Por favor, adicione nesta pasta:
1. **Caderno Jupyter (`.ipynb`):** Código fonte original com as rotinas de cálculo geomecânico e plotagem de curvas.
2. **Arquivos de Dados de Entrada (`.csv`):** Perfis de poço, dados de sobrecarga, tensões in-situ, litologias ou registros de poço utilizados pelo código.
3. **Arquivos de Resultados / Gabaritos (`.csv`):** Dados de saída gerados pelo autor original para validação cruzada.

---

## 🔬 Plano de Trabalho Interno na Sandbox

1. **Inspeção do Notebook:** Análise das fórmulas físicas, unidades ($ppg$, $psi/ft$, $g/cm^3$, $m$, $ft$) e bibliotecas necessárias.
2. **Script Benchmark:** Conversão do notebook para script Python puro e execução contra os dados CSV.
3. **Validação Numérica:** Confronto dos resultados gerados com o gabarito.
4. **Proposta de Integração:** Desenho do serviço final para ser migrado para `src/services/geomecanica_service.py` e interface no `app.py`.
