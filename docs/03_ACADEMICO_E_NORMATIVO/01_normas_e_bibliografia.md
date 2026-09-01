# 📕 Nível 3: Normas Técnicas, Literatura Canônica e Rastreabilidade

> **Objetivo deste documento:** Fornecer o respaldo acadêmico, científico e normativo formal de Engenharia de Petróleo para bancas avaliadoras, orientadores e relatórios técnicos.

---

## 1. Referências Bibliográficas Canônicas (Normas & Livros)

1. **BOURGOYNE JR., A. T.; CHENEVERT, M. E.; MILLHEIM, K. K.; YOUNG JR., F. S.**  
   *Applied Drilling Engineering*. Society of Petroleum Engineers (SPE) Textbook Series, Vol. 2, Richardson, TX, EUA, 1986.  
   *(Especialmente o **Capítulo 3: Cementing**, Págs. 85–130 — Base dos cálculos volumétricos e tabela de aditivos).*

2. **NELSON, E. B.; GUILLOT, D.**  
   *Well Cementing*. 2ª Edição, Schlumberger, Sugar Land, TX, EUA, 2006.  
   *(Referência mundial em físico-química de pastas de cimento, cinética de hidratação e degradação térmica em HPHT).*

3. **AMERICAN PETROLEUM INSTITUTE (API).**  
   *API Specification 10A (API Spec 10A) / ISO 10426-1: Specification for Cements and Materials for Well Cementing*. 25ª Edição, Washington, D.C., EUA.  
   *(Padronização de classes Portland de A até H, teores de água e composições químicas).*

4. **AMERICAN PETROLEUM INSTITUTE (API).**  
   *API Recommended Practice 10B-2 (API RP 10B-2): Recommended Practice for Testing Well Cements*. 2ª Edição, Washington, D.C., EUA.  
   *(Ensaios laboratoriais padronizados: tempo de espessamento, perda de filtrado API e resistência à compressão UCA).*

5. **ROCHA, L. A. S.; AZUAGA, D.; SANTOS, O. L. A.; VIEIRA, C. R.**  
   *Projetos de Poços de Petróleo: Geopressões e Assentamento de Colunas*. 2ª Edição, Editora Interciência / Petrobras, Rio de Janeiro, 2011.  
   *(Definição de janelas operacionais de pressão, gradientes de poro e fratura).*

6. **HALLIBURTON ENERGY SERVICES.**  
   *Cementing Technical Handbook & e-RedBook Tables*. Duncan, OK, EUA.  
   *(Especificações de aditivos comerciais das séries HR, HALAD e CFR).*

---

## 2. Mapeamento de Rastreabilidade no Código-Fonte

Abaixo está o mapeamento exato entre as constantes/equações normativas e sua implementação nos arquivos do simulador:

| Parâmetro / Equação | Valor / Expressão | Norma / Literatura | Arquivo de Implementação |
| :--- | :---: | :--- | :--- |
| **Massa Padrão do Saco de Cimento ($M_{sk}$)** | **$94{,}0\text{ lb}$** ($42{,}64\text{ kg}$) | API Spec 10A, Seção 4 | [`config.py`](../../config.py) |
| **Densidade da Água Doce ($\rho_{água}$)** | **$8{,}33\text{ lb/gal}$** | Bourgoyne et al., Tab. 3.1 | [`config.py`](../../config.py) |
| **Gravidade Específica do Cimento ($SG_{cim}$)** | **$3{,}14$** | API Spec 10A / Bourgoyne | [`config.py`](../../config.py) |
| **Água de Mistura Classe G ($V_{água}$)** | **$5{,}00\text{ gal/sk}$** ($44\%\text{ w/c}$) | API Spec 10A | [`config.py`](../../config.py) |
| **Água de Mistura Classe H ($V_{água}$)** | **$4{,}30\text{ gal/sk}$** ($38\%\text{ w/c}$) | API Spec 10A | [`config.py`](../../config.py) |
| **Volume Absoluto do Cimento ($V_{sk}$)** | **$3{,}595\text{ gal/sk}$** | Bourgoyne Eq. 3.2 | [`src/services/calculadora.py`](../../src/services/calculadora.py) |
| **Regra dos 35% de Flor de Sílica (SSA-1)** | **$35{,}0\%\text{ BWOC}$** ($BHST > 110\ ^\circ\text{C}$) | Nelson & Guillot (2006) | [`src/services/requisitos_ia.py`](../../src/services/requisitos_ia.py) |
| **Seleção de Retardadores Térmicos** | HR-4 ($50-75\ ^\circ\text{C}$), HR-12 ($>75\ ^\circ\text{C}$) | Halliburton RedBook | [`src/services/groq_agent_service.py`](../../src/services/groq_agent_service.py) |
| **Pressão Hidrostática ($P_{hid}$)** | $P = 0{,}052 \cdot \sum (\rho_i \cdot h_i)$ | Bourgoyne Eq. 3.15 | [`src/services/calculadora.py`](../../src/services/calculadora.py) |

---

## 3. Catálogo Homologado de 26 Aditivos

Todos os aditivos pré-carregados no banco de dados persistente [`data/aditivos_db.json`](../../data/aditivos_db.json) possuem densidades relativas ($SG$) e dosagens rigorosamente extraídas da **Tabela 3.8 do Bourgoyne et al. (Págs. 102–104)**:

- **Densificantes:** Barita ($SG = 4{,}23$), Hematita ($SG = 5{,}02$).
- **Extensores:** Bentonita ($SG = 2{,}65$), Gilsonita ($SG = 1{,}07$), Diatomita ($SG = 2{,}10$), Pozolanas ($SG = 2{,}46 - 2{,}50$), Perlita ($SG = 2{,}20$).
- **Aceleradores:** Cloreto de Cálcio flocos/salmoura ($SG = 1{,}96 / 1{,}03$), Cloreto de Sódio ($SG = 2{,}17$), Gesso ($SG = 2{,}70$), Cal ($SG = 2{,}20$).
- **Retardadores:** HR-4 ($SG = 1{,}56$), HR-7 ($SG = 1{,}30$), HR-12 ($SG = 1{,}22$).
- **Dispersantes:** CFR-1 ($SG = 1{,}63$), CFR-2 ($SG = 1{,}30$).
- **Controladores de Filtrado:** HALDAD-9 ($SG = 1{,}22$), HALDAD-14 ($SG = 1{,}31$), Diacel LWL ($SG = 1{,}36$).
- **LCM e Especiais:** Flor de Sílica SSA-1 ($SG = 2{,}63$), Areia de Sílica ($SG = 2{,}63$), Tuf-Plug ($SG = 1{,}28$), Carvão Ativado ($SG = 1{,}57$).
