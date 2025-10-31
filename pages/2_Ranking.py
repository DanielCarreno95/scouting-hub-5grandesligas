# =====================================
# pages/2_Ranking.py | Ranking FINAL (fix columnas duplicadas)
# =====================================

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_main_dataset
from utils.metrics import label, round_numeric_for_display
from utils.filters import render_global_filters
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, GridUpdateMode, JsCode

st.set_page_config(page_title="Ranking de Jugadores - Busqueda por Rendimiento Individual", layout="wide")


# ==============================
# Cargar dataset
# ==============================
df = load_main_dataset()
if df is None or df.empty:
    st.error("No se encontró el dataset principal.")
    st.stop()

df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]
if "comp" not in df.columns and "league" in df.columns:
    df["comp"] = df["league"]

# ==============================
# Filtros globales laterales
# ==============================
df_filtered = render_global_filters(df)
if df_filtered.empty:
    st.warning("⚠️ No hay datos tras aplicar los filtros.")
    st.stop()

# ==============================
# Encabezado del módulo Ranking
# ==============================
st.markdown("""
    <style>
    /* Expande el contenido principal (como en Comparador) */
    section.main > div {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* Ajuste visual para títulos */
    h2 {
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 0.25rem !important;
    }

    .ranking-caption {
        color: #9aa2ad;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2> Ranking de Jugadores - Busqueda por Rendimiento Individual</h2>", unsafe_allow_html=True)
st.markdown(
    "<div class='ranking-caption'>Consulta y ordena el rendimiento de los jugadores según diferentes métricas clave. "
    "Filtra por liga, posición, edad o minutos para enfocar tu análisis.</div>",
    unsafe_allow_html=True
)

# ==============================
# KPIs
# ==============================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Número de Jugadores", f"{len(df_filtered):,}")
col2.metric("Equipos", f"{df_filtered['squad'].nunique():,}")
col3.metric("Edad media", f"{pd.to_numeric(df_filtered['age'], errors='coerce').mean():.1f}")
col4.metric("Avg Minutos Jugados", f"{int(pd.to_numeric(df_filtered.get('min', 0), errors='coerce').median()):,}")

st.markdown("---")

# ==============================
# Configuración superior
# ==============================
left, right = st.columns([0.75, 0.25])
with left:
    st.subheader("Modo de ranking")
    rank_mode = st.radio(
        "Selecciona el modo de análisis",
        ["Por una métrica", "Multi-métrica (ponderado)"],
        horizontal=True,
        label_visibility="collapsed",
        key="rank_mode_toggle"
    )
with right:
    st.caption("Filtro rápido por edad")
    quick_age = st.radio("", ["Todos", "U22 (≤22)", "U28 (≤28)"], horizontal=True)

df_view = df_filtered.copy()
if "age" in df_view.columns and quick_age != "Todos":
    ages = pd.to_numeric(df_view["age"], errors="coerce")
    df_view = df_view[ages <= (22 if quick_age.startswith("U22") else 28)]

if df_view.empty:
    st.warning("⚠️ No hay jugadores en este rango de edad.")
    st.stop()

st.markdown("---")

# ==============================
# Colorear columnas condicionales
# ==============================
heat_js = JsCode("""
    function(params) {
        var v = Number(params.value);
        if (isNaN(v)) return {};
        var hue = 120 * (v / 100.0);
        return {'backgroundColor': 'hsl(' + hue + ',70%,35%)', 'color':'white'};
    }
""")

# ==============================
# RANKING UNA MÉTRICA
# ==============================
if rank_mode == "Por una métrica":
    metrics = [c for c in df_view.columns if c.endswith("_per90") or c in ["cmp%", "save%"]]
    st.caption("Selecciona la métrica base")
    metric_to_rank = st.selectbox(
        "Métrica base",
        metrics,
        index=0,
        format_func=lambda x: label(x),
        key="single_metric"
    )

    order_dir = st.radio("Orden", ["Ascendente (mejor arriba)", "Descendente (peor arriba)"], horizontal=True)
    ascending = order_dir.startswith("Asc")

    # --- cálculo del ranking ---
    df_rank = df_view.copy()
    df_rank["Índice Final"] = df_rank[metric_to_rank].rank(pct=True, ascending=False) * 100  # 👈 aquí está el cambio
    df_rank = df_rank.sort_values(metric_to_rank, ascending=ascending)

    # --- columnas visibles ---
    cols_show = ["player", "squad", "season", "rol_tactico", "comp", "min", "age", metric_to_rank, "Índice Final"]
    df_disp = round_numeric_for_display(df_rank[cols_show], 3)

    df_disp.columns = [
        "Jugador", "Equipo", "Temporada", "Rol Táctico", "Competición", "Minutos", "Edad",
        f"{label(metric_to_rank)}", "Índice Final"
    ]

    # --- grid con formato condicional ---
    gb = GridOptionsBuilder.from_dataframe(df_disp)
    gb.configure_default_column(sortable=True, resizable=True, filter=True)
    gb.configure_column("Índice Final", cellStyle=heat_js)
    gb.configure_column("Jugador", pinned="left", minWidth=180)
    grid = gb.build()

    AgGrid(
        df_disp,
        gridOptions=grid,
        theme="streamlit",
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        update_mode=GridUpdateMode.NO_UPDATE,
        height=480,
        allow_unsafe_jscode=True,
        key="single_aggrid"
    )


# ==============================
# RANKING MULTI-MÉTRICA
# ==============================
else:
    metrics = [c for c in df_view.columns if c.endswith("_per90") or c in ["cmp%", "save%"]]
    st.caption("Selecciona entre 3–12 métricas para el índice compuesto")
    feats = st.multiselect(
        "Métricas a ponderar",
        metrics,
        default=metrics[:5],
        format_func=lambda x: label(x),
        key="multi_feats"
    )

    if len(feats) < 3:
        st.info("Selecciona al menos 3 métricas para continuar.")
        st.stop()

    st.markdown("Pesos de métricas")
    weights = {f: st.slider(f"{label(f)}", 0.0, 2.0, 1.0, 0.1, key=f"w_{f}") for f in feats}

    X = df_view[feats].astype(float).fillna(0)
    Xn = (X - X.min()) / (X.max() - X.min() + 1e-9)
    w = np.array([weights[f] for f in feats])
    w /= (w.sum() + 1e-9)
    idx_norm = (Xn @ w) * 100

    df_rank = df_view[["player", "squad", "season", "rol_tactico", "comp", "min", "age"]].copy()
    df_rank["Índice Final"] = idx_norm

    # Añadir métricas ponderadas
    for m in feats:
        df_rank[f"{label(m)}"] = (df_view[m] * weights[m]).round(3)

    df_rank = df_rank.sort_values("Índice Final", ascending=False)

    cols_show = ["player", "squad", "season", "rol_tactico", "comp", "min", "age"] + [f"{label(m)}" for m in feats] + ["Índice Final"]
    df_disp = round_numeric_for_display(df_rank[cols_show], 3)
    df_disp.columns = ["Jugador", "Equipo", "Temporada", "Rol Táctico", "Competición", "Minutos", "Edad"] + [f"{label(m)}" for m in feats] + ["Índice Final"]

    gb = GridOptionsBuilder.from_dataframe(df_disp)
    gb.configure_default_column(sortable=True, resizable=True, filter=True)
    gb.configure_column("Índice Final", cellStyle=heat_js)
    gb.configure_column("Jugador", pinned="left", minWidth=180)
    grid = gb.build()

    AgGrid(
        df_disp,
        gridOptions=grid,
        theme="streamlit",
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        update_mode=GridUpdateMode.NO_UPDATE,
        height=480,
        allow_unsafe_jscode=True,
        key="multi_aggrid"
    )

# ==============================
# BOTONES
# ==============================
st.markdown("---")
colb1, colb2 = st.columns([0.5, 0.5])
with colb1:
    if st.button("Limpiar filtros", use_container_width=True):
        st.session_state.clear()
        st.rerun()
with colb2:
    st.download_button(
        "📥 Exportar CSV",
        data=df_view.to_csv(index=False).encode("utf-8-sig"),
        file_name="ranking_jugadores.csv",
        mime="text/csv",
        use_container_width=True
    )
