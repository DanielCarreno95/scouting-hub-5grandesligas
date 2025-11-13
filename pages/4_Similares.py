# =====================================
# pages/4_Similares.py | Jugadores Similares (versión final pulida)
# =====================================

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_main_dataset
from utils.metrics import label, round_numeric_for_display
from utils.filters import sidebar_filters
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, GridUpdateMode, JsCode

# ======= CONFIGURACIÓN BASE =======
st.set_page_config(page_title="Jugadores similares", layout="wide")

# ======= ESTILO ANCHO COMPLETO =======
st.markdown("""
    <style>
    section.main > div {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    div[data-testid="column"] { flex: 1 1 100% !important; }
    div.block-container { max-width: 100% !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0.7rem !important; }
    .stSelectbox, .stMultiSelect, .stRadio, .stSlider, .stCheckbox,
    .stNumberInput, .stTextInput { margin:.2rem 0 !important; }
    .kpi-row .stMetric { text-align:center; }
    </style>
""", unsafe_allow_html=True)

# ======= ENCABEZADO ESTILO UNIFICADO (como Comparador) =======
st.markdown("""
<h2 style='font-weight:700; margin-bottom:0.25rem; letter-spacing:-0.01em;'>
Jugadores Similares — Detección de Perfiles Comparables
</h2>
<p style='color:#9aa2ad; font-size:0.9rem; margin-bottom:1.2rem;'>
Identifica jugadores con características de rendimiento y rol táctico similares.
Analiza sustitutos naturales o talentos con patrones estadísticos equivalentes.
</p>
""", unsafe_allow_html=True)

# ======= CARGA DE DATOS =======
df = load_main_dataset()
dff_view = sidebar_filters(df)
if dff_view.empty:
    st.warning("No hay jugadores que cumplan las condiciones de filtro.")
    st.stop()

df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
if "comp" not in df.columns and "league" in df.columns:
    df["comp"] = df["league"]

# ======= KPIs DEL UNIVERSO (AL INICIO, estilo Ranking) =======
st.markdown("---")

# Calcular métricas base
num_players = len(dff_view)
num_teams = dff_view["squad"].nunique() if "squad" in dff_view.columns else "—"
avg_age = pd.to_numeric(dff_view.get("age", pd.Series(dtype=float)), errors="coerce").mean()
avg_minutes = pd.to_numeric(dff_view.get("min", pd.Series(dtype=float)), errors="coerce").mean()

# Mostrar en 4 columnas
k1, k2, k3, k4 = st.columns(4)
k1.metric("Número de Jugadores", f"{num_players:,}")
k2.metric("Equipos", f"{num_teams:,}")
k3.metric("Edad media", f"{avg_age:.1f}" if not np.isnan(avg_age) else "—")
k4.metric("Avg Minutos Jugados", f"{avg_minutes:.0f}" if not np.isnan(avg_minutes) else "—")


# ======= PRESETS DE ROLES (ampliados y robustos) =======
ROLE_PRESETS = {
    "Portero": ["save%", "psxg+/-_per90", "psxg_per90", "saves_per90", "cs%", "launch%", "prgp_per90"],
    "Central": ["tkl+int_per90", "int_per90", "blocks_per90", "clr_per90", "recov_per90","touches_per90","err_per90"],
    "Lateral": ["ppa_per90", "prgp_per90", "carries_per90", "tkl+int_per90", "1/3_per90","touches_per90","pressures_per90"],
    "Mediocentro":  ["xa_per90", "prgp_per90", "recov_per90", "pressures_per90", "totdist_per90","prgC_per90","totdist_per90"],
    "Volante": ["xag_per90", "kp_per90", "gca90_per90", "prgp_per90", "sca_per90","1/3_per90","sot_per90",],
    "Delantero":  ["gls_per90", "xg_per90", "npxg_per90", "sot_per90", "xa_per90","touches_per90","pressures_per90"],
}

# ======= SELECCIÓN DE JUGADOR =======
players_all = sorted(dff_view["player"].dropna().unique().tolist())
ref_player = st.selectbox(
    "Selecciona el jugador de referencia",
    options=players_all,
    index=0,
    placeholder="Empieza a escribir un nombre (Ej.: Nico Williams)"
)

from uuid import uuid4

# ===================== SELECCIÓN DE PRESETS Y MÉTRICAS =====================
col1, col2 = st.columns([0.7, 0.3])
with col1:
    preset_sel = st.selectbox(
        "Rol táctico (para cargar métricas predefinidas)",
        ["— (manual)"] + list(ROLE_PRESETS.keys()), index=0
    )

with col2:
    if st.button("Aplicar preset", use_container_width=True):
        cols_lower_map = {c.lower(): c for c in dff_view.columns}

        preset_feats = []
        for m in ROLE_PRESETS.get(preset_sel, []):
            m_low = m.lower()
            if m_low in cols_lower_map:
                preset_feats.append(cols_lower_map[m_low])
                continue
            match = next(
                (orig for low, orig in cols_lower_map.items() if m_low in low or low in m_low),
                None
            )
            if match:
                preset_feats.append(match)

        st.session_state["sim_feats"] = preset_feats
        st.session_state["sim_feats_uuid"] = uuid4().hex  # 🔥 FORZAR NUEVA MATRIZ DE KEYS
        st.success(f"Métricas cargadas: {preset_sel} → {len(preset_feats)} métricas.")
        st.rerun()

metric_pool = [
    c for c in dff_view.columns
    if (c.endswith("_per90") or c.endswith("%") or "rate" in c.lower() or "ratio" in c.lower())
]

default_feats = st.session_state.get("sim_feats", ROLE_PRESETS.get(preset_sel, []))
default_feats = [f for f in default_feats if f in metric_pool]

if len(default_feats) < 6:
    default_feats = metric_pool[:8]

feats = st.multiselect(
    "Selecciona las métricas del perfil (6–12 recomendadas)",
    options=metric_pool,
    default=default_feats,
    format_func=lambda c: label(c)
)

if len(feats) < 6:
    st.info("El perfil necesita al menos 6 métricas para comparar correctamente.")
    st.stop()

from uuid import uuid4

# --- manejar UUID estable por sesión ---
if "sim_session_uuid" not in st.session_state:
    st.session_state["sim_session_uuid"] = uuid4().hex

base_uuid = st.session_state["sim_session_uuid"]

# --- generar weights sin dict comprehension (solución definitiva) ---
weights = {}
with st.expander("Ajusta la importancia de cada métrica (0.0–2.0)", expanded=True):
    for f in feats:
        # key 100% único, estable, sin colisiones
        key = f"sim_w_{preset_sel}_{f}_{base_uuid}"

        weights[f] = st.slider(
            label(f),
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key=key
        )

# ======= CONSTRUCCIÓN Y NORMALIZACIÓN =======
pool = dff_view.copy()
feats = [f for f in feats if f in pool.columns]
X_raw = pool[feats].astype(float).copy()
Xn = (X_raw - X_raw.min()) / (X_raw.max() - X_raw.min() + 1e-9)
Xn = Xn.fillna(0.0)

w = np.array([weights[f] for f in feats], dtype=float)
w = w / (w.sum() + 1e-9)

if any(pool["player"] == ref_player):
    v = Xn[pool["player"] == ref_player].mean(axis=0).to_numpy()
    pool_no_ref = pool[pool["player"] != ref_player].copy()
    X_no_ref = Xn.loc[pool_no_ref.index].copy()
else:
    st.warning("El jugador objetivo no está en el universo actual.")
    st.stop()

v_w = v * w
V_unit = v_w / (np.linalg.norm(v_w) + 1e-12)
U = X_no_ref.to_numpy() * w
U_unit = U / (np.linalg.norm(U, axis=1, keepdims=True) + 1e-12)
sim = (U_unit @ V_unit)

# ======= RESULTADOS =======
st.subheader("Jugadores más similares")

# Contenedor dividido: tabla + fortalezas
col_left, col_right = st.columns([0.65, 0.35], gap="large")

# -------------------------- #
# IZQUIERDA: TABLA DE RESULTADOS (con métricas seleccionadas)
# -------------------------- #
with col_left:
    # Definimos columnas base que existan en el dataset
    cols_id = [c for c in ["player", "squad", "season", "rol_tactico", "comp", "min", "age"] if c in pool.columns]

    # Añadimos dinámicamente las métricas seleccionadas
    cols_show = cols_id + feats + ["parecido"]

    # Creamos el dataframe final
    out = pool_no_ref.copy()
    out["parecido"] = sim
    out = out.sort_values("parecido", ascending=False).head(25)
    out = out[cols_show].copy()

    # Renombramos la columna principal
    out.rename(columns={"player": "Jugador"}, inplace=True)

    # Redondeamos métricas numéricas
    disp = round_numeric_for_display(out, ndigits=3)

    # ==== CONFIGURACIÓN DE AGGRID ====
    gb = GridOptionsBuilder.from_dataframe(disp)
    gb.configure_default_column(sortable=True, filter=True, resizable=True, floatingFilter=True)
    gb.configure_column("Jugador", pinned="left", minWidth=230, tooltipField="Jugador")

    # === FORMATO CONDICIONAL (heatmap para métricas y parecido) ===
    heat_js = JsCode("""
        function(params){
            var v = Number(params.value);
            if(isNaN(v)) return {};
            v = Math.max(0, Math.min(1.0, v));
            var hue = 120 * v;
            return {'backgroundColor':'hsl(' + hue + ',65%,25%)','color':'white'};
        }
    """)

    # Aplicamos estilo condicional a cada métrica y al índice de parecido
    for col in feats + ["parecido"]:
        if col in disp.columns:
            gb.configure_column(col, cellStyle=heat_js, minWidth=110)

    # === RENDERIZAR TABLA ===
    AgGrid(
        disp,
        gridOptions=gb.build(),
        theme="streamlit",
        update_mode=GridUpdateMode.NO_UPDATE,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=500,
        allow_unsafe_jscode=True
    )

    # === DESCARGA CSV ===
    st.download_button(
        "⬇️ Descargar lista (CSV)",
        data=out.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"similares_{ref_player}.csv",
        mime="text/csv"
    )


# -------------------------- #
# DERECHA: FORTALEZAS / ÁREAS DE MEJORA
# -------------------------- #
with col_right:
    st.markdown(f"### Perfil de {ref_player}")
    mask_ref = (pool["player"] == ref_player)
    if mask_ref.any():
        S = pool[feats].astype(float)
        pcts = S.rank(pct=True)
        ref_pct = pcts[mask_ref].mean().sort_values(ascending=False)
        strengths = ref_pct.head(5)
        needs = ref_pct.tail(5)

        cA, cB = st.columns(2)
        with cA:
            st.markdown("**Fortalezas**")
            for k, v_ in strengths.items():
                st.write(f"• {label(k)} — {v_*100:.0f}º pct")
        with cB:
            st.markdown("**Áreas de mejora**")
            for k, v_ in needs.items():
                st.write(f"• {label(k)} — {v_*100:.0f}º pct")
    else:
        st.info("El jugador de referencia no se encuentra en el universo actual.")
