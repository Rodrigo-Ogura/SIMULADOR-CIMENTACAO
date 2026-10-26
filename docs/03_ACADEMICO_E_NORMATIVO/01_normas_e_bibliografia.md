# 📕 Nível 3: Normas Técnicas, Literatura Canônica e Rastreabilidade

> **Objetivo deste documento:** Fornecer o respaldo acadêmico, científico e normativo formal de Engenharia de Petróleo para bancas avaliadoras, orientadores e relatórios técnicos.

---

## 1. Referências Bibliográficas Canônicas (Normas, Livros & Bases Públicas)

### A. Cimentação de Poços & Normas Internacionais
1. **BOURGOYNE JR., A. T.; MILLHEIM, K. K.; CHENEVERT, M. E.; YOUNG JR., F. S.**  
   *Applied Drilling Engineering*. Society of Petroleum Engineers (SPE) Textbook Series, Vol. 2, Richardson, TX, EUA, 1986. ISBN: 978-1-55563-001-0.  
   *(Especialmente o **Chapter 3: Cements**, **Págs. 85–112** — Base dos cálculos volumétricos, Tabela 3.6 de teor de água na pág. 92, Tabela 3.8 de gravidades específicas na pág. 93, Tabela 3.9 de água de aditivos na pág. 94 e Exemplo 3.6 na pág. 109).*  
   - 📄 **Anexo Local Auditável:** [`docs/anexos/Bourgoyne_Cap3_Cementing.pdf`](../anexos/Bourgoyne_Cap3_Cementing.pdf)  
   - 🔗 **Link Oficial / DOI (SPE OnePetro):** [https://doi.org/10.2118/9781555630010](https://doi.org/10.2118/9781555630010)

2. **NELSON, E. B.; GUILLOT, D.**  
   *Well Cementing*. 2ª Edição, Schlumberger, Sugar Land, TX, EUA, 2006. ISBN: 978-0-9788530-0-6.  
   *(Referência mundial em físico-química de pastas de cimento, cinética de hidratação, eficiência de deslocamento no Cap. 10 e prevenção de regressão de resistência térmica com 35% BWOC de sílica em $BHST > 110\ ^\circ\text{C}$).*

3. **AMERICAN PETROLEUM INSTITUTE (API).**  
   *API Specification 10A (API Spec 10A) / ISO 10426-1: Specification for Cements and Materials for Well Cementing*. 25ª Edição, Washington, D.C., EUA, 2019.  
   *(Padronização de classes Portland de A até H, massa padrão de $94\text{ lb/sk}$, teores de água e requisitos físico-químicos).*  
   - 🔗 **Portal Oficial API:** [https://www.api.org](https://www.api.org)

4. **AMERICAN PETROLEUM INSTITUTE (API).**  
   *API Recommended Practice 10B-2 (API RP 10B-2) / ISO 10426-2: Recommended Practice for Testing Well Cements*. 2ª Edição, Washington, D.C., EUA, 2013.  
   *(Ensaios laboratoriais padronizados: consistometria de tempo de espessamento em Unidades Bearden $B_c$, perda de filtrado API em $30\text{ min}$ a $1.000\text{ psi}$, água livre e resistência à compressão).*

5. **HALLIBURTON ENERGY SERVICES.**  
   *Cementing Tables & Technical Handbook (e-RedBook)*. Duncan, OK, EUA.  
   *(Especificações técnicas dos aditivos das séries HR-4/7/12, HALAD-9/14, CFR-1/2 e SSA-1 citados nas Tabelas 3.8 e 3.9 de Bourgoyne et al.).*

---

### B. Geomecânica, Janelas Operacionais & Bases de Dados Reais (Aba 1)
6. **ROCHA, L. A. S.; AZEVEDO, C. T.**  
   *Projetos de Poços de Petróleo: Geopressões e Assentamento de Colunas*. 2ª/3ª Edição, Editora Interciência / Petrobras, Rio de Janeiro, 2009 / 2019. ISBN: 978-85-7193-214-2.  
   *(Bibliografia base da proposta de Iniciação Científica na Poli-USP para definição de janelas operacionais de pressão, gradientes de sobrecarga, poro, colapso e fratura).*  
   - 📄 **Proposta Original de IC Anexada:** [`docs/anexos/Proposta_IC_Poli_USP.pdf`](../anexos/Proposta_IC_Poli_USP.pdf)

7. **AADNOY, B. S.; COOPER, I.; MISKA, S. Z.; MITCHELL, R. F.; PAYNE, M. L.**  
   *Advanced Drilling and Well Technology*. Society of Petroleum Engineers (SPE), Richardson, TX, EUA, 2009. ISBN: 978-1-55563-145-1.  
   - 🔗 **Link Oficial / DOI (SPE OnePetro):** [https://doi.org/10.2118/9781555631451](https://doi.org/10.2118/9781555631451)

8. **GARDNER, G. H. F.; GARDNER, L. W.; GREGORY, A. R.**  
   *Formation Velocity and Density — The Diagnostic Basics for Stratigraphic Traps*. Geophysics, Vol. 39, No. 6, pp. 770–780, 1974.  
   *(Correlação empírica $\rho = a \cdot V_p^b$ utilizada no cálculo do gradiente de sobrecarga a partir do perfil sônico $\Delta t$).*  
   - 🔗 **Link Oficial / DOI:** [https://doi.org/10.1190/1.1440465](https://doi.org/10.1190/1.1440465)

9. **EATON, B. A.**  
   *The Equation for Geopressure Prediction from Well Logs*. Society of Petroleum Engineers, SPE-5544-MS, Fall Meeting of SPE-AIME, Dallas, TX, 1975.  
   *(Equação clássica $G_p = G_{ob} - (G_{ob} - G_n)(\Delta t_n / \Delta t)^x$ utilizada no motor geomecânico dos poços do Mar do Norte).*  
   - 🔗 **Link Oficial / DOI (SPE OnePetro):** [https://doi.org/10.2118/5544-MS](https://doi.org/10.2118/5544-MS)

10. **NORWEGIAN OFFSHORE DIRECTORATE (SODIR / antigo NPD) & FORCE 2020 DATASET.**  
    *FactPages Wellbore Data (Block 15/9: Wells 15/9-13, 15/9-14, 15/9-15, 15/9-17, 15/9-23)* & *FORCE 2020 Well Log Dataset (Bormann et al., 2020)*.  
    *(Fontes públicas auditáveis dos perfis sônicos $\Delta t$, raios gama $GR$, densidades de lama históricas e testes de absorção LOT da plataforma continental norueguesa).*  
    - 🔗 **Sodir FactPages (Poços do Bloco 15/9):** [https://factpages.sodir.no/en/wellbore/PageView/With/Wdss/45](https://factpages.sodir.no/en/wellbore/PageView/With/Wdss/45)  
    - 🔗 **Dataset Zenodo / FORCE 2020 (DOI `10.5281/zenodo.4351156`):** [https://zenodo.org/records/4351156](https://zenodo.org/records/4351156)

---

## 2. Mapeamento de Rastreabilidade no Código-Fonte

Abaixo está o mapeamento exato entre as constantes/equações normativas, a localização precisa no PDF anexado ([`Bourgoyne_Cap3_Cementing.pdf`](../anexos/Bourgoyne_Cap3_Cementing.pdf)) e sua implementação nos módulos do simulador:

| Parâmetro / Equação | Valor / Expressão | Localização Exata na Norma / Literatura | Arquivo de Implementação |
| :--- | :---: | :--- | :--- |
| **Massa Padrão do Saco de Cimento ($M_{sk}$)** | **$94{,}0\text{ lb}$** ($42{,}64\text{ kg}$) | API Spec 10A / Bourgoyne Seção 3.1 (pág. 85) e Tab. 3.8 (pág. 93) | [`config.py`](../../config.py) |
| **Densidade da Água Doce ($\rho_{água}$)** | **$8{,}33\text{ lb/gal}$** ($62{,}4\text{ lb/ft}^3$) | Bourgoyne et al., Tab. 3.8 (pág. 93) e Exemplo 3.4 (pág. 92) | [`config.py`](../../config.py) |
| **Gravidade Específica do Cimento ($SG_{cim}$)** | **$3{,}14$** | API Spec 10A / Bourgoyne Tab. 3.8 (pág. 93) | [`config.py`](../../config.py) |
| **Água de Mistura por Classe (A–H)** | **$5{,}20\text{ gal/sk}$ (A/B), $6{,}30$ (C), $4{,}30$ (D/E/F/H), $5{,}00$ (G)** | API Spec 10A / Bourgoyne Tab. 3.6 (pág. 92) e Tab. 3.9 (pág. 94) | [`config.py`](../../config.py) |
| **Volume Absoluto do Cimento ($V_{sk}$)** | **$3{,}595\text{ gal/sk}$** ($94 / [3{,}14 \times 8{,}33]$) | Bourgoyne Seção 3.4, Exemplo 3.4 (pág. 92) e Exemplo 3.5 (pág. 98) | [`src/services/calculadora.py`](../../src/services/calculadora.py) |
| **Balanço Volumétrico Bi-Pasta (Caso Canônico)** | Anular $17\text{"} \times 13\ 3/8\text{"}$, Excesso $1{,}75$, Sapata $40\text{ ft}$ | Bourgoyne Seção 3.5.11, **Exemplo 3.6 (pág. 109)** | [`src/services/calculadora.py`](../../src/services/calculadora.py) |
| **Regra dos 35% de Flor de Sílica (SSA-1)** | **$35{,}0\%\text{ BWOC}$** ($BHST > 110\ ^\circ\text{C}$) | Bourgoyne Tab. 3.9 (pág. 94) & Nelson & Guillot (2006) | [`src/services/requisitos_ia.py`](../../src/services/requisitos_ia.py) |
| **Seleção de Retardadores Térmicos** | HR-4 ($50-75\ ^\circ\text{C}$), HR-12 ($>75\ ^\circ\text{C}$) | Bourgoyne Seção 3.4.16, Tab. 3.22 (pág. 100) / Halliburton | [`src/services/requisitos_ia.py`](../../src/services/requisitos_ia.py) |
| **Pressão Hidrostática ($P_{hid}$)** | $P = 0{,}052 \cdot \sum (\rho_i \cdot h_i)$ | Bourgoyne Cap. 1 & Cap. 2 (Eq. 2.2) / Rocha & Azevedo | [`src/services/calculadora.py`](../../src/services/calculadora.py) |
| **Sobrecarga, Poro, Fratura e Colapso** | Gardner (1974), Eaton (1975), LOT & Mohr-Coulomb | Sodir FactPages / FORCE 2020 / Rocha & Azevedo | [`src/services/geomecanica_service.py`](../../src/services/geomecanica_service.py) |

---

## 3. Catálogo Homologado de 26 Aditivos

Todos os aditivos pré-carregados no banco de dados persistente [`data/aditivos_db.json`](../../data/aditivos_db.json) possuem densidades relativas ($SG$) e exigências de água rigorosamente extraídas da **Tabela 3.8 (*Physical Properties of Cementing Materials*, pág. 93)** e da **Tabela 3.9 (*Water Requirements*, pág. 94)** do capítulo anexado de **Bourgoyne et al. (1986)**:

- **Densificantes:** Barita ($SG = 4{,}23$), Hematita ($SG = 5{,}02$).
- **Extensores:** Bentonita ($SG = 2{,}65$), Gilsonita ($SG = 1{,}07$), Diatomita Diacel D ($SG = 2{,}10$), Pozolanas Pozmix A/D ($SG = 2{,}46 - 2{,}50$), Perlita Regular ($SG = 2{,}20$).
- **Aceleradores:** Cloreto de Cálcio em flocos/salmoura ($SG = 1{,}96 / 1{,}0329$, conforme Exemplo 3.6 na pág. 109), Cloreto de Sódio seco/salmoura ($SG = 2{,}17 / 1{,}0279$), Gesso Cal-Seal ($SG = 2{,}70$), Cal Hidratada ($SG = 2{,}20$).
- **Retardadores:** HR-4 ($SG = 1{,}56$), HR-7 ($SG = 1{,}30$), HR-12 ($SG = 1{,}22$).
- **Dispersantes:** CFR-1 ($SG = 1{,}63$), CFR-2 ($SG = 1{,}30$).
- **Controladores de Filtrado:** HALDAD-9 ($SG = 1{,}22$), HALDAD-14 ($SG = 1{,}31$), Diacel LWL ($SG = 1{,}36$). *(Nota de Auditoria: A grafia `HALDAD-9` / `HALDAD-14` reproduz fielmente a impressão original da Tabela 3.8 de Bourgoyne et al. na pág. 93 para os polímeros comerciais HALAD®-9 e HALAD®-14).*
- **Estabilizadores Térmicos, LCM e Especiais:** Flor de Sílica SSA-1 ($SG = 2{,}63$), Areia de Sílica Ottawa ($SG = 2{,}63$), Tuf-Plug ($SG = 1{,}28$), Carvão Ativado ($SG = 1{,}57$).
