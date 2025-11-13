import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_main_dataset
from utils.metrics import label
from utils.filters import sidebar_filters

# ======= EXPANDIR A ANCHO COMPLETO (como Ranking) =======
st.markdown("""
    <style>
    /* Quita los márgenes laterales del contenido principal */
    section.main > div {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* Asegura que las columnas se expandan en todo el ancho */
    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Evita centrado forzado del contenedor principal */
    div.block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Reduce los márgenes entre widgets */
    div[data-testid="stVerticalBlock"] {
        gap: 0.7rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ===================== COMPARADOR (Radar) ===========================

df = load_main_dataset()
dff_view = sidebar_filters(df)

if len(dff_view) == 0:
    st.warning("No hay jugadores que cumplan las condiciones de filtro.")
    st.stop()

st.markdown("""
<h2 style='font-weight:700; margin-bottom:0.25rem; letter-spacing:-0.01em;'>
Comparador de jugadores - Radar Chart
</h2>
<p style='color:#9aa2ad; font-size:0.9rem; margin-bottom:1.2rem;'>
Analiza y compara el rendimiento de hasta tres jugadores en distintos aspectos del juego.
</p>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.cmp .block-container, .cmp [data-testid="stVerticalBlock"]{gap:.35rem !important}
.cmp .stRadio, .cmp .stMultiSelect, .cmp .stSelectbox, .cmp .stSlider,
.cmp .stToggleSwitch{margin: .1rem 0 .35rem 0 !important}
.cmp label{margin-bottom:.15rem !important}
.cmp .metric-note{color:#9aa2ad; font-size:.85rem; margin:.2rem 0 .6rem 0}
.cmp .stMetric{padding-top:.2rem}
</style>
""", unsafe_allow_html=True)

c = st.container()
c.markdown('<div class="cmp">', unsafe_allow_html=True)

kpi_top = c.container()
c.caption(
    '<div class="metric-note">Índice agregado (0–100): media de métricas normalizadas seleccionadas. '
    'El Δ indica cuánto está por encima/por debajo del jugador de referencia.</div>',
    unsafe_allow_html=True
)

# ===================== DETECTAR COLUMNA DE JUGADOR =====================
player_col = None
for col in dff_view.columns:
    if col.lower() in ["player", "jugador", "nombre", "name"]:
        player_col = col
        break

if not player_col:
    st.error("❌ No se encontró una columna de jugadores ('Player', 'Jugador', 'Nombre', 'Name').")
    st.stop()

# ===================== PRESETS =====================
ROLE_PRESETS = {
    "Portero":     ["save%", "psxg+/-_per90", "psxg_per90", "saves_per90", "cs%", "launch%", "prgp_per90"],
    "Central":     ["tkl+int_per90", "int_per90", "blocks_per90", "clr_per90", "recov_per90","touches_per90","err_per90"],
    "Lateral":     ["ppa_per90", "prgp_per90", "carries_per90", "tkl+int_per90", "1/3_per90","touches_per90","pressures_per90"],
    "Mediocentro": ["xa_per90", "prgp_per90", "recov_per90", "pressures_per90", "totdist_per90","prgC_per90","totdist_per90"],
    "Volante":     ["xag_per90", "kp_per90", "gca90_per90", "prgp_per90", "sca_per90","1/3_per90","sot_per90",],
    "Delantero":   ["gls_per90", "xg_per90", "npxg_per90", "sot_per90", "xa_per90","touches_per90","pressures_per90"],
}

# ===================== SELECCIÓN DE JUGADORES =====================
players_all = dff_view[player_col].dropna().unique().tolist()
pre_sel = st.session_state.get("cmp_players", [])
default_players = [p for p in pre_sel if p in players_all][:3] or players_all[:2]

sel_players = c.multiselect("Jugadores (máx. 3)", players_all, default=default_players, key="cmp_players")
if not sel_players:
    st.info("Selecciona al menos 1 jugador.")
    st.stop()
if len(sel_players) > 3:
    sel_players = sel_players[:3]

ref_player = c.selectbox("Jugador referencia", sel_players, index=0, key="cmp_ref")

# === NUEVO: para forzar actualización del multiselect ===
if "feats_key" not in st.session_state:
    st.session_state["feats_key"] = 0

col_r1, col_r2 = c.columns([0.72, 0.28])
with col_r1:
    cmp_role = st.selectbox(
        "Rol táctico (preset opcional)",
        ["— (ninguno)"] + list(ROLE_PRESETS.keys()),
        index=0,
        key="cmp_role"
    )

with col_r2:
    if cmp_role != "— (ninguno)":
        if st.button("Aplicar preset", use_container_width=True, key="cmp_role_btn"):
            # Normalizar columnas y presets a minúsculas
            cols_lower = {c.lower(): c for c in dff_view.columns}
            preset_raw = [m.lower() for m in ROLE_PRESETS[cmp_role]]
            preset_feats = [cols_lower[m] for m in preset_raw if m in cols_lower]

            if preset_feats:
                st.session_state["feats"] = preset_feats
                st.session_state["feats_key"] += 1
                st.success(f"Preset aplicado: {cmp_role} → {len(preset_feats)} métricas.")
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.warning(f"No se encontraron métricas coincidentes para el rol '{cmp_role}'.")

# ===================== MULTISELECT DE MÉTRICAS =====================
valid_feats = [
    c for c in dff_view.columns
    if c.endswith("_per90")
    or c.endswith("%")
    or "rate" in c.lower()
    or "ratio" in c.lower()
]

default_feats = st.session_state.get("feats", valid_feats[:6])

radar_feats = c.multiselect(
    "Métricas para el radar (elige 4–10)",
    options=valid_feats,
    default=[f for f in default_feats if f in valid_feats],
    key=f"feats_{st.session_state['feats_key']}",
    format_func=lambda c: label(c),
)
if len(radar_feats) < 4:
    st.info("Selecciona al menos 4 métricas para el radar.")
    st.stop()

# ===================== CONTROLES DE CONTEXTO =====================
col_ctx1, col_ctx2, col_ctx3 = c.columns([1, 1, 1.2])
ctx_mode = col_ctx1.selectbox(
    "Cálculo de percentiles",
    options=["Jugadores Seleccionados", "Por Posición", "Por Liga"],
    index=0,
    key="cmp_ctx",
)
show_baseline = col_ctx2.toggle("Mostrar baseline del grupo", value=True, key="cmp_baseline")
use_percentiles = col_ctx3.toggle("Tooltip con percentiles", value=True, key="cmp_pct_tooltip")

# ===================== FUNCIÓN DE CONTEXTO =====================
def _ctx_mask(df_in: pd.DataFrame) -> pd.Series:
    """Filtra el DataFrame según el modo de contexto seleccionado."""
    if ctx_mode == "Muestra filtrada":
        return pd.Series(True, index=df_in.index)
    if ctx_mode == "Por rol táctico" and "rol_tactico" in df_in.columns:
        if any(dff_view[player_col] == ref_player):
            rol_ref = dff_view.loc[dff_view[player_col] == ref_player, "rol_tactico"].iloc[0]
            return (df_in["rol_tactico"] == rol_ref)
    if ctx_mode == "Por competición" and "comp" in df_in.columns:
        if any(dff_view[player_col] == ref_player):
            comp_ref = dff_view.loc[dff_view[player_col] == ref_player, "comp"].iloc[0]
            return (df_in["comp"] == comp_ref)
    return pd.Series(True, index=df_in.index)

# ✅ Crear el grupo de datos según el contexto antes de la normalización
df_group = dff_view[_ctx_mask(dff_view)].copy()
if df_group.empty:
    df_group = dff_view.copy()


# ===================== NORMALIZACIÓN =====================
S_global = df[radar_feats].astype(float)
S = df_group[radar_feats].astype(float).copy()

# FIX anti-errores de alineación usando NumPy (escalares 100% seguros)
mins = S_global.min(axis=0)
maxs = S_global.max(axis=0)
ranges = (maxs - mins + 1e-9)

S_norm = (S - mins.values) / ranges.values * 100
S_norm = S_norm.clip(lower=0, upper=100)

baseline = S_norm.mean(axis=0)
pct = df_group[radar_feats].rank(pct=True) * 100 if use_percentiles else None

# ===================== KPI ARRIBA =====================
with kpi_top:
    cols_kpi = st.columns(len(sel_players))
    # ❌ antes: * 100 (duplicado)
    ref_val = S_norm[df_group[player_col] == ref_player][radar_feats].mean(axis=1).mean()
    for i, pl in enumerate(sel_players):
        val = S_norm[df_group[player_col] == pl][radar_feats].mean(axis=1).mean()
        delta = None if pl == ref_player else round(val - float(ref_val), 1)
        cols_kpi[i].metric(
            pl + (" (ref.)" if pl == ref_player else ""),
            f"{val:,.1f}",
            delta=None if delta is None else (f"{delta:+.1f}")
        )


# ===================== RADAR (MEJORADO TIPO FBREF) =====================
theta_labels = [label(f) for f in radar_feats]
fig = go.Figure()
palette = ["#4F8BF9", "#F95F53", "#2BB673"]

# 🔹 Percentiles globales (0–100)
S_perc = df[radar_feats].rank(pct=True) * 100
S_group_perc = S_perc.loc[df_group.index].copy()
player_means = (
    S_group_perc.assign(player=df_group[player_col])
    .groupby("player")[radar_feats]
    .mean()
)
baseline = player_means.mean(axis=0)

# === Añadir trazas ===
for i, pl in enumerate(sel_players):
    if pl not in player_means.index:
        continue
    r_vec = player_means.loc[pl, radar_feats].fillna(0).values
    fig.add_trace(go.Scatterpolar(
        r=r_vec,
        theta=theta_labels,
        fill='toself',
        mode='lines+markers',
        name=pl + (" (ref.)" if pl == ref_player else ""),
        line=dict(color=palette[i % len(palette)], width=2),
        marker=dict(size=5, color=palette[i % len(palette)], line=dict(width=1, color='white')),
        opacity=0.85 if pl == ref_player else 0.7,
        hovertemplate="<b>%{theta}</b><br>Percentil: %{r:.1f}<extra></extra>",
    ))


fig.update_layout(
    template="plotly_dark",
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
            gridcolor="#374151",
            linecolor="#4b5563"
        )
    ),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, x=0),
    margin=dict(l=30, r=30, t=10, b=10),
)
c.plotly_chart(fig, use_container_width=True)

# ===================== TABLA =====================
raw_group = dff_view[_ctx_mask(dff_view)].copy()
rows = {}
for pl in sel_players:
    rows[pl] = raw_group[raw_group[player_col] == pl][radar_feats].astype(float).mean()

df_cmp = pd.DataFrame({"Métrica": [label(f) for f in radar_feats]})
for pl, vals in rows.items():
    df_cmp[pl] = vals.values
for pl in sel_players:
    if pl == ref_player:
        continue
    df_cmp[f"Δ ({pl} − {ref_player})"] = df_cmp[pl] - df_cmp[ref_player]

if use_percentiles:
    pct_raw = raw_group[radar_feats].rank(pct=True)
    for pl in sel_players:
        pr = pct_raw[raw_group[player_col] == pl][radar_feats].mean(numeric_only=True) * 100
        df_cmp[f"% {pl}"] = pr.values

for ccol in df_cmp.columns:
    if ccol != "Métrica":
        df_cmp[ccol] = pd.to_numeric(df_cmp[ccol], errors="coerce").round(3)

first_delta = [c for c in df_cmp.columns if c.startswith("Δ (")]
if first_delta:
    df_cmp = df_cmp.reindex(df_cmp[first_delta[0]].abs().sort_values(ascending=False).index)

c.caption(
    '<div class="metric-note"><b>Cómo leer:</b> cada fila muestra un aspecto del juego. '
    '<b>Δ</b> = Diferencia Métrica entre jugadores · <b>%</b> = Percentil al que pertenecen en la liga.</div>',
    unsafe_allow_html=True
)
c.dataframe(df_cmp, use_container_width=True, hide_index=True)

# ===================== EXPORTAR RADAR =====================
gen = c.button("🖼️ Generar PNG del radar", key="cmp_png_btn")
if gen:
    try:
        st.session_state["radar_png"] = fig.to_image(format="png", scale=2)
        c.success("PNG generado. Ahora puedes descargarlo.")
    except Exception as e:
        c.error(f"No se pudo generar el PNG. ¿Tienes 'kaleido' instalado? Detalle: {e}")

if "radar_png" in st.session_state:
    c.download_button(
        "⬇️ Descargar radar (PNG)",
        data=st.session_state["radar_png"],
        file_name=f"radar_{'_vs_'.join(sel_players)}.png",
        mime="image/png",
        key="cmp_png_dl"
    )
