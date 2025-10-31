# ============================================
# pages/5_Shortlist.py | Shortlist FINAL DEFINITIVO (OK)
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_main_dataset
from utils.metrics import METRIC_LABELS

st.set_page_config(page_title="Shortlist de Jugadores - Lista de Seguimiento y Evaluación", layout="wide")

# ==============================
# Cargar dataset
# ==============================
df = load_main_dataset()
if df is None or df.empty:
    st.error("❌ No se encontró el dataset principal.")
    st.stop()

dff_view = df.copy()
dff_view.columns = [c.strip().replace(" ", "_").lower() for c in dff_view.columns]

if "comp" not in dff_view.columns:
    if "league" in dff_view.columns:
        dff_view["comp"] = dff_view["league"]
    else:
        dff_view["comp"] = "Desconocida"

# ==============================
# ENCABEZADO ESTILO UNIFICADO
# ==============================
st.markdown("""
<h2 style='font-weight:700; margin-bottom:0.25rem; letter-spacing:-0.01em;'>
Shortlist de Jugadores — Lista de Seguimiento y Evaluación
</h2>
<p style='color:#9aa2ad; font-size:0.9rem; margin-bottom:1.2rem;'>
Administra el seguimiento, evaluación y priorización de jugadores detectados en el proceso de scouting.
Actualiza estados, define próximas acciones y centraliza la información clave de cada perfil.
</p>
""", unsafe_allow_html=True)

# ==============================
# BOTÓN DE CIERRE DE SESIÓN (solo)
# ==============================
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar sesión"):
    # Limpiar toda la sesión actual
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Marcar estado de autenticación como falso
    st.session_state["auth"] = False
    st.session_state["page"] = "login"

    st.success("Sesión cerrada correctamente. Redirigiendo al inicio...")

    # Redirigir a la pantalla principal de login (app.py)
    st.switch_page("app.py")

# ==============================
# Configuración base
# ==============================
base_cols = ["player", "squad", "season", "rol_tactico", "comp", "min", "age"]
meta_cols = ["estado", "prioridad", "tags", "notas", "prox_accion", "estim_fee", "origen"]
core_cols = base_cols + meta_cols
estado_opts = ["Observado", "Seguimiento", "Candidato", "No procede"]

if "shortlist_df" not in st.session_state:
    st.session_state.shortlist_df = pd.DataFrame(columns=core_cols)

# 🔹 Mantiene exactamente las mismas funcionalidades que antes

# ==============================
# KPIs superiores
# ==============================
shdf = st.session_state.shortlist_df.copy()
def _c(est): return int((shdf["estado"] == est).sum()) if len(shdf) else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Observados", f"{_c('Observado'):,}")
k2.metric("En seguimiento", f"{_c('Seguimiento'):,}")
k3.metric("Candidatos", f"{_c('Candidato'):,}")
k4.metric("No procede", f"{_c('No procede'):,}")
try:
    k5.metric("Edad media", f"{pd.to_numeric(shdf['age'], errors='coerce').mean():.1f}" if len(shdf) else "—")
except Exception:
    k5.metric("Edad media", "—")

st.markdown("<hr style='opacity:.15;margin:.35rem 0;'>", unsafe_allow_html=True)

# ==============================
# 🔹 Funciones auxiliares
# ==============================
def _reset_form_values():
    """Reinicia los valores del formulario a su estado inicial."""
    st.session_state["sh_add_sel"] = []
    st.session_state["sh_add_estado"] = estado_opts[0]
    st.session_state["sh_add_prior"] = "B"
    st.session_state["sh_add_tags"] = ""
    st.session_state["sh_add_notas"] = ""
    st.session_state["sh_add_fee"] = ""
    st.session_state["sh_add_date"] = None

def add_to_shortlist():
    """Añade jugador a shortlist y limpia el formulario."""
    add_sel   = st.session_state.get("sh_add_sel", [])
    add_estado= st.session_state.get("sh_add_estado", estado_opts[0])
    add_prior = st.session_state.get("sh_add_prior", "B")
    add_tags  = st.session_state.get("sh_add_tags", "")
    add_notas = st.session_state.get("sh_add_notas", "")
    add_fee   = st.session_state.get("sh_add_fee", "")
    add_date  = st.session_state.get("sh_add_date", None)

    if not add_sel:
        st.warning("Selecciona al menos un jugador.")
        return

    take = dff_view[dff_view["player"].isin(add_sel)][base_cols].drop_duplicates(
        subset=["player", "squad", "season"]
    ).copy()

    if take.empty:
        st.info("No se encontraron filas para esos jugadores.")
        _reset_form_values()
        return

    take["estado"]      = add_estado
    take["prioridad"]   = add_prior
    take["tags"]        = add_tags
    take["notas"]       = add_notas
    take["prox_accion"] = (add_date.isoformat() if add_date else "")
    take["estim_fee"]   = add_fee
    take["origen"]      = "App"

    if not st.session_state.shortlist_df.empty:
        k_old = st.session_state.shortlist_df[["player", "squad", "season"]].astype(str).agg("|".join, axis=1)
        k_new = take[["player", "squad", "season"]].astype(str).agg("|".join, axis=1)
        take  = take[~k_new.isin(set(k_old))]

    if len(take):
        st.session_state.shortlist_df = pd.concat([st.session_state.shortlist_df, take], ignore_index=True)
        st.success(f"Añadidos {len(take)} jugador(es) a la shortlist.")
    else:
        st.info("Todos los seleccionados ya estaban en la shortlist.")

    _reset_form_values()

def clear_form_now():
    """Borra todos los campos manualmente."""
    _reset_form_values()
    st.info("Campos del formulario borrados correctamente.")

# ==============================
# Alta de jugador
# ==============================
st.markdown("**➕ Alta de jugador** · Define su estado, prioridad y próximas acciones:")

c1, c2 = st.columns([0.65, 0.35])
with c1:
    st.multiselect(
        "Jugador(es) objetivo",
        options=sorted(dff_view["player"].dropna().unique().tolist()),
        placeholder="Escribe nombre…",
        key="sh_add_sel",
    )
with c2:
    st.write("")
    b1, b2 = st.columns(2, gap="small")
    b1.button("➕ Añadir a Shortlist", use_container_width=True, on_click=add_to_shortlist)
    b2.button("Borrar datos actuales", use_container_width=True, on_click=clear_form_now)

# Campos adicionales
f1, f2, f3, f4, f5 = st.columns([0.15, 0.12, 0.22, 0.21, 0.15], gap="small")
with f1:
    st.selectbox("Estado", estado_opts, index=0, key="sh_add_estado")
with f2:
    st.selectbox("Prioridad", ["A","B","C"], index=1, key="sh_add_prior")
with f3:
    st.text_input("Tags (coma)", key="sh_add_tags", placeholder="U23, zurdo, HG")
with f4:
    st.text_input("Notas (contexto, rol, status)", key="sh_add_notas")
with f5:
    st.text_input("Estim. fee (€)", key="sh_add_fee", placeholder="ej. 12-15M")

g1, g2 = st.columns([0.18, 0.82])
with g1:
    st.date_input("Próx. acción (YYYY-MM-DD)", value=None, format="YYYY-MM-DD", key="sh_add_date")
with g2:
    st.caption("Ej.: vídeo, live, informe específico, llamada, visita, etc.")

st.markdown("<hr style='opacity:.15;margin:.35rem 0;'>", unsafe_allow_html=True)

# ==============================
# Métricas extra (opcional)
# ==============================
all_metric_candidates = [c for c in dff_view.columns if (c.endswith("_per90") or c in ["cmp%","save%"])]
extra_metrics = st.multiselect(
    "Añadir columnas de métricas a la tabla",
    options=sorted(all_metric_candidates),
    default=[],
    format_func=lambda c: METRIC_LABELS.get(c, c),
    key="sh_extra_metrics",
)

# ==============================
# Tabla y acciones
# ==============================
left, right = st.columns([0.77, 0.23], gap="large")

with left:
    show_cols = core_cols + extra_metrics
    tbl = st.session_state.shortlist_df.reindex(columns=show_cols, fill_value="").copy()

    if not len(tbl):
        tbl["Sel"] = pd.Series(dtype=bool)
    else:
        sel_series = pd.Series(False, index=tbl.index, dtype=bool)
        if "shortlist_sel_ids" in st.session_state and len(st.session_state.shortlist_sel_ids):
            row_key = tbl[["player","squad","season"]].astype(str).agg("|".join, axis=1)
            sel_series = row_key.isin(set(st.session_state.shortlist_sel_ids)).astype(bool)
        tbl.insert(0, "Sel", sel_series)

    cfg = {
        "Sel": st.column_config.CheckboxColumn("Sel", help="Selecciona para eliminar", width="small"),
        "player":      st.column_config.TextColumn("Jugador", disabled=True),
        "squad":       st.column_config.TextColumn("Equipo", disabled=True),
        "season":      st.column_config.TextColumn("Temporada", disabled=True),
        "rol_tactico": st.column_config.TextColumn("Rol Táctico", disabled=True),
        "comp":        st.column_config.TextColumn("Competición", disabled=True),
        "min":         st.column_config.NumberColumn("Minutos", disabled=True),
        "age":         st.column_config.NumberColumn("Edad", disabled=True),
        "estado":      st.column_config.SelectboxColumn("Estado", options=estado_opts),
        "prioridad":   st.column_config.SelectboxColumn("Prioridad", options=["A","B","C"]),
        "tags":        st.column_config.TextColumn("Tags"),
        "notas":       st.column_config.TextColumn("Notas"),
        "prox_accion": st.column_config.TextColumn("Próx. acción"),
        "estim_fee":   st.column_config.TextColumn("Estim. fee (€)"),
        "origen":      st.column_config.TextColumn("Origen"),
    }
    for m in extra_metrics:
        cfg[m] = st.column_config.NumberColumn(METRIC_LABELS.get(m.lower(), m), disabled=True)

    edited = st.data_editor(
        tbl,
        column_config=cfg,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="sh_editor",
    )

    if st.button("Aplicar cambios", type="primary"):
        if len(edited):
            upd_meta = edited[["player","squad","season"] + meta_cols].copy()
            idx_base = st.session_state.shortlist_df.set_index(["player","squad","season"])
            idx_upd  = upd_meta.set_index(["player","squad","season"])
            for c in meta_cols:
                if c in idx_upd.columns:
                    idx_base.loc[idx_upd.index, c] = idx_upd[c]
            st.session_state.shortlist_df = idx_base.reset_index()[core_cols]
            st.success("Cambios aplicados.")
            st.rerun()

with right:
    st.markdown("### Acciones")

    selected_keys = []
    if isinstance(edited, pd.DataFrame) and len(edited):
        sel_col = edited["Sel"] if "Sel" in edited.columns else pd.Series([], dtype=bool)
        sel_mask = (
            pd.Series(sel_col, dtype="object")
            .apply(lambda x: bool(x) if pd.notna(x) else False)
            .astype(bool)
        )
        keys_df = edited.loc[sel_mask, ["player", "squad", "season"]].copy()
        if not keys_df.empty:
            key_series = keys_df.astype(str).agg("|".join, axis=1)
            selected_keys = key_series.tolist()

    if selected_keys:
        st.success(f"{len(selected_keys)} jugador(es) marcados para borrar.")
    else:
        st.caption("Marca **Sel** en la tabla para eliminar.")

    if st.button("Eliminar seleccionados", use_container_width=True, disabled=(len(selected_keys) == 0)):
        if len(st.session_state.shortlist_df):
            cur_keys = (
                st.session_state.shortlist_df[["player", "squad", "season"]]
                .astype(str).agg("|".join, axis=1)
            )
            keep_mask = ~cur_keys.isin(set(selected_keys))
            st.session_state.shortlist_df = (
                st.session_state.shortlist_df.loc[keep_mask].reset_index(drop=True)
            )
        st.session_state.shortlist_sel_ids = []
        st.rerun()

    st.download_button(
        "⬇️ Descargar shortlist (CSV)",
        data=st.session_state.shortlist_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="shortlist_scouting.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("Vaciar shortlist (seguro)", type="secondary", use_container_width=True,
                 disabled=(len(st.session_state.shortlist_df) == 0)):
        st.session_state.shortlist_df = pd.DataFrame(columns=core_cols)
        st.session_state.shortlist_sel_ids = []
        st.rerun()
