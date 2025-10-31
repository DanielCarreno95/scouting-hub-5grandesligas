# =======================================
# pages/1_Overview.py | Overview FINAL DEFINITIVO
# =======================================

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_main_dataset
from utils.metrics import METRIC_LABELS
from utils.filters import sidebar_filters   # ✅ AÑADE ESTA LÍNEA

st.set_page_config(page_title="Scouting Hub — Visión Global del Rendimiento", layout="wide")

PALETTE = ["#1E3A8A", "#2563EB", "#10B981", "#F59E0B", "#EF4444", "#6B7280"]

st.title("Scouting Hub — Visión Global del Rendimiento")
st.caption("Análisis macro de jugadores — tendencias, roles y estructuras competitivas.")

# ==============================
# CARGA DE DATOS
# ==============================
df = load_main_dataset()
if df is None or df.empty:
    st.error("No se pudo cargar el dataset principal.")
    st.stop()

df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

# ==============================
# FILTROS LATERALES (centralizados)
# ==============================
f = sidebar_filters(df)


# ==============================
# BLOQUE 1: CURVA DE MADUREZ COMPETITIVA
# ==============================
st.subheader("Curva de madurez competitiva por rol táctico")
st.caption("Relación entre la edad media y los minutos jugados por posición. Indica a qué edad los jugadores alcanzan mayor carga competitiva.")

curve_df = (
    f.groupby(["rol_tactico", "age"], as_index=False)["min"]
    .mean()
    .dropna()
)

fig_curve = px.line(
    curve_df,
    x="age",
    y="min",
    color="rol_tactico",
    color_discrete_sequence=PALETTE,
    template="plotly_dark",
)
fig_curve.update_layout(
    height=400,
    xaxis_title="Edad",
    yaxis_title="Minutos promedio por jugador",
    legend_title="Rol táctico",
)
st.plotly_chart(fig_curve, use_container_width=True)

st.markdown(
    "_Interpretación:_ los picos de cada curva reflejan la edad de máxima participación. "
    "Por ejemplo, los delanteros suelen alcanzar su pico competitivo antes que los centrales."
)

st.markdown("---")

# ==============================
# BLOQUE 2: DISTRIBUCIÓN TÁCTICA POR COMPETICIÓN
# ==============================
st.subheader("Distribución táctica por competición")
st.caption("Proporción de jugadores por rol en cada liga. Permite comparar estructuras tácticas y estilos de competición.")

dist_df = (
    f.groupby(["league", "rol_tactico"])
    .size()
    .reset_index(name="jugadores")
)
total_league = dist_df.groupby("league")["jugadores"].sum().reset_index(name="total")
dist_df = dist_df.merge(total_league, on="league")
dist_df["pct"] = dist_df["jugadores"] / dist_df["total"]

fig_dist = px.bar(
    dist_df,
    x="pct",
    y="league",
    color="rol_tactico",
    orientation="h",
    color_discrete_sequence=PALETTE,
    template="plotly_dark",
    text=dist_df["jugadores"],
)
fig_dist.update_layout(
    height=450,
    xaxis_title="Proporción de jugadores",
    yaxis_title="Competición",
    legend_title="Rol táctico",
)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown(
    "_Insight:_ Ligas con mayor equilibrio posicional suelen tener una estructura más flexible y competitiva, "
    "mientras que aquellas concentradas en ciertos roles reflejan estilos tácticos dominantes."
)

st.markdown("---")

# ==============================
# BLOQUE 3: EXPLORADOR DE MÉTRICAS
# ==============================
st.subheader("Explorador de métricas de rendimiento")
st.caption("Selecciona dos métricas para analizar su relación. Cada punto representa un jugador, coloreado por su rol táctico.")

metric_pool = [c for c in df.columns if c.endswith("_per90") or c in ["cmp%", "save%", "xg", "xa"]]

colx, coly = st.columns(2)
with colx:
    x_metric = st.selectbox(
        "Eje X",
        metric_pool,
        index=metric_pool.index("gls_per90") if "gls_per90" in metric_pool else 0,
        format_func=lambda x: METRIC_LABELS.get(x, x)
    )
with coly:
    y_metric = st.selectbox(
        "Eje Y",
        metric_pool,
        index=metric_pool.index("xg_per90") if "xg_per90" in metric_pool else 1,
        format_func=lambda x: METRIC_LABELS.get(x, x)
    )

fig_scatter = px.scatter(
    f,
    x=x_metric,
    y=y_metric,
    color="rol_tactico",
    size="min",
    hover_name="player",
    color_discrete_sequence=PALETTE,
    template="plotly_dark",
)
fig_scatter.update_layout(
    height=450,
    xaxis_title=METRIC_LABELS.get(x_metric, x_metric),
    yaxis_title=METRIC_LABELS.get(y_metric, y_metric),
    legend_title="Rol táctico",
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown(
    "_Ejemplo:_ una relación positiva entre `xG/90` y `SoT/90` sugiere que los jugadores más "
    "activos en el área tienden también a generar más oportunidades de gol."
)

st.markdown("---")

# ==============================
# BLOQUE 4: PERFIL MEDIO POR EQUIPO
# ==============================
st.subheader("Perfil medio por equipo")
st.caption(
    "Compara el perfil medio por equipo. Selecciona hasta tres métricas (ofensivas, creación, progresión o defensa). "
    "El orden siempre es de mayor a menor en el promedio de las métricas elegidas."
)

# --- Defaults
DEFAULT_METRICS_TEAM = ["xg_per90"]
DEFAULT_TOPN_TEAM = 10

# --- Estado inicial seguro ---
if "metrics_team" not in st.session_state:
    st.session_state["metrics_team"] = DEFAULT_METRICS_TEAM.copy()
if "top_n_team" not in st.session_state:
    st.session_state["top_n_team"] = DEFAULT_TOPN_TEAM

# --- Función de reseteo ---
def _reset_team_filters():
    st.session_state["metrics_team"] = DEFAULT_METRICS_TEAM.copy()
    st.session_state["top_n_team"] = DEFAULT_TOPN_TEAM

# --- Botón reset ---
st.button("Borrar filtros de equipo", on_click=_reset_team_filters)

# --- Selector de métricas ---
metrics_team = st.multiselect(
    "Selecciona métricas (máximo 3)",
    metric_pool,
    key="metrics_team",
    max_selections=3,
    format_func=lambda x: METRIC_LABELS.get(x, x),
)

# --- Slider sin conflicto de SessionState ---
top_n_teams = st.slider(
    "Número de equipos a mostrar (Top N)",
    min_value=5,
    max_value=30,
    key="top_n_team",  # no pasamos 'value' → evita el warning
)

# --- Garantía de valores por defecto ---
if not metrics_team:
    metrics_team = DEFAULT_METRICS_TEAM.copy()
    st.session_state["metrics_team"] = metrics_team

# --- Cálculo de ranking (mayor a menor) ---
team_avg = (
    f.groupby("squad")[metrics_team]
    .mean(numeric_only=True)
    .dropna()
    .reset_index()
)

# Promedio conjunto de métricas seleccionadas
team_avg["__orden__"] = team_avg[metrics_team].mean(axis=1)
team_avg = team_avg.sort_values("__orden__", ascending=False)

# Top N equipos
top_squads_ordered = team_avg["squad"].head(top_n_teams).tolist()

# Pasar a formato largo (long)
long_team = (
    team_avg.melt(id_vars=["squad", "__orden__"], var_name="métrica", value_name="valor")
    .query("squad in @top_squads_ordered")
)
long_team["squad"] = pd.Categorical(long_team["squad"], categories=top_squads_ordered, ordered=True)

# --- Visualización ---
fig_team = px.bar(
    long_team,
    x="valor",
    y="squad",
    color="métrica",
    barmode="group",
    color_discrete_sequence=PALETTE,
    template="plotly_dark",
)
fig_team.update_layout(
    height=460,
    xaxis_title="Valor promedio",
    yaxis_title="Equipo",
    legend_title="Métrica",
)
fig_team.update_yaxes(autorange="reversed")  # Mejor equipo arriba

st.plotly_chart(fig_team, use_container_width=True)

st.markdown(
    "_Lectura_: el orden refleja el promedio conjunto de las métricas seleccionadas. Sirve para comparar estilos colectivos; "
    "por ejemplo, equipos con alto xG/90 y xA/90 dominan creación y finalización."
)
st.markdown("---")

# ==============================
# BLOQUE 5: EVOLUCIÓN TÁCTICA POR EQUIPO
# ==============================
st.subheader("Evolución táctica por equipo")
st.caption(
    "Analiza la progresión temporal de hasta cuatro métricas por equipo. "
    "El Top N se calcula por el promedio de las métricas seleccionadas a lo largo del periodo."
)

# --- Defaults ---
DEFAULT_METRICS_EVOL = ["xg_per90"]
DEFAULT_TOPN_EVOL = 3  # empieza en 3 como pediste

# --- Inicializar estado si no existe ---
if "metrics_evol" not in st.session_state:
    st.session_state["metrics_evol"] = DEFAULT_METRICS_EVOL.copy()
if "top_n_evol" not in st.session_state:
    st.session_state["top_n_evol"] = DEFAULT_TOPN_EVOL

# --- Función de reseteo ---
def _reset_evol_filters():
    st.session_state["metrics_evol"] = DEFAULT_METRICS_EVOL.copy()
    st.session_state["top_n_evol"] = DEFAULT_TOPN_EVOL

# --- Botón reset ---
st.button("Borrar filtros de evolución", on_click=_reset_evol_filters)

# --- Multiselect controlado SIN default ---
metrics_selected = st.multiselect(
    "Selecciona métricas (máximo 4)",
    metric_pool,
    key="metrics_evol",
    max_selections=4,
    format_func=lambda x: METRIC_LABELS.get(x, x),
)

# --- Slider controlado SIN value ---
top_n_evol = st.slider(
    "Número de equipos a mostrar (Top N)",
    min_value=3,
    max_value=10,
    key="top_n_evol",
)

# --- Garantizar al menos 1 métrica ---
if not metrics_selected:
    metrics_selected = DEFAULT_METRICS_EVOL.copy()
    st.session_state["metrics_evol"] = metrics_selected

# --- Serie temporal por equipo ---
if "season" in f.columns and metrics_selected:
    # Calcular score promedio para top N equipos
    score_by_team = f.groupby("squad")[metrics_selected].mean(numeric_only=True).mean(axis=1)
    top_teams = score_by_team.sort_values(ascending=False).head(st.session_state["top_n_evol"]).index.tolist()

    long_evol = (
        f[f["squad"].isin(top_teams)]
        .groupby(["season", "squad"])[metrics_selected]
        .mean(numeric_only=True)
        .reset_index()
        .melt(id_vars=["season", "squad"], var_name="métrica", value_name="valor")
        .dropna()
    )

    long_evol["squad"] = pd.Categorical(long_evol["squad"], categories=top_teams, ordered=True)

    # --- Gráfico de barras verticales ---
import plotly.express as px

fig_evol = px.bar(
    long_evol,
    x="season",
    y="valor",
    color="squad",
    facet_col="métrica",
    facet_col_wrap=2,
    barmode="group",  # Barras agrupadas (no apiladas)
    color_discrete_sequence=PALETTE,
    template="plotly_dark",
)

# --- Ajustes estéticos ---
fig_evol.update_layout(
    height=520 + 80 * max(0, len(metrics_selected) - 2),
    xaxis_title="Temporada",
    yaxis_title="Valor medio",
    legend_title="Equipo",
    bargap=0.25,  # separación entre barras
    bargroupgap=0.15,  # separación entre grupos
)

# Mejorar legibilidad de etiquetas
fig_evol.update_xaxes(type="category", tickangle=-30)

st.plotly_chart(fig_evol, use_container_width=True)

# ==============================
# 📄 Exportar infografía (1 página grande, Hero + 2×2)
# ==============================
import io
from datetime import datetime
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import streamlit as st

# ---- Tamaño de página personalizado (GRANDE) ----
# 1 punto = 1/72 inch. Estos tamaños dan una página amplia y nítida.
PAGE_W, PAGE_H = 2400, 1600   # puedes subir/bajar si lo prefieres

def _png_for_pdf(
    fig,
    w, h,                # ← exportamos exactamente al tamaño de la celda
    scale=3,             # ↑ nitidez. Si pesa mucho, baja a 2
    base=18, tick=16, axis_title=18, legend=16, title=24
):
    """
    Exporta una copia de la figura con tipografías grandes y líneas/markers más gruesos,
    renderizada al tamaño real al que se imprimirá en el PDF (w×h).
    """
    fe = go.Figure(fig)  # copia segura
    fe.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0B0F17",
        plot_bgcolor="#0B0F17",
        font=dict(color="#F3F4F6", size=base),
        width=int(w),
        height=int(h),
        margin=dict(l=56, r=56, t=64, b=56),
        legend=dict(font=dict(size=legend)),
        title=dict(font=dict(size=title))
    )
    # Aumentar tipografías en todos los ejes (incluye facetas)
    for k in fe.layout:
        if k.startswith("xaxis") or k.startswith("yaxis"):
            ax = getattr(fe.layout, k)
            if ax:
                ax.update(tickfont=dict(size=tick), title_font=dict(size=axis_title))
    # Engrosar líneas / markers
    for tr in fe.data:
        if hasattr(tr, "line") and tr.line is not None:
            lw = getattr(tr.line, "width", 1) or 1
            tr.update(line=dict(width=max(lw, 2.2)))
        if hasattr(tr, "marker") and tr.marker is not None and hasattr(tr.marker, "size"):
            try:
                if isinstance(tr.marker.size, (int, float)):
                    tr.update(marker=dict(size=max(tr.marker.size, 9)))
            except Exception:
                pass
        if hasattr(tr, "textfont") and tr.textfont is not None:
            tf = getattr(tr.textfont, "size", 12) or 12
            tr.update(textfont=dict(size=max(tf, 14)))

    fe.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
    return fe.to_image(format="png", scale=scale)  # requiere kaleido

def build_infographic_pdf_5(
    hero, tl, tr, bl, br,
    title="Scouting Hub — Data Performance Summary",
    subtitle="Análisis integral de rendimiento y evolución táctica",
):
    """
    Maquetación en una sola página GRANDE:
      - Hero (ancho completo arriba)
      - 2×2 abajo con separación homogénea
    """
    buf = io.BytesIO()

    # Márgenes y rejilla
    M   = 50                 # margen exterior
    HDR = 110                # cabecera (título + subtítulo)
    GUT = 26                 # separación entre elementos

    W, H = PAGE_W, PAGE_H

    # Área de contenido
    content_w = W - 2*M
    content_h = H - HDR - M

    # Distribución: hero ~44% + rejilla 2×2
    hero_h = content_h * 0.44
    grid_h = content_h - hero_h - GUT
    cell_w = (content_w - GUT) / 2
    cell_h = (grid_h - GUT) / 2

    # Canvas
    c = canvas.Canvas(buf, pagesize=(W, H))
    BG = HexColor("#0B0F17")
    FG = HexColor("#F3F4F6")
    MUTED = HexColor("#9AA2AD")

    # Fondo negro
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Cabecera
    c.setFillColor(FG)
    c.setFont("Helvetica-Bold", 38)
    c.drawString(M, H - M - 8, title)

    c.setFont("Helvetica", 18)
    c.setFillColor(MUTED)
    c.drawString(M, H - M - 8 - 30, subtitle)

    # Fecha (solo día/mes/año)
    c.setFont("Helvetica", 14)
    c.drawRightString(W - M, H - M - 8, datetime.now().strftime("%d/%m/%Y"))

    # Posiciones
    x_hero = M
    y_hero = H - M - HDR - hero_h

    x_tl = M
    y_tl = y_hero - GUT - cell_h

    x_tr = M + cell_w + GUT
    y_tr = y_tl

    x_bl = M
    y_bl = y_tl - GUT - cell_h

    x_br = x_tr
    y_br = y_bl

    # Pintado (centrando y preservando AR)
    def _draw(img_bytes, x, y, w, h):
        if not img_bytes:
            return
        img = ImageReader(io.BytesIO(img_bytes))
        c.drawImage(
            img, x, y, width=w, height=h, mask='auto',
            preserveAspectRatio=True, anchor='c'
        )

    _draw(hero, x_hero, y_hero, content_w, hero_h)
    _draw(tl,   x_tl,  y_tl,   cell_w,    cell_h)
    _draw(tr,   x_tr,  y_tr,   cell_w,    cell_h)
    _draw(bl,   x_bl,  y_bl,   cell_w,    cell_h)
    _draw(br,   x_br,  y_br,   cell_w,    cell_h)

    c.showPage()
    c.save()
    return buf.getvalue()

# ---- Botón de descarga (5 figuras ya creadas en la página) ----
# Asegúrate de tener: fig_scatter, fig_curve, fig_dist, fig_team, fig_evol
if st.button("📄 Descargar infografía (1 página, 5 gráficas — alta definición)"):
    try:
        # Calculamos tamaños EXACTOS según la rejilla para exportar cada figura
        M, HDR, GUT = 50, 110, 26
        W, H = PAGE_W, PAGE_H
        content_w = W - 2*M
        content_h = H - HDR - M
        hero_h = content_h * 0.44
        grid_h = content_h - hero_h - GUT
        cell_w = (content_w - GUT) / 2
        cell_h = (grid_h - GUT) / 2

        # Exportación nítida al tamaño real de impresión
        PNG_KW = dict(scale=3, base=18, tick=16, axis_title=18, legend=16, title=24)
        imgs = {
            "hero": _png_for_pdf(fig_scatter, w=content_w, h=hero_h, **PNG_KW),
            "tl":   _png_for_pdf(fig_curve,   w=cell_w,    h=cell_h,  **PNG_KW),
            "tr":   _png_for_pdf(fig_dist,    w=cell_w,    h=cell_h,  **PNG_KW),
            "bl":   _png_for_pdf(fig_team,    w=cell_w,    h=cell_h,  **PNG_KW),
            "br":   _png_for_pdf(fig_evol,    w=cell_w,    h=cell_h,  **PNG_KW),
        }

        pdf_bytes = build_infographic_pdf_5(
            hero=imgs["hero"],
            tl=imgs["tl"], tr=imgs["tr"],
            bl=imgs["bl"], br=imgs["br"],
            title="SCOUTING HUB — Informe de Rendimiento",
            subtitle="Temporada 2024/25 · 5 Grandes Ligas"
        )

        st.download_button(
            "⬇️ Descargar PDF",
            data=pdf_bytes,
            file_name=f"Infografia_Scouting_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(
            f"❌ No se pudo generar el PDF: {e}\n"
            f"Sugerencia: confirma que 'kaleido' y 'reportlab' están instalados."
        )
