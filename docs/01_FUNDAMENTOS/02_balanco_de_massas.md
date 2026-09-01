# 📘 Nível 1: Balanço de Massas e Matemática da Cimentação

> **Objetivo deste documento:** Explicar passo a passo a física e a matemática por trás da formulação de pastas de cimento, demonstrando o método dos volumes absolutos, cálculo de rendimento, número de sacos e pressão hidrostática.

---

## 1. O Princípio dos Volumes Absolutos

Na engenharia de cimentação de poços de petróleo, não misturamos os ingredientes por "volume aparente" (como copos medidores), porque os pós possuem ar entre suas partículas.

Utilizamos o **Método dos Volumes Absolutos**: cada componente (cimento em pó, água, aditivos químicos e sais) contribui para o volume final líquido exatamente de acordo com sua massa e sua densidade real (**Gravidade Específica - $SG$**):

$$\text{Volume Absoluto (gal)} = \frac{\text{Massa (lb)}}{\text{Gravidade Específica } (SG) \times 8{,}33\text{ lb/gal}}$$

> Onde $8{,}33\text{ lb/gal}$ é a densidade da água doce pura à temperatura ambiente.

---

## 2. A Unidade Básica da Indústria: O Saco de Cimento ($sk$)

Historicamente padronizado pelo **American Petroleum Institute (API)**:
- **1 Saco de Cimento ($1\text{ sk}$):** Pesa exatamente **$94{,}0\text{ lb}$** ($\approx 42{,}64\text{ kg}$).
- **Gravidade Específica do Cimento Portland ($SG_{cimento}$):** **$3{,}14$** (adimensional).

Portanto, o volume ocupado por $1\text{ saco}$ de cimento seco puro é:

$$V_{cimento} = \frac{94{,}0\text{ lb}}{3{,}14 \times 8{,}33\text{ lb/gal}} = \mathbf{3{,}595\text{ galões por saco}}$$

---

## 3. Água de Mistura Requerida (API Spec 10A)

Cada classe de cimento API exige uma quantidade padronizada de água de mistura para que a reação química de hidratação ocorra de forma completa e estável:

| Classe API | Aplicação Típica | Água Recomendada ($gal/sk$) | Relação Água/Cimento ($w/c$) |
| :---: | :--- | :---: | :---: |
| **Classe A e B** | Poços rasos e amenos ($0 - 1.830\text{ m}$) | **$5{,}20\text{ gal/sk}$** | $46{,}0\%$ |
| **Classe C** | Alto ganho inicial de resistência | **$6{,}30\text{ gal/sk}$** | $56{,}0\%$ |
| **Classe D, E, F**| Poços profundos e quentes | **$4{,}30\text{ gal/sk}$** | $38{,}0\%$ |
| **Classe G** | **Padrão global da indústria** ($0 - 2.440\text{ m}$) | **$5{,}00\text{ gal/sk}$** | **$44{,}0\%$** |
| **Classe H** | Alternativa para poços profundos | **$4{,}30\text{ gal/sk}$** | **$38{,}0\%$** |

---

## 4. Como os Aditivos Entram na Conta (% BWOC)

A dosagem da maioria dos aditivos é expressa em **$\%\text{ BWOC}$** (*By Weight of Cement* - Porcento em Relação ao Peso do Cimento).

- Se adicionamos **$2{,}0\%\text{ BWOC}$ de Bentonita** a $1\text{ saco}$ de cimento:
  $$\text{Massa da Bentonita} = 94{,}0\text{ lb} \times \frac{2{,}0}{100} = \mathbf{1{,}88\text{ lb}}$$
  
- Como a Bentonita possui $SG = 2{,}65$:
  $$V_{bentonita} = \frac{1{,}88\text{ lb}}{2{,}65 \times 8{,}33\text{ lb/gal}} = \mathbf{0{,}085\text{ gal}}$$

---

## 5. As Três Fórmulas Mestras do Simulador

### 1️⃣ Rendimento Volumétrico da Pasta ($Yield$ ou $Y$)
É o volume total de pasta fluida gerado por cada saco de cimento misturado:

$$Y = \frac{V_{cimento} + V_{água} + \sum V_{aditivos}}{7{,}48052} \quad [ft^3/\text{sk}]$$

> *(O fator $7{,}48052$ converte galões americanos para pés cúbicos, $ft^3$).*

### 2️⃣ Densidade Resultante da Pasta ($\rho_{pasta}$)
É a massa total de todos os componentes dividida pelo volume total líquido:

$$\rho_{pasta} = \frac{M_{cimento} + M_{água} + \sum M_{aditivos}}{V_{cimento} + V_{água} + \sum V_{aditivos}} \quad [\text{lbm/gal ou ppg}]$$

### 3️⃣ Número Total de Sacos de Cimento ($N_{sk}$)
Para preencher o volume anular geométrico do poço ($V_{anular\_total}$ em $ft^3$):

$$N_{sk} = \frac{V_{anular\_total}}{Y} \quad [\text{sacos}]$$

---

## 6. Pressão Hidrostática no Fundo ($P_{hid}$)

A pressão que a coluna líquida de cimento exerce no fundo do poço (para não deixar o gás entrar e nem fraturar a rocha) é calculada por:

$$P_{hid} = 0{,}052 \cdot \sum_{i=1}^{n} (\rho_i \cdot h_i) \quad [psi]$$

Onde:
- $0{,}052$ é a constante de conversão de unidades de campo de petróleo ($ppg \cdot ft \rightarrow psi$).
- $\rho_i$ é a densidade de cada seção de pasta ($ppg$).
- $h_i$ é a altura vertical da seção de pasta ($ft$).

---

➡️ **Próximo passo:** Para conhecer todos os aditivos químicos disponíveis e suas funções, leia o documento [**03. Guia Completo de Aditivos de Cimentação**](./03_guia_de_aditivos.md).
