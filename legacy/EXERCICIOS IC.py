import math
from enum import nonmember

#CONSTANTES
m_saco = 94
ro_agua = 8.33
d_cimento = 3.14
d_bentonita = 2.65
d_sNaCl = 1.0279
d_sCaCl2 = 1.0329
pi = math.pi
Volumes = []
Sacos = []
#CONSTANTES

#FUNÇÕES
def pergunta(prompt,prompt2):
    a = input(prompt)
    while a != "s" and a != "n":
        a = input(prompt)
    if a == "s":
        return float(input(prompt2))
    elif a == "n": return 0
#FUNÇÕES


#INPUTS PADROES
D = float(input(f"Digite a profundidade total em ft:"))
DE = float(input(f"Digite o Diametro Externo em in:"))
DI = float(input(f"Digite o Diametro Interno em in:"))
DB = float(input(f"Digite o Diametro da Broca em in:"))
FE = float(input(f"Digite o Fator de Excesso:"))
V_Agua = 0
#INPUTS PADROES


CF = pergunta(f"Possui Colar Flutuante?(s/n):",f"A que distancia, em ft, da Sapata?:")

qtd_pasta = int(input(f"Quantas pastas serão utilizadas?:"))
npasta = 1

if qtd_pasta != 1:
    print(f"AS PASTAS SÃO NUMERADAS DE BAIXO PARA CIMA!")

while qtd_pasta != 0:
        print(f"Sobre a pasta {npasta}:")
        h = float(input(f"Qual a distancia a partir do fundo?:"))
        classe = (input(f"Qual a classe do cimento?:"))
        if classe == "A" or "B":
            V_Agua = 5.2
        if classe == "C":
            V_Agua = 6.3
        if classe == "D" or "E" or "F" or "H":
            V_Agua = 4.3
        if classe == "G":
            V_Agua = 5
        

        bentonita = pergunta(f"Possui Bentonita na composição?(s/n):",f"Qual a porcentagem de bentonita?:")
        NaCl = pergunta(f"Possui NaCl na composição?(s/n):",f"Qual a porcentagem de NaCl?:")
        CaCl2 = pergunta(f"Possui CaCl2 na composição?(s/n):",f"Qual a porcentagem de CaCl2?:")
        PM = pergunta(f"Possui Fator Água-Cimento específico?(s/n):",f"Quantos gal/saco?:")
        V_Agua = PM

        # Vpasta
        V_Anular = (pi / 4) * (DB ** 2 - DE ** 2) * h / 144
        if npasta > 1:
            CF = 0
        V_cs = (pi / 4) * (DI ** 2) * CF / 144

        V_pasta = (V_Anular * FE) + V_cs
        Volumes.append(V_pasta)
        # Vpasta

        # Vcimento
        V_cimento = m_saco / (d_cimento * ro_agua)
        # Vcimento

        # Vsalmoura
        m_agua = ro_agua * V_Agua
        m_CaCl2 = (CaCl2 / 100) * m_saco
        m_NaCl = (NaCl / 100) * m_saco
        if CaCl2 != 0:
            V_salmoura_CaCl2 = (m_CaCl2 + m_agua) / (d_sCaCl2 * ro_agua)
        else:
            V_salmoura_CaCl2 = 0
        if NaCl != 0:
            V_salmoura_NaCl = (m_NaCl + m_agua) / (d_sNaCl * ro_agua)
        else:
            V_salmoura_NaCl = 0
        # V_Salmoura

        # V_Bentonita
        m_bentonita = (bentonita / 100) * m_saco
        V_bentonita = m_bentonita / (d_bentonita * ro_agua)
        # V_Bentonita

        # Rendimento
        Y = (V_cimento + V_bentonita + V_salmoura_CaCl2 + V_salmoura_NaCl) / 7.5
        Y_Arredondado = round(Y, 1)
        print(f"O Rendimento em ft\u00b3 para a pasta {npasta} é: {Y_Arredondado}")
        # Rendimento

        # N_Sacos
        N_Sacos = V_pasta / Y
        N_Sacos_Arredondado = round(N_Sacos)
        Sacos.append(N_Sacos_Arredondado)
        print(f"O número de sacos de cimento necessário para a pasta {npasta} é:{N_Sacos_Arredondado}")
        # N_Sacos

        npasta += 1
        qtd_pasta -= 1

print(Volumes, Sacos)