# =====================================
# utils/metrics.py
# Diccionario y helpers para etiquetas y visualización (versión FIX)
# =====================================

import pandas as pd
import numpy as np

# ======================================================
# Diccionario base: nombre_columna → etiqueta legible
# ======================================================
# 🔸 Todas las claves se pasan a minúsculas para evitar problemas con df.columns.lower()
METRIC_LABELS = {
    "player": "Jugador",
    "squad": "Equipo",
    "season": "Temporada",
    "rol_tactico": "Rol Táctico",
    "league": "Competición",
    "comp": "Competición",
    "min": "Minutos",
    "age": "Edad",
    "cmp%": "Precisión pase %",
    "save%": "Eficiencia paradas %",
    "gls_per90": "Goles /90",
    "xg_per90": "xG /90",
    "npxg_per90": "NPxG /90",
    "sh_per90": "Tiros /90",
    "sot_per90": "Tiros a puerta /90",
    "xa_per90": "xA /90",
    "kp_per90": "Pases clave /90",
    "gca90_per90": "GCA /90",
    "sca_per90": "SCA /90",
    "prgp_per90": "Pases progresivos /90",
    "prgc_per90": "Conducciones prog. /90",
    "carries_per90": "Conducciones /90",
    "tkl+int_per90": "Entradas + Intercepciones /90",
    "int_per90": "Intercepciones /90",
    "recov_per90": "Recuperaciones /90",
    "blocks_per90": "Bloqueos /90",
    "clr_per90": "Despejes /90",
    "touches_per90": "Toques /90",
    "dis_per90": "Pérdidas /90",
    "pressures_per90": "Presiones /90",
    "err_per90": "Errores /90",
    "cmp_per90": "Pases completados /90",
    "ppa_per90": "Pases al área /90",
    "totdist_per90": "Distancia total pase /90",
    "psxg+/-_per90": "PSxG +/- /90",
    "psxg_per90": "PSxG /90",
    "saves_per90": "Paradas /90",
    "cs%": "Portería a 0 %",
    "launch%": "Saques largos %",
}

# ======================================================
# Función auxiliar: devuelve la etiqueta legible + métrica técnica
# ======================================================
def label(col_name: str) -> str:
    """
    Devuelve una etiqueta legible en español + el nombre técnico entre paréntesis.
    Ejemplo: "Goles /90 (gls_per90)"
    """
    col_key = col_name.lower()
    base_label = METRIC_LABELS.get(col_key, col_key.replace("_", " ").title())

    # Evita repetir el nombre técnico si ya está formateado
    if "(" in base_label or col_key in ["player", "squad", "season", "rol_tactico", "league", "comp", "min", "age"]:
        return base_label

    return f"{base_label} ({col_key})"


# ======================================================
# Redondeo uniforme de valores numéricos
# ======================================================
def round_numeric_for_display(df: pd.DataFrame, ndigits: int = 3) -> pd.DataFrame:
    """
    Redondea todas las columnas numéricas para visualización limpia.
    """
    df_copy = df.copy()
    for c in df_copy.select_dtypes(include=[np.number]).columns:
        df_copy[c] = df_copy[c].round(ndigits)
    return df_copy


# ======================================================
# Renombrado amigable para visualización
# ======================================================
def rename_for_display(df: pd.DataFrame, cols_show: list[str]) -> pd.DataFrame:
    """
    Renombra columnas del DataFrame aplicando etiquetas legibles
    y manteniendo solo las columnas indicadas.
    """
    df_copy = df.copy()
    rename_map = {c: label(c) for c in cols_show if c in df_copy.columns}
    df_copy = df_copy.rename(columns=rename_map)
    ordered_cols = [rename_map[c] for c in cols_show if c in rename_map]
    return df_copy[ordered_cols]
