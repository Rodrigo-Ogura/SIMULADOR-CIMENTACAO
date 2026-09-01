import math
from typing import List, Tuple

# incluir a densidade de cada pasta e rendimento no resumo final

# CONSTANTES
M_SACO = 94  # lb
RO_AGUA = 8.33  # lb/gal
D_CIMENTO = 3.14  # rel
D_BENTONITA = 2.65
D_S_NACL = 1.0279
D_S_CACL2 = 1.0329
PI = math.pi

# Dicionário de volumes de água por classe de cimento
VOLUME_AGUA_POR_CLASSE = {
    'A': 5.2, 'B': 5.2,
    'C': 6.3,
    'D': 4.3, 'E': 4.3, 'F': 4.3, 'H': 4.3,
    'G': 5.0
}


class PastaCimento:
    """Classe para representar uma pasta de cimento"""

    def __init__(self, numero: int, distancia_fundo: float, classe: str):
        self.numero = numero
        self.distancia_fundo = distancia_fundo
        self.classe = classe.upper()
        self.bentonita = 0.0
        self.nacl = 0.0
        self.cacl2 = 0.0
        self.fator_agua_cimento = 0.0
        self.volume_pasta = 0.0
        self.rendimento = 0.0
        self.numero_sacos = 0
        self.densidade = 0.0  # lbm/gal


def pergunta_sim_nao(prompt: str) -> bool:
    """Faz uma pergunta sim/não e retorna boolean"""
    while True:
        resposta = input(prompt).lower().strip()
        if resposta in ['s', 'sim']:
            return True
        elif resposta in ['n', 'não', 'nao']:
            return False
        print("Por favor, digite 's' para sim ou 'n' para não.")


def pergunta_porcentagem(prompt: str) -> float:
    """Faz uma pergunta e retorna um valor float"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Por favor, digite um número válido.")


def calcular_volume_anular(diametro_broca: float, diametro_externo: float, altura: float) -> float:
    """Calcula o volume anular em ft³"""
    return (PI / 4) * (diametro_broca ** 2 - diametro_externo ** 2) * altura / 144


def calcular_volume_colar_flutuante(diametro_interno: float, distancia_sapata: float) -> float:
    """Calcula o volume do colar flutuante em ft³"""
    return (PI / 4) * (diametro_interno ** 2) * distancia_sapata / 144


def calcular_volume_cimento() -> float:
    """Calcula o volume do cimento por saco em ft³/gal"""
    return M_SACO / (D_CIMENTO * RO_AGUA)


def calcular_volume_salmoura(massa_agua: float, porcentagem: float, densidade_salmoura: float) -> float:
    """Calcula o volume da salmoura em ft³/gal"""
    if porcentagem == 0:
        return 0
    massa_aditivo = (porcentagem / 100) * M_SACO
    return (massa_aditivo + massa_agua) / (densidade_salmoura * RO_AGUA)


def calcular_volume_bentonita(porcentagem: float) -> float:
    """Calcula o volume da bentonita em ft³/gal"""
    if porcentagem == 0:
        return 0
    massa_bentonita = (porcentagem / 100) * M_SACO
    return massa_bentonita / (D_BENTONITA * RO_AGUA)


def calcular_rendimento(pasta: PastaCimento) -> float:
    """Calcula o rendimento da pasta em ft³/saco"""
    volume_agua = pasta.fator_agua_cimento if pasta.fator_agua_cimento > 0 else VOLUME_AGUA_POR_CLASSE.get(pasta.classe,
                                                                                                           5.0)
    massa_agua = RO_AGUA * volume_agua

    volume_cimento = calcular_volume_cimento()
    volume_bentonita = calcular_volume_bentonita(pasta.bentonita)
    volume_salmoura_cacl2 = calcular_volume_salmoura(massa_agua, pasta.cacl2, D_S_CACL2)
    volume_salmoura_nacl = calcular_volume_salmoura(massa_agua, pasta.nacl, D_S_NACL)

    return (volume_cimento + volume_bentonita + volume_salmoura_cacl2 + volume_salmoura_nacl) / 7.5


def calcular_densidade_pasta(pasta: PastaCimento) -> float:
    """
    Calcula a densidade da pasta segundo a fórmula:
    Densidade = (massa_agua + massa_cimento + massa_aditivos) / (volume_agua + volume_cimento + volume_aditivos)
    Unidade: lbm/gal
    """
    # Volume e massa de água
    volume_agua = pasta.fator_agua_cimento if pasta.fator_agua_cimento > 0 else VOLUME_AGUA_POR_CLASSE.get(pasta.classe,
                                                                                                           5.0)
    massa_agua = RO_AGUA * volume_agua

    # Massa e volume do cimento
    massa_cimento = M_SACO
    volume_cimento = massa_cimento / (D_CIMENTO * RO_AGUA)

    # Massas e volumes dos aditivos
    massa_bentonita = (pasta.bentonita / 100) * M_SACO if pasta.bentonita > 0 else 0
    volume_bentonita = massa_bentonita / (D_BENTONITA * RO_AGUA) if pasta.bentonita > 0 else 0

    massa_nacl = (pasta.nacl / 100) * M_SACO if pasta.nacl > 0 else 0
    volume_nacl = (massa_nacl + massa_agua) / (D_S_NACL * RO_AGUA) if pasta.nacl > 0 else 0

    massa_cacl2 = (pasta.cacl2 / 100) * M_SACO if pasta.cacl2 > 0 else 0
    volume_cacl2 = (massa_cacl2 + massa_agua) / (D_S_CACL2 * RO_AGUA) if pasta.cacl2 > 0 else 0

    # Cálculo da densidade total
    massa_total = massa_agua + massa_cimento + massa_bentonita + massa_nacl + massa_cacl2
    volume_total = volume_agua + volume_cimento + volume_bentonita + volume_nacl + volume_cacl2

    # Densidade em lbm/gal
    if volume_total > 0:
        densidade = massa_total / volume_total
    else:
        densidade = 0

    return densidade


def obter_dados_pasta(numero_pasta: int) -> PastaCimento:
    """Obtém os dados de uma pasta do usuário"""
    print(f"\n--- Dados da Pasta {numero_pasta} ---")

    distancia_fundo = pergunta_porcentagem("Qual a distância a partir do fundo (ft): ")
    classe = input("Qual a classe do cimento? (A, B, C, D, E, F, G, H): ").upper()

    pasta = PastaCimento(numero_pasta, distancia_fundo, classe)

    # Aditivos
    if pergunta_sim_nao("Possui Bentonita na composição? (s/n): "):
        pasta.bentonita = pergunta_porcentagem("Qual a porcentagem de bentonita: ")

    if pergunta_sim_nao("Possui NaCl na composição? (s/n): "):
        pasta.nacl = pergunta_porcentagem("Qual a porcentagem de NaCl: ")

    if pergunta_sim_nao("Possui CaCl2 na composição? (s/n): "):
        pasta.cacl2 = pergunta_porcentagem("Qual a porcentagem de CaCl2: ")

    if pergunta_sim_nao("Possui Fator Água-Cimento específico? (s/n): "):
        pasta.fator_agua_cimento = pergunta_porcentagem("Quantos gal/saco: ")

    return pasta


def main():
    """Função principal do programa"""
    print("=== CALCULADORA DE CIMENTAÇÃO ===")

    # Inputs básicos
    profundidade_total = pergunta_porcentagem("Digite a profundidade total em ft: ")
    diametro_externo = pergunta_porcentagem("Digite o Diâmetro Externo em in: ")
    diametro_interno = pergunta_porcentagem("Digite o Diâmetro Interno em in: ")
    diametro_broca = pergunta_porcentagem("Digite o Diâmetro da Broca em in: ")
    fator_excesso = pergunta_porcentagem("Digite o Fator de Excesso: ")
    distancia_sapata = pergunta_porcentagem("Digite a distância do colar flutuante da sapata (ft): ")

    quantidade_pastas = int(pergunta_porcentagem("Quantas pastas serão utilizadas?: "))

    if quantidade_pastas > 1:
        print("\n⚠️  AS PASTAS SÃO NUMERADAS DE BAIXO PARA CIMA!")

    pastas = []
    volumes = []
    sacos = []

    # Processamento de cada pasta
    for numero_pasta in range(1, quantidade_pastas + 1):
        pasta = obter_dados_pasta(numero_pasta)

        # Cálculo do volume da pasta
        volume_anular = calcular_volume_anular(diametro_broca, diametro_externo, pasta.distancia_fundo)

        # Apenas a primeira pasta considera o colar flutuante
        volume_colar = calcular_volume_colar_flutuante(diametro_interno, distancia_sapata) if numero_pasta == 1 else 0

        pasta.volume_pasta = (volume_anular * fator_excesso) + volume_colar
        volumes.append(pasta.volume_pasta)

        # Cálculo do rendimento
        pasta.rendimento = calcular_rendimento(pasta)

        # Cálculo da densidade
        pasta.densidade = calcular_densidade_pasta(pasta)

        # Cálculo do número de sacos
        pasta.numero_sacos = round(pasta.volume_pasta / pasta.rendimento)
        sacos.append(pasta.numero_sacos)
        print(f"O número de sacos de cimento necessário para a pasta {numero_pasta} é: {pasta.numero_sacos}")

        pastas.append(pasta)

    # Resumo final
    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50)

    for pasta in pastas:
        rendimento_arredondado = round(pasta.rendimento, 1)
        densidade_arredondada = round(pasta.densidade, 2)
        print(
            f"Pasta {pasta.numero}: {pasta.numero_sacos} sacos, Volume: {pasta.volume_pasta:.1f} ft³, Rendimento: {rendimento_arredondado} ft³/saco, Densidade: {densidade_arredondada} lbm/gal")

    return volumes, sacos


volumes, sacos = main()