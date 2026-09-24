"""
Validador e Benchmark do Módulo de Janela Operacional (Geopressões - Mar do Norte)
Executa o motor físico e compara numericamente com os resultados salvos em resultados/A, B, K.
"""

import os
import sys

# Garante saída UTF-8 no terminal Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd

# Caminhos base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUTS_DIR = os.path.join(BASE_DIR, "inputs_codigo")
RES_DIR = os.path.join(BASE_DIR, "resultados")

print(f"Diretório base: {BASE_DIR}")
print(f"Diretório de inputs: {INPUTS_DIR}")

# 1. Carregar os 4 CSVs de entrada
_sonico_csv = pd.read_csv(os.path.join(INPUTS_DIR, "sonico.csv"))
_cabecalho_csv = pd.read_csv(os.path.join(INPUTS_DIR, "cabecalho.csv"))
_lama_csv = pd.read_csv(os.path.join(INPUTS_DIR, "lama.csv"))
_lot_csv = pd.read_csv(os.path.join(INPUTS_DIR, "lot.csv"))

POCOS = sorted(_cabecalho_csv["poço"].unique().tolist())
print(f"Poços identificados nos inputs: {POCOS}")

# Constantes físicas do motor
G_PSI_POR_M = 1.422
FATOR_PPG = 0.1704
RHO_AGUA_MAR = 1.03
A_GARDNER = 0.234
B_GARDNER = 0.25
N_EATON = 2.0
THETA_GRAUS = 32.0
C0_PSI = 700.0
COEF_SIGMA_H = 3.25
PPG_POR_SG = 8.3454
GN_PREMISSA_PPG = 1.03 * PPG_POR_SG
CORTE_GR_API = 75.0
FOLGA_ABAIXO_DO_LEITO_M = 150.0
SEPARACAO_MINIMA_TENDENCIA_M = 500.0


class ErroDeDados(ValueError):
    pass


class ErroDeCaso(RuntimeError):
    pass


def _num(s) -> pd.Series:
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    return pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce")


def colunas_sonico(d: pd.DataFrame):
    c_d = [c for c in d.columns if "prof" in c.lower() or c.strip() == "D (m)"][0]
    c_dt = [c for c in d.columns if "dt" in c.lower() or "t" in c.lower()][0]
    return c_d, c_dt


def colunas_lot(d: pd.DataFrame):
    return "D(s)", "LOT", "Sobrecarga", "Poros"


def mod_sobrecarga(df_son, LDA, a_gardner=A_GARDNER, b_gardner=B_GARDNER, rho_agua=RHO_AGUA_MAR):
    LDA = float(LDA)
    d = df_son.copy()
    c_d, c_dt = colunas_sonico(d)
    son = pd.DataFrame({"Profundidade": _num(d[c_d]), "Delta t": _num(d[c_dt])})
    son = son.dropna(subset=["Profundidade", "Delta t"])
    son = son[son["Delta t"] > 0].sort_values("Profundidade").drop_duplicates("Profundidade")

    topo_d = [0.0, LDA]
    topo_dt = [np.nan, np.nan]
    corpo = son[son["Profundidade"] > LDA]
    prof = topo_d + corpo["Profundidade"].tolist()
    dt = topo_dt + corpo["Delta t"].tolist()

    dens = [rho_agua, rho_agua] + [
        float(a_gardner) * ((1e6 / float(x)) ** float(b_gardner)) for x in dt[2:]
    ]

    sigma = [np.nan]
    grad = [np.nan]
    soma = 0.0
    for i in range(1, len(prof)):
        soma += dens[i] * (prof[i] - prof[i - 1])
        s = G_PSI_POR_M * soma
        sigma.append(round(s, 1))
        grad.append(round(s / (FATOR_PPG * prof[i]), 1) if prof[i] > 0 else np.nan)

    df = pd.DataFrame({
        "Profundidade": prof,
        "Delta t": dt,
        "Densidade (g/cm³)": [round(x, 6) for x in dens],
        "Tensão de Sobrecarga": sigma,
        "Gradiente de Sobrecarga": grad,
    })
    df.loc[0, "Densidade (g/cm³)"] = np.nan
    return df, f"pontos={len(df)}", []


def _linha_com_dt(df, alvo, rotulo):
    v = df[df["Delta t"].notna() & (df["Delta t"] > 0)]
    i = (v["Profundidade"] - float(alvo)).abs().idxmin()
    return v.loc[i], None


def mod_poros(df, LDA, rft, n_eaton=N_EATON, d_trend0=None, d_trend1=None):
    df = df.copy()
    LDA = float(LDA)
    n_eaton = float(n_eaton)
    validos = df[df["Delta t"].notna() & (df["Delta t"] > 0)]

    dt_i = float(validos.iloc[0]["Delta t"])
    D_i = float(validos.iloc[0]["Profundidade"])

    if d_trend0 is None:
        d_trend0 = D_i
    if d_trend1 is None:
        d_trend1 = float(validos["Profundidade"].iloc[min(len(validos) - 1, len(validos) // 2)])
    l0, _ = _linha_com_dt(df, d_trend0, "Tendência 1")
    l1, _ = _linha_com_dt(df, d_trend1, "Tendência 2")
    D0, D1 = float(l0["Profundidade"]), float(l1["Profundidade"])
    dt0, dt1 = float(l0["Delta t"]), float(l1["Delta t"])
    m = np.log10(dt1 / dt0) / (D1 - D0)

    P = pd.to_numeric(df["Profundidade"], errors="coerce")
    df["Delta tN"] = np.where(
        df["Delta t"].notna(),
        np.round(dt_i * 10.0 ** (m * (P - D_i)), 2),
        np.nan,
    )

    Gob = pd.to_numeric(df["Gradiente de Sobrecarga"], errors="coerce")
    df["Gradiente de Sobrecarga"] = Gob
    gns = []
    for gp_med, d_med in rft:
        lin, _ = _linha_com_dt(df, d_med, "RFT")
        gob = float(lin["Gradiente de Sobrecarga"])
        razao = float(lin["Delta tN"]) / float(lin["Delta t"])
        gns.append((float(gp_med) - gob) / (razao ** n_eaton) + gob)
    GN = float(np.mean(gns))

    razao_perfil = df["Delta tN"] / df["Delta t"]
    Gp = Gob - (Gob - GN) * (razao_perfil ** n_eaton)
    Gp = Gp.where(df["Delta t"].notna())
    df["Gradiente de Poros"] = Gp.round(2)

    diag = {"m": m, "GN": GN, "d_trend0": D0, "d_trend1": D1}
    return df, diag, f"GN={GN:.2f}", []


def mod_fratura(df, df_lot, LDA, col_poros="Gradiente de Poros", limitar_gf_gob=True, sufixo=""):
    df = df.copy()
    LDA = float(LDA)
    lot = df_lot.copy().dropna()
    lot["K real"] = (lot["LOT"] - lot["Poros"]) / (lot["Sobrecarga"] - lot["Poros"])

    a_reg, b_reg = (float(v) for v in np.polyfit(lot["K real"], np.log(lot["D(s)"]), 1))

    P = pd.to_numeric(df["Profundidade"], errors="coerce")
    Ds = P - LDA
    with np.errstate(divide="ignore", invalid="ignore"):
        K = (np.log(Ds.where(Ds > 0)) - b_reg) / a_reg
    K = pd.Series(K, index=df.index).replace([np.inf, -np.inf], np.nan)
    df["K ajustado" + sufixo] = K.round(6)

    Gp = pd.to_numeric(df[col_poros], errors="coerce")
    Gob = pd.to_numeric(df["Gradiente de Sobrecarga"], errors="coerce")
    Gf = (Gp + K * (Gob - Gp)).round(4)
    if limitar_gf_gob:
        Gf = Gf.where(~(Gf > Gob))
    df["Gradiente de Fratura" + sufixo] = Gf

    diag = {"a_reg": a_reg, "b_reg": b_reg, "lot": lot}
    return df, lot, diag, "", []


def mod_colapso(df, LDA, col_poros="Gradiente de Poros", col_fratura="Gradiente de Fratura",
                theta_graus=THETA_GRAUS, C0=C0_PSI, coef_sigma_H=COEF_SIGMA_H, sufixo=""):
    df = df.copy()
    LDA = float(LDA)
    t2 = float(np.tan(np.pi / 4 + np.radians(float(theta_graus)) / 2) ** 2)

    P = pd.to_numeric(df["Profundidade"], errors="coerce")
    Gp = pd.to_numeric(df[col_poros], errors="coerce")
    Gf = pd.to_numeric(df[col_fratura], errors="coerce")

    sig_h = (float(coef_sigma_H) * (P - LDA)).round(1)
    sig_h = sig_h.where(P > LDA)
    Pf = (P * FATOR_PPG * Gf).round(1)
    Pp = (P * FATOR_PPG * Gp).round(1)
    Pc = ((3 * sig_h - Pf - C0 + Pp * (t2 - 1)) / (t2 + 1)).round(1)
    Gc = (Pc / (P * FATOR_PPG)).where(P > 0).round(4)

    df["Sigma H" + sufixo] = sig_h
    df["Pressão de Fratura" + sufixo] = Pf
    df["Pressão de Poros" + sufixo] = Pp
    df["Pc (psi)" + sufixo] = Pc
    df["Gradiente de Colapso" + sufixo] = Gc

    diag = {"t2": t2, "theta_graus": float(theta_graus), "C0": float(C0), "coef_sigma_H": float(coef_sigma_H)}
    return df, diag, "", []


def janela_operacional(df, col_poros="Gradiente de Poros", col_fratura="Gradiente de Fratura", col_colapso="Gradiente de Colapso"):
    cols = ["Profundidade", "Gradiente de Sobrecarga", col_poros, col_fratura, col_colapso]
    d = df.copy()
    for c in cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=cols).sort_values("Profundidade")
    d["Limite inferior"] = np.maximum(d[col_poros], d[col_colapso])
    d["Limite superior"] = np.minimum(d[col_fratura], d["Gradiente de Sobrecarga"])
    d["Largura da janela"] = d["Limite superior"] - d["Limite inferior"]
    return d, "", []


# Estrutura auxiliar
class G:
    mod_sobrecarga = staticmethod(mod_sobrecarga)
    mod_poros = staticmethod(mod_poros)
    mod_fratura = staticmethod(mod_fratura)
    mod_colapso = staticmethod(mod_colapso)
    janela_operacional = staticmethod(janela_operacional)
    FATOR_PPG = FATOR_PPG
    N_EATON = N_EATON
    THETA_GRAUS = THETA_GRAUS
    C0_PSI = C0_PSI
    COEF_SIGMA_H = COEF_SIGMA_H


def cabecalho(poco: str) -> dict:
    return _cabecalho_csv[_cabecalho_csv["poço"] == poco].iloc[0].to_dict()


def sonico_preenchido(poco: str) -> pd.DataFrame:
    cols = ["D (m)", "Δt (µs/ft)", "GR (API)", "RHOB (g/cm³)", "CALI (pol)",
            "Δt de análogo", "Δt mínimo dos análogos", "Δt máximo dos análogos"]
    d = _sonico_csv[_sonico_csv["poço"] == poco][cols].copy()
    return d.sort_values("D (m)").reset_index(drop=True)


def lama(poco: str) -> pd.DataFrame:
    d = _lama_csv[_lama_csv["poço"] == poco][["D_m", "lama_sg", "lama_ppg", "tipo"]].copy()
    return d.sort_values("D_m").reset_index(drop=True)


def pontos_de_lot(poco: str) -> pd.DataFrame:
    d = _lot_csv[_lot_csv["poço"] == poco][["tipo", "diametro", "sapata_m", "lot_sg", "lot_ppg"]].copy()
    return d.sort_values("sapata_m").reset_index(drop=True)


def intervalo_de_tendencia(poco: str):
    cab = cabecalho(poco)
    return cab["LDA"] + FOLGA_ABAIXO_DO_LEITO_M, float(cab["topo_rogaland_m"])


def pontos_da_tendencia(son: pd.DataFrame, faixa, corte_gr=None):
    d = son[(son["D (m)"] >= faixa[0]) & (son["D (m)"] <= faixa[1])].copy()
    d = d[d["Δt (µs/ft)"] > 0]
    if corte_gr is not None:
        d = d[d["GR (API)"].notna() & (d["GR (API)"] >= corte_gr)]
    D = d["D (m)"].values.astype(float)
    L = np.log10(d["Δt (µs/ft)"].values.astype(float))
    m_lsq, b_lsq = np.polyfit(D, L, 1)

    melhor = None
    for i in range(len(D)):
        dif = D - D[i]
        ok = np.abs(dif) >= SEPARACAO_MINIMA_TENDENCIA_M
        if not ok.any():
            continue
        m_par = (L[ok] - L[i]) / dif[ok]
        j = int(np.argmin(np.abs(m_par - m_lsq)))
        erro = abs(m_par[j] - m_lsq)
        if melhor is None or erro < melhor[0]:
            melhor = (erro, D[i], D[ok][j], m_par[j])
    erro, d0, d1, m_par = melhor
    if d1 < d0:
        d0, d1 = d1, d0
    return {"d0": float(d0), "d1": float(d1), "m_lsq": float(m_lsq), "m_par": float(m_par)}


def aplica_mascara_de_folhelho(df: pd.DataFrame, son: pd.DataFrame, corte_gr: float):
    df = df.copy()
    gr = pd.Series(son.set_index("D (m)")["GR (API)"]).reindex(
        pd.to_numeric(df["Profundidade"], errors="coerce").values).values
    df["GR (API)"] = gr
    folhelho = pd.Series(gr, index=df.index).notna() & (pd.Series(gr, index=df.index) >= corte_gr)
    gp = pd.to_numeric(df["Gradiente de Poros"], errors="coerce")
    P = pd.to_numeric(df["Profundidade"], errors="coerce")
    valido = folhelho & gp.notna()

    interp = pd.Series(np.interp(P.values, P[valido].values, gp[valido].values), index=df.index)
    interp[(P < P[valido].min()) | (P > P[valido].max())] = np.nan
    df["Gp de folhelho"] = np.where(valido, gp, np.nan)
    df["Gradiente de Poros"] = np.where(valido, gp, interp).round(2)
    df["Gp interpolado"] = (~valido) & df["Gradiente de Poros"].notna()
    return df, {"corte_gr": float(corte_gr)}


def c0_pelo_peso_de_lama(df: pd.DataFrame, lam: pd.DataFrame, theta_graus: float, c0_referencia: float):
    t2 = float(np.tan(np.pi / 4.0 + np.radians(theta_graus) / 2.0) ** 2)
    P = pd.to_numeric(df["Profundidade"], errors="coerce")
    gc = pd.to_numeric(df["Gradiente de Colapso"], errors="coerce")
    ok = P.notna() & gc.notna()

    exigencias = []
    for _, r in lam.iterrows():
        d = float(r["D_m"])
        if d < P[ok].min() or d > P[ok].max():
            continue
        gc_d = float(np.interp(d, P[ok].values, gc[ok].values))
        exigencias.append({"D_m": d, "lama_ppg": float(r["lama_ppg"]), "Gc_ppg": gc_d,
                           "delta_C0_psi": (gc_d - float(r["lama_ppg"])) * (t2 + 1.0) * G.FATOR_PPG * d})
    e = pd.DataFrame(exigencias)
    c0_minimo = float(c0_referencia + e["delta_C0_psi"].max())
    if c0_minimo <= c0_referencia:
        return c0_referencia, {"c0_usado": float(c0_referencia), "recalibrou": False}
    return c0_minimo, {"c0_usado": c0_minimo, "recalibrou": True}


def quadro_de_lot(poco: str, df: pd.DataFrame, lda: float) -> pd.DataFrame:
    lots = pontos_de_lot(poco)
    P = pd.to_numeric(df["Profundidade"], errors="coerce")
    gob = pd.to_numeric(df["Gradiente de Sobrecarga"], errors="coerce")
    gp = pd.to_numeric(df["Gradiente de Poros"], errors="coerce")

    linhas = []
    for _, r in lots.iterrows():
        d = float(r["sapata_m"])
        ok_ob = P.notna() & gob.notna()
        ok_gp = P.notna() & gp.notna()
        if d < P[ok_gp].min() or d > P[ok_gp].max():
            continue
        linhas.append({
            "poço de origem": poco, "D (m)": d, "D(s)": d - lda,
            "LOT": float(r["lot_ppg"]), "LOT (g/cm³)": float(r["lot_sg"]),
            "diâmetro": r["diametro"],
            "Sobrecarga": float(np.interp(d, P[ok_ob], gob[ok_ob])),
            "Poros": float(np.interp(d, P[ok_gp], gp[ok_gp])),
        })
    return pd.DataFrame(linhas)


def roda_caso(poco: str, variante: str, pocos_do_K=None, corte_gr=CORTE_GR_API,
               gn_ppg=GN_PREMISSA_PPG, n_eaton=G.N_EATON, coef_sigma_H=G.COEF_SIGMA_H,
               theta_graus=G.THETA_GRAUS, c0_referencia=G.C0_PSI, quadros_de_lot=None) -> dict:
    sintetica = variante == "sintética"
    calibrada = variante in ("B", "sintética")

    cab = cabecalho(poco)
    lda = cab["LDA"]
    son = sonico_preenchido(poco)
    lam = lama(poco)

    df, _, _ = G.mod_sobrecarga(son[["D (m)", "Δt (µs/ft)"]], lda)

    faixa = intervalo_de_tendencia(poco)
    tend = pontos_da_tendencia(son, faixa, corte_gr if calibrada else None)
    rft = [(gn_ppg, tend["d0"]), (gn_ppg, tend["d1"])]

    df_eaton = df.copy()
    acima = pd.to_numeric(df_eaton["Profundidade"], errors="coerce") < tend["d0"]
    df_eaton.loc[acima, "Delta t"] = np.nan
    df, _, _, _ = G.mod_poros(df_eaton, lda, rft, n_eaton=n_eaton, d_trend0=tend["d0"], d_trend1=tend["d1"])
    df["Delta t"] = pd.to_numeric(
        pd.Series(son.set_index("D (m)")["Δt (µs/ft)"]).reindex(
            pd.to_numeric(df["Profundidade"], errors="coerce").values).values,
        errors="coerce")

    P_flag = pd.to_numeric(df["Profundidade"], errors="coerce")
    df["Eaton extrapolado"] = P_flag > faixa[1]

    if calibrada:
        df, _ = aplica_mascara_de_folhelho(df, son, corte_gr)
    else:
        gr = pd.Series(son.set_index("D (m)")["GR (API)"]).reindex(
            pd.to_numeric(df["Profundidade"], errors="coerce").values).values
        df["GR (API)"] = gr
        df["Gp de folhelho"] = np.nan
        df["Gp interpolado"] = False

    if quadros_de_lot is None:
        quadros_de_lot = {}
    if sintetica:
        partes = [quadros_de_lot[p] for p in pocos_do_K if p in quadros_de_lot]
        q_lot = pd.concat(partes, ignore_index=True)
        origem_do_K = "LOT dos vizinhos: " + ", ".join(pocos_do_K)
    else:
        q_lot = quadro_de_lot(poco, df, lda)
        origem_do_K = "LOT do próprio poço"

    COLUNAS_DO_MODULO = ["D(s)", "LOT", "Sobrecarga", "Poros"]
    df, lot_c, _, _, _ = G.mod_fratura(df, q_lot[COLUNAS_DO_MODULO], lda, "Gradiente de Poros")
    df, _, _, _ = G.mod_colapso(df, lda, theta_graus=theta_graus, C0=c0_referencia, coef_sigma_H=coef_sigma_H)

    if calibrada:
        c0, d_c0 = c0_pelo_peso_de_lama(df, lam, theta_graus, c0_referencia)
        if d_c0["recalibrou"]:
            df, _, _, _ = G.mod_colapso(df, lda, theta_graus=theta_graus, C0=c0, coef_sigma_H=coef_sigma_H)

    jan, _, _ = G.janela_operacional(df)

    # Injeta identificadores idênticos ao CSV salvo
    df.insert(0, "poço", poco)
    df.insert(1, "variante", variante if not sintetica else "sintética")
    df.insert(2, "origem_do_K", origem_do_K)

    return {
        "poço": poco, "variante": variante, "df": df, "janela": jan,
        "quadro_de_lot": q_lot
    }


# EXECUÇÃO DO BENCHMARK
print("\n" + "=" * 60)
print("🚀 EXECUTANDO MOTOR DE JANELAS OPERACIONAIS...")
print("=" * 60)

quadros = {}
casos = {}

# 1. Roda variantes A e B para todos os poços
for p in POCOS:
    for v in ("A", "B"):
        c = roda_caso(p, v)
        casos[(p, v)] = c
        if v == "B":
            quadros[p] = c["quadro_de_lot"]
        print(f"✓ Poço {p} - Variante {v} concluído ({len(c['df'])} profundidades calculadas).")

# 2. Roda variante Sintética K para todos os poços
for p in POCOS:
    vizinhos = [q for q in POCOS if q != p]
    c = roda_caso(p, "sintética", pocos_do_K=vizinhos, quadros_de_lot=quadros)
    casos[(p, "sintética")] = c
    print(f"✓ Poço {p} - Variante Sintética K concluído com vizinhos {vizinhos}.")

print("\n" + "=" * 60)
print("🔍 AUDITORIA NUMÉRICA: CONFRONTANDO COM CSVs DE RESULTADOS...")
print("=" * 60)

def conferir_contra_csv_salvo(poco, variante, subpasta, nome_arquivo):
    caminho_csv = os.path.join(RES_DIR, subpasta, nome_arquivo)
    if not os.path.exists(caminho_csv):
        print(f"⚠️ Arquivo de referência não encontrado: {caminho_csv}")
        return

    df_esperado = pd.read_csv(caminho_csv)
    caso = casos[(poco, variante)]
    df_gerado = caso["df"]

    # Comparar colunas numéricas chave
    colunas_teste = [
        "Profundidade", "Tensão de Sobrecarga", "Gradiente de Sobrecarga",
        "Gradiente de Poros", "Gradiente de Fratura", "Gradiente de Colapso"
    ]

    erros_max = {}
    for col in colunas_teste:
        if col in df_esperado.columns and col in df_gerado.columns:
            s_esp = pd.to_numeric(df_esperado[col], errors="coerce")
            s_ger = pd.to_numeric(df_gerado[col], errors="coerce")
            mask = s_esp.notna() & s_ger.notna()
            if mask.sum() > 0:
                diff = (s_esp[mask] - s_ger[mask]).abs().max()
                erros_max[col] = diff

    print(f"\n📊 Poço {poco} | Variante {variante} (comparado com {nome_arquivo}):")
    print(f"   - Linhas geradas: {len(df_gerado)} | Linhas de referência: {len(df_esperado)}")
    for col, diff in erros_max.items():
        status = "✅ IGUAL" if diff < 1e-3 else f"⚠️ Dif={diff:.4f}"
        print(f"   - {col:25s}: {status} (erro máximo = {diff:.6f})")

# Testar para poço 15/9-13
conferir_contra_csv_salvo("15/9-13", "A", "A", "perfil_15_9-13_variante_A.csv")
conferir_contra_csv_salvo("15/9-13", "B", "B", "perfil_15_9-13_variante_B.csv")
conferir_contra_csv_salvo("15/9-13", "sintética", "K", "perfil_15_9-13_sintetica_K_dos_vizinhos.csv")

# Testar para outro poço (ex: 15/9-14)
conferir_contra_csv_salvo("15/9-14", "A", "A", "perfil_15_9-14_variante_A.csv")
conferir_contra_csv_salvo("15/9-14", "B", "B", "perfil_15_9-14_variante_B.csv")
conferir_contra_csv_salvo("15/9-14", "sintética", "K", "perfil_15_9-14_sintetica_K_dos_vizinhos.csv")
