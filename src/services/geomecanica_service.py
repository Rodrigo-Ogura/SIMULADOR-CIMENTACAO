"""
Serviço de Gestão e Processamento de Perfis Geomecânicos e Janelas Operacionais.
Suporta importação de CSVs externos e perfis pré-calculados do Mar do Norte (Equinor/Sodir Bloco 15/9).
"""

import os
import io
import re
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from src.utils.logger import logger

# Conversão de unidades
METROS_PARA_PES = 3.28084
PES_PARA_METROS = 0.3048


class GeomecanicaService:
    """Serviço para carga, padronização e análise de curvas de janelas geomecânicas."""

    # Diretório dos resultados pré-calculados
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    RESULTADOS_DIR = os.path.join(ROOT_DIR, "sandbox", "janela_operacional", "resultados")

    @classmethod
    def listar_pocos_presets(cls) -> List[str]:
        """Lista os poços históricos disponíveis com perfis calibrados."""
        return ["15/9-13", "15/9-14", "15/9-15", "15/9-17", "15/9-23"]

    @classmethod
    def listar_variantes(cls) -> Dict[str, str]:
        """Lista as variantes geomecânicas disponíveis."""
        return {
            "B": "🟢 Variante B (Recomendada: Calibrada com Lama e Folhelhos)",
            "A": "🟡 Variante A (Literatura Clássica: Premissas do Enunciado)",
            "K": "🔵 Variante K (Sintética: Calibração Regional por Poços Vizinhos)"
        }

    @classmethod
    def carregar_preset(cls, poco: str, variante: str) -> Optional[pd.DataFrame]:
        """
        Carrega o perfil pré-calculado de um dos poços do Mar do Norte.
        """
        poco_slug = poco.replace("/", "_")
        subpasta = variante if variante in ("A", "B", "K") else "B"

        if variante in ("A", "B"):
            nome_arquivo = f"perfil_{poco_slug}_variante_{variante}.csv"
        else:
            nome_arquivo = f"perfil_{poco_slug}_sintetica_K_dos_vizinhos.csv"

        caminho = os.path.join(cls.RESULTADOS_DIR, subpasta, nome_arquivo)
        if not os.path.exists(caminho):
            logger.warning(f"Arquivo preset não encontrado: {caminho}")
            return None

        try:
            df_bruto = pd.read_csv(caminho)
            return cls.padronizar_dataframe(df_bruto, unidade_prof_entrada="m", nome_fonte=f"Poço {poco} (Var. {variante})")
        except Exception as e:
            logger.error(f"Erro ao carregar preset {caminho}: {e}")
            return None

    @classmethod
    def processar_csv_upload(cls, arquivo_ou_buffer, unidade_prof_entrada: str = "m", nome_arquivo: str = "CSV Personalizado") -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Lê e padroniza qualquer CSV de perfil geomecânico enviado pelo usuário.
        Tolerante a separadores (, ou ;) e variações comuns de nomes de coluna.
        """
        try:
            # Leitura flexível universal (UploadedFile, bytes, str ou arquivo aberto)
            if hasattr(arquivo_ou_buffer, "read"):
                conteudo = arquivo_ou_buffer.read()
            elif isinstance(arquivo_ou_buffer, (bytes, bytearray)):
                conteudo = bytes(arquivo_ou_buffer)
            elif isinstance(arquivo_ou_buffer, str):
                if os.path.exists(arquivo_ou_buffer):
                    with open(arquivo_ou_buffer, "rb") as f:
                        conteudo = f.read()
                else:
                    conteudo = arquivo_ou_buffer.encode("utf-8")
            else:
                conteudo = bytes(arquivo_ou_buffer)

            if isinstance(conteudo, bytes):
                texto = None
                for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
                    try:
                        texto = conteudo.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                if texto is None:
                    return False, None, "Não foi possível decodificar o arquivo CSV (tente codificação UTF-8)."
            else:
                texto = str(conteudo)

            buffer = io.StringIO(texto)

            # Tenta separadores vírgula e ponto-e-vírgula
            df = None
            for sep in (",", ";", "\t"):
                try:
                    if hasattr(buffer, "seek"):
                        buffer.seek(0)
                    df_tentativa = pd.read_csv(buffer, sep=sep)
                    if df_tentativa.shape[1] >= 2 and len(df_tentativa) > 0:
                        df = df_tentativa
                        break
                except Exception:
                    continue

            if df is None or len(df) == 0:
                return False, None, "Arquivo CSV vazio ou com formato ilegível."

            df_padronizado = cls.padronizar_dataframe(df, unidade_prof_entrada=unidade_prof_entrada, nome_fonte=nome_arquivo)
            if df_padronizado is None:
                return False, None, "O CSV não possui as colunas mínimas requeridas (Profundidade e ao menos um Gradiente de Poro/Fratura)."

            return True, df_padronizado, f"Perfil carregado com sucesso ({len(df_padronizado)} profundidades identificadas)."
        except Exception as e:
            logger.error(f"Falha ao processar CSV geomecânico: {e}")
            return False, None, f"Erro no processamento do arquivo: {str(e)}"

    @classmethod
    def padronizar_dataframe(cls, df: pd.DataFrame, unidade_prof_entrada: str = "m", nome_fonte: str = "Perfil") -> Optional[pd.DataFrame]:
        """
        Normaliza colunas e converte unidades para formato unificado do simulador.
        """
        df = df.copy()

        def achar_col(padroes: List[str]) -> Optional[str]:
            for p in padroes:
                for c in df.columns:
                    c_limpo = re.sub(r"[\s_()/-]+", "", str(c).lower())
                    p_limpo = re.sub(r"[\s_()/-]+", "", str(p).lower())
                    if p_limpo in c_limpo:
                        return c
            return None

        col_prof = achar_col(["profundidade", "depth", "tvd", "d (m)", "dm", "prof"])
        col_poro = achar_col(["gradiente de poros", "gradienteporos", "poros", "poro", "gp", "pore"])
        col_frac = achar_col(["gradiente de fratura", "gradientefratura", "fratura", "frac", "gf"])
        col_colap = achar_col(["gradiente de colapso", "gradientecolapso", "colapso", "collapse", "gc", "breakout"])
        col_sobre = achar_col(["gradiente de sobrecarga", "gradientesobrecarga", "sobrecarga", "overburden", "gob", "obg"])

        if not col_prof or (not col_poro and not col_frac):
            return None

        # Conversão numérica e limpeza
        def to_num(s):
            return pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce")

        prof_raw = to_num(df[col_prof])

        # Define profundidade em metros e em pés
        if unidade_prof_entrada.lower() in ("ft", "pes", "pés", "feet"):
            prof_ft = prof_raw
            prof_m = prof_raw * PES_PARA_METROS
        else:
            prof_m = prof_raw
            prof_ft = prof_raw * METROS_PARA_PES

        out = pd.DataFrame({
            "prof_m": prof_m.round(1),
            "prof_ft": prof_ft.round(1)
        })

        if col_poro:
            out["poro_ppg"] = to_num(df[col_poro]).round(2)
        else:
            out["poro_ppg"] = np.nan

        if col_frac:
            out["fratura_ppg"] = to_num(df[col_frac]).round(2)
        else:
            out["fratura_ppg"] = np.nan

        if col_colap:
            out["colapso_ppg"] = to_num(df[col_colap]).round(2)
        else:
            out["colapso_ppg"] = np.nan

        if col_sobre:
            out["sobrecarga_ppg"] = to_num(df[col_sobre]).round(2)
        else:
            out["sobrecarga_ppg"] = np.nan

        # Limite inferior: max(poro, colapso)
        out["limite_inferior_ppg"] = np.nanmax([
            out["poro_ppg"].fillna(-999).values,
            out["colapso_ppg"].fillna(-999).values
        ], axis=0)
        out["limite_inferior_ppg"] = out["limite_inferior_ppg"].replace(-999, np.nan)

        # Limite superior: min(fratura, sobrecarga)
        out["limite_superior_ppg"] = np.nanmin([
            out["fratura_ppg"].fillna(999).values,
            out["sobrecarga_ppg"].fillna(999).values
        ], axis=0)
        out["limite_superior_ppg"] = out["limite_superior_ppg"].replace(999, np.nan)

        # Largura da janela operacional
        out["largura_janela_ppg"] = (out["limite_superior_ppg"] - out["limite_inferior_ppg"]).round(2)

        # Remove linhas totalmente sem dados
        out = out.dropna(subset=["prof_m"]).sort_values("prof_m").reset_index(drop=True)
        out.attrs["nome_fonte"] = nome_fonte

        return out

    @classmethod
    def extrair_metricas_resumo(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas executivas do perfil para cards e telemetria."""
        if df is None or len(df) == 0:
            return {}

        prof_min_m = float(df["prof_m"].min())
        prof_max_m = float(df["prof_m"].max())
        prof_min_ft = float(df["prof_ft"].min())
        prof_max_ft = float(df["prof_ft"].max())

        larguras_validas = df["largura_janela_ppg"].dropna()
        largura_min = float(larguras_validas.min()) if len(larguras_validas) else 0.0
        largura_media = float(larguras_validas.mean()) if len(larguras_validas) else 0.0

        ponto_critico = {}
        if len(larguras_validas):
            idx_crit = larguras_validas.idxmin()
            lin_crit = df.loc[idx_crit]
            ponto_critico = {
                "prof_m": float(lin_crit["prof_m"]),
                "prof_ft": float(lin_crit["prof_ft"]),
                "largura_ppg": float(lin_crit["largura_janela_ppg"]),
                "poro_ppg": float(lin_crit.get("poro_ppg", 0)),
                "fratura_ppg": float(lin_crit.get("fratura_ppg", 0)),
                "colapso_ppg": float(lin_crit.get("colapso_ppg", 0))
            }

        poros_validos = df["poro_ppg"].dropna()
        fracs_validas = df["fratura_ppg"].dropna()

        return {
            "prof_min_m": prof_min_m,
            "prof_max_m": prof_max_m,
            "prof_min_ft": prof_min_ft,
            "prof_max_ft": prof_max_ft,
            "largura_min_ppg": largura_min,
            "largura_media_ppg": largura_media,
            "poro_max_ppg": float(poros_validos.max()) if len(poros_validos) else 0.0,
            "fratura_min_ppg": float(fracs_validas.min()) if len(fracs_validas) else 0.0,
            "ponto_critico": ponto_critico,
            "total_pontos": len(df),
            "nome_fonte": df.attrs.get("nome_fonte", "Perfil Ativo")
        }

    @classmethod
    def obter_metadados_poco_preset(cls, poco: str) -> Dict[str, Any]:
        """Recupera metadados adicionais do poço (TD, LDA, sapatas e lama) dos inputs do Mar do Norte."""
        inputs_dir = os.path.join(cls.ROOT_DIR, "sandbox", "janela_operacional", "inputs_codigo")
        meta = {
            "poco": poco,
            "td_m": 3200.0,
            "td_ft": 3200.0 * METROS_PARA_PES,
            "lda_m": 100.0,
            "lda_ft": 100.0 * METROS_PARA_PES,
            "sapatas": [],
            "diametro_revestimento": "9 5/8",
            "d_ext_in": 9.625,
            "d_int_in": 8.681,
            "d_broca_in": 12.250,
            "dens_lama_fundo_ppg": 10.60
        }

        # 1. Cabeçalho
        caminho_cab = os.path.join(inputs_dir, "cabecalho.csv")
        if os.path.exists(caminho_cab):
            try:
                df_cab = pd.read_csv(caminho_cab)
                r_cab = df_cab[df_cab["poço"] == poco]
                if not r_cab.empty:
                    lin = r_cab.iloc[0]
                    meta["td_m"] = float(lin.get("TD_tvd_m", lin.get("TD_md_m", 3200.0)))
                    meta["td_ft"] = meta["td_m"] * METROS_PARA_PES
                    meta["lda_m"] = float(lin.get("LDA", 100.0))
                    meta["lda_ft"] = meta["lda_m"] * METROS_PARA_PES
                    meta["campo"] = str(lin.get("campo", "Sleipner"))
            except Exception as e:
                logger.warning(f"Erro ao ler cabeçalho para {poco}: {e}")

        # 2. Sapatas / LOT
        caminho_lot = os.path.join(inputs_dir, "lot.csv")
        if os.path.exists(caminho_lot):
            try:
                df_lot = pd.read_csv(caminho_lot)
                r_lot = df_lot[df_lot["poço"] == poco]
                if not r_lot.empty:
                    meta["sapatas"] = r_lot[["tipo", "diametro", "sapata_m", "lot_ppg"]].to_dict("records")
                    # Última sapata
                    ult_sap = r_lot.iloc[-1]
                    meta["prof_ultima_sapata_m"] = float(ult_sap["sapata_m"])
                    meta["prof_ultima_sapata_ft"] = meta["prof_ultima_sapata_m"] * METROS_PARA_PES
                    diam_str = str(ult_sap.get("diametro", "9 5/8")).strip()
                    meta["diametro_revestimento"] = diam_str
                    if "9 5/8" in diam_str:
                        meta["d_ext_in"] = 9.625
                        meta["d_int_in"] = 8.681
                        meta["d_broca_in"] = 12.250
                    elif "13 3/8" in diam_str:
                        meta["d_ext_in"] = 13.375
                        meta["d_int_in"] = 12.415
                        meta["d_broca_in"] = 17.500
                    elif "7" in diam_str:
                        meta["d_ext_in"] = 7.000
                        meta["d_int_in"] = 6.094
                        meta["d_broca_in"] = 8.500
            except Exception as e:
                logger.warning(f"Erro ao ler LOT para {poco}: {e}")

        # 3. Lama de Perfuração
        caminho_lama = os.path.join(inputs_dir, "lama.csv")
        if os.path.exists(caminho_lama):
            try:
                df_lama = pd.read_csv(caminho_lama)
                r_lama = df_lama[df_lama["poço"] == poco]
                if not r_lama.empty:
                    ult_lama = r_lama.iloc[-1]
                    meta["dens_lama_fundo_ppg"] = float(ult_lama.get("lama_ppg", 10.60))
            except Exception as e:
                logger.warning(f"Erro ao ler lama para {poco}: {e}")

        return meta
