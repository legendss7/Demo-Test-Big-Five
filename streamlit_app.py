# streamlit_app.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from math import erf, sqrt
import base64
import io

# =========================
# 0) CONFIGURACIÓN & ESTILO
# =========================
st.set_page_config(
    page_title="Big Five (OCEAN) | Evaluación Profesional",
    page_icon="🧠",
    layout="wide",
)

CSS = """
<style>
/* Base blanco/negro */
html, body, [data-testid="stAppViewContainer"] { background:#fff !important; color:#111 !important; }
.block-container { padding-top: 0.8rem; max-width: 1200px; }

/* Header fijo minimal */
.header-wrap {
  position: sticky; top: 0; z-index: 6; background:#fff; border-bottom: 1px solid #eee;
  padding: 10px 6px; margin-bottom: .6rem;
}
.header-inner { display:flex; align-items:center; gap: 12px; flex-wrap: wrap; }
.header-logo { width:38px; height:38px; border-radius:8px; object-fit:contain; border:1px solid #eee; background:#fff; }
.header-title { font-weight:800; letter-spacing:.2px; font-size: clamp(16px, 2vw, 18px); }
.header-meta { margin-left:auto; font-size: 12px; color:#444 !important; display:flex; gap:10px; align-items:center; }

/* Animaciones */
@keyframes slideUpFade { 0% { transform: translateY(14px); opacity:0;} 100% { transform: translateY(0); opacity:1;} }
@keyframes pulseSoft { 0% { box-shadow:0 0 0 0 rgba(17,17,17,.20);} 70%{ box-shadow:0 0 0 10px rgba(17,17,17,0);} 100%{ box-shadow:0 0 0 0 rgba(17,17,17,0);} }

/* Hero portada */
.hero {
  border:1px solid #eee; border-radius:18px; padding:24px; background:#fff;
  box-shadow: 0 1px 3px rgba(0,0,0,.06); animation: slideUpFade .5s ease;
}
.hero-title { font-size: clamp(28px, 4.6vw, 40px); font-weight:900; margin:0 0 .3rem 0; }
.hero-sub { color:#444 !important; margin:0 0 .8rem 0; }
.step { display:flex; gap:10px; align-items:flex-start; margin:.2rem 0; }
.step-dot { width:8px; height:8px; border-radius:50%; background:#111; margin-top:.45rem; }

/* Badges & Cards */
.dim-badge {
  display:inline-block; border:1px solid #eaeaea; border-radius:16px; padding:6px 14px; font-size:14px;
  letter-spacing:.3px; background:#fff; animation: slideUpFade .6s ease;
}
.title-animated {
  font-size: clamp(22px, 4.8vw, 56px); font-weight: 900; letter-spacing:.3px; margin:.25rem 0 .35rem 0;
  line-height:1.08; animation: slideUpFade .6s ease;
}
.qtext { font-size: clamp(16px, 2.4vw, 18px); color:#222 !important; margin-bottom:.6rem; }

/* Pregunta */
.question-wrap {
  border:1px solid #eee; border-radius:16px; padding:18px; background:#fff;
  box-shadow: 0 1px 2px rgba(0,0,0,.06);
  animation: slideUpFade .6s ease;
}

/* KPIs */
.kpi-big {
  border:1px solid #eee; border-radius:18px; padding:18px 20px; background:#fff;
  display:flex; align-items:center; gap:16px; animation: slideUpFade .7s ease;
}
.kpi-dot { width:12px; height:12px; border-radius:999px; background:#111; animation: pulseSoft 2.2s infinite; }
.kpi-title { font-size:13px; color:#666 !important; margin-bottom:4px; }
.kpi-value { font-size:22px; font-weight:800; letter-spacing:.2px; }

/* Secciones */
.section-title { font-size: clamp(22px, 3vw, 28px); font-weight: 900; margin:.25rem 0 .75rem 0; }
.subtle { color:#555 !important; }
hr { border:none; border-top:1px solid #eee; margin:1rem 0; }

/* Cualitativo */
.qualibox {
  border:1px solid #eee; border-radius:16px; padding:16px; background:#fff; margin-bottom:14px;
}
.qualititle { font-weight:800; margin-bottom:.35rem; }
.qualichips { display:flex; flex-wrap:wrap; gap:6px; margin:.35rem 0 .25rem; }
.chip { border:1px solid #e9e9e9; border-radius:999px; padding:2px 10px; font-size:12px; }

/* Print */
@media print {
  .stApp header, .stApp footer, [data-testid="stToolbar"], [data-testid="stSidebar"], .viewerBadge_container__1QSob { display:none !important; }
  .block-container { padding: 0 20px !important; max-width: 100% !important; }
  .stPlotlyChart canvas { page-break-inside: avoid; }
  .qualibox, .question-wrap, .kpi-big { break-inside: avoid; }
  .print-header { position: fixed; top: 0; left: 0; right: 0; border-bottom:1px solid #eee; padding:8px 20px; background:#fff; }
  .print-footer { position: fixed; bottom:0; left:0; right:0; border-top:1px solid #eee; padding:6px 20px; font-size:11px; color:#444 !important; background:#fff; }
  .print-spacer { height: 64px; }
  .print-footer-spacer { height: 42px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ====================
# 1) DATOS DE EMPRESA (SIN SIDEBAR)
# ====================
if "empresa" not in st.session_state: st.session_state.empresa = "Tu Empresa S.A."
if "candidato" not in st.session_state: st.session_state.candidato = "Candidato/a"
if "puesto" not in st.session_state: st.session_state.puesto = "—"
if "logo_b64" not in st.session_state: st.session_state.logo_b64 = ""

def handle_company_form():
    st.session_state.empresa = st.session_state._empresa
    st.session_state.candidato = st.session_state._candidato
    st.session_state.puesto = st.session_state._puesto
    if st.session_state.get("_logo") is not None:
        b = st.session_state._logo.read()
        st.session_state.logo_b64 = base64.b64encode(b).decode()

# ====================
# 2) MODELO DE DATOS
# ====================
DIMENSIONES = {
    "Apertura a la Experiencia": {"code": "O", "icon": "💡"},
    "Responsabilidad": {"code": "C", "icon": "🎯"},
    "Extraversión": {"code": "E", "icon": "🗣️"},
    "Amabilidad": {"code": "A", "icon": "🤝"},
    "Estabilidad Emocional": {"code": "N", "icon": "🧘"},
}
DIM_LIST = list(DIMENSIONES.keys())

LIKERT_LABELS = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}
LIKERT = list(LIKERT_LABELS.keys())

def reverse_score(x: int) -> int:
    return 6 - x

def preguntas_bigfive():
    P = []
    def add(dim, key_prefix, items):
        for i, (texto, rev) in enumerate(items, start=1):
            P.append({"key": f"{key_prefix}{i}", "dim": dim, "text": texto, "reverse": rev})
    add("Apertura a la Experiencia", "O", [
        ("Tengo una imaginación activa.", False),
        ("Me atraen las ideas complejas.", False),
        ("Disfruto explorando arte o cultura.", False),
        ("Estoy abierto a cambiar de opinión.", False),
        ("Valoro la creatividad y la novedad.", False),
        ("Prefiero rutinas a probar cosas nuevas.", True),
        ("Me aburren los debates abstractos.", True),
        ("Evito actividades poco convencionales.", True),
        ("Me cuesta apreciar nuevas perspectivas.", True),
        ("Rara vez busco experiencias distintas.", True),
    ])
    add("Responsabilidad", "C", [
        ("Planifico mis tareas con anticipación.", False),
        ("Soy constante con mis objetivos.", False),
        ("Cumplo plazos y compromisos.", False),
        ("Me esfuerzo en los detalles.", False),
        ("Mantengo orden en mis cosas.", False),
        ("Dejo tareas a medias.", True),
        ("Me distraigo con facilidad.", True),
        ("Aplazo cosas importantes.", True),
        ("Soy desordenado con frecuencia.", True),
        ("Olvido hacer seguimientos.", True),
    ])
    add("Extraversión", "E", [
        ("Me energiza interactuar con otras personas.", False),
        ("Hablo con soltura en grupos grandes.", False),
        ("Busco oportunidades para socializar.", False),
        ("Me siento cómodo iniciando conversaciones.", False),
        ("Disfruto, a veces, ser el centro de atención.", False),
        ("Prefiero estar solo la mayor parte del tiempo.", True),
        ("Soy reservado y callado.", True),
        ("Evito reuniones sociales prolongadas.", True),
        ("Me incomodan los desconocidos.", True),
        ("Prefiero trabajar en segundo plano.", True),
    ])
    add("Amabilidad", "A", [
        ("Empatizo con facilidad con los demás.", False),
        ("Confío en las buenas intenciones de la gente.", False),
        ("Colaboro y apoyo a mi equipo.", False),
        ("Trato a las personas con respeto y cortesía.", False),
        ("Busco resolver conflictos de forma constructiva.", False),
        ("Sospecho de las motivaciones ajenas.", True),
        ("Suelo ser directo aunque suene duro.", True),
        ("Me cuesta ponerme en el lugar del otro.", True),
        ("Antepongo mis intereses casi siempre.", True),
        ("No me conmueven los problemas de otros.", True),
    ])
    add("Estabilidad Emocional", "N", [
        ("Permanezco calmado ante la presión.", False),
        ("Gestiono el estrés de forma efectiva.", False),
        ("Me recupero rápido de contratiempos.", False),
        ("Mantengo la serenidad en situaciones difíciles.", False),
        ("Confío en mis recursos para resolver problemas.", False),
        ("Me preocupan excesivamente las cosas.", True),
        ("Me irrito con facilidad.", True),
        ("Tengo cambios de ánimo frecuentes.", True),
        ("Me abruma la incertidumbre.", True),
        ("Me siento ansioso sin razón aparente.", True),
    ])
    return P

PREGUNTAS = preguntas_bigfive()

# ===============
# 3) SESSION STATE
# ===============
if "stage" not in st.session_state: st.session_state.stage = "inicio"      # inicio | test | resultados
if "q_index" not in st.session_state: st.session_state.q_index = 0         # 0..49
if "answers" not in st.session_state: st.session_state.answers = {q["key"]: None for q in PREGUNTAS}
if "started_at" not in st.session_state: st.session_state.started_at = None
if "finished_at" not in st.session_state: st.session_state.finished_at = None

def reset_all():
    st.session_state.stage = "inicio"
    st.session_state.q_index = 0
    st.session_state.answers = {q["key"]: None for q in PREGUNTAS}
    st.session_state.started_at = None
    st.session_state.finished_at = None

def current_question():
    return PREGUNTAS[st.session_state.q_index]

def go_results():
    st.session_state.stage = "resultados"
    st.session_state.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M")

# ============
# 4) SCORING
# ============
def compute_scores(answers: dict) -> dict:
    buckets = {d: [] for d in DIM_LIST}
    for q in PREGUNTAS:
        val = answers.get(q["key"])
        if val is None: continue
        score_1_5 = reverse_score(val) if q["reverse"] else val
        buckets[q["dim"]].append(score_1_5)
    # completar con neutrales si faltan
    for d in DIM_LIST:
        if len(buckets[d]) < 10:
            buckets[d] += [3] * (10 - len(buckets[d]))
    return {d: round(((np.mean(buckets[d]) - 1) / 4) * 100, 1) for d in DIM_LIST}

def interprete(score):
    if score >= 75: return "Muy alto", "Dominante"
    if score >= 60: return "Alto", "Marcado"
    if score >= 40: return "Promedio", "Moderado"
    if score >= 25: return "Bajo", "Suave"
    return "Muy bajo", "Mínimo"

# ============
# 5) ENCABEZADO FIJO (CON LOGO)
# ============
logo_html = ""
if st.session_state.logo_b64:
    logo_html = f"<img class='header-logo' src='data:image/png;base64,{st.session_state.logo_b64}'/>"

st.markdown(
    f"""
    <div class="header-wrap">
      <div class="header-inner">
        {logo_html}
        <div class="header-title">{st.session_state.empresa} — Evaluación Big Five (OCEAN)</div>
        <div class="header-meta">
            <span>👤 {st.session_state.candidato}</span>
            <span>💼 {st.session_state.puesto}</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============
# 6) PANTALLAS
# ============
def portada():
    # Hero
    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>Evaluación de Personalidad Big Five (OCEAN)</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Herramienta profesional para selección y desarrollo. Responde 50 afirmaciones en escala 1–5. Auto-avance activado.</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([2,1], vertical_alignment="top")
    with c1:
        st.markdown("**Cómo funciona**")
        for t in [
            "Lee la afirmación y elige la opción que mejor te represente.",
            "Avanzas automáticamente al seleccionar la alternativa.",
            "Al terminar, verás un informe con KPIs, gráficos y análisis.",
        ]:
            st.markdown(f"<div class='step'><div class='step-dot'></div><div>{t}</div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown("**Datos del informe**")
        with st.form("company_form"):
            st.text_input("Empresa", key="_empresa", value=st.session_state.empresa)
            st.text_input("Candidato/a", key="_candidato", value=st.session_state.candidato)
            st.text_input("Puesto / Área", key="_puesto", value=st.session_state.puesto)
            st.file_uploader("Logo (PNG/JPG)", type=["png","jpg","jpeg"], key="_logo")
            submitted = st.form_submit_button("Guardar datos")
            if submitted:
                handle_company_form()
                st.success("Datos guardados.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Dimensiones en tarjetas
    c1, c2, c3, c4, c5 = st.columns(5)
    cols = [c1, c2, c3, c4, c5]
    for i, d in enumerate(DIM_LIST):
        with cols[i]:
            st.markdown(
                f"<div class='qualibox' style='text-align:center'><div class='qualititle'>{DIMENSIONES[d]['icon']} {DIMENSIONES[d]['code']}</div><div class='subtle'>{d}</div></div>",
                unsafe_allow_html=True
            )

    st.markdown("")
    if st.button("🚀 Comenzar evaluación", type="primary", use_container_width=True):
        st.session_state.stage = "test"
        st.session_state.started_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.rerun()

def handle_choice(qkey):
    # Guardamos respuesta elegida
    chosen = st.session_state.get(f"radio_{qkey}", None)
    if chosen is not None:
        st.session_state.answers[qkey] = chosen
    # Auto-avance + scroll top
    total = len(PREGUNTAS)
    if st.session_state.q_index < total - 1:
        st.session_state.q_index += 1
        st.markdown("<script>window.parent.scrollTo({top:0,behavior:'auto'});</script>", unsafe_allow_html=True)
        st.rerun()
    else:
        go_results()
        st.rerun()

def pantalla_test():
    q = current_question()
    idx = st.session_state.q_index
    total = len(PREGUNTAS)

    st.markdown(f"<div class='dim-badge'>{DIMENSIONES[q['dim']]['icon']} {DIMENSIONES[q['dim']]['code']} — {q['dim']}</div>", unsafe_allow_html=True)
    # Dimensión gigante
    st.markdown(f"<div class='title-animated'>{q['dim']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='qtext'>Pregunta {idx+1} de {total}: {q['text']}</div>", unsafe_allow_html=True)

    st.markdown("<div class='question-wrap'>", unsafe_allow_html=True)
    # Valor actual si lo hubo
    current_val = st.session_state.answers.get(q["key"], None)

    # Radio con callback robusto
    st.radio(
        "Tu respuesta",
        options=LIKERT,
        index=(LIKERT.index(current_val) if current_val in LIKERT else None),
        format_func=lambda k: f"{k} — {LIKERT_LABELS[k]}",
        key=f"radio_{q['key']}",
        horizontal=True,
        label_visibility="collapsed",
        on_change=lambda: handle_choice(q["key"])
    )
    st.markdown("</div>", unsafe_allow_html=True)

    pct = int((idx / total) * 100)
    st.progress(pct/100, text=f"Progreso: {idx}/{total} ({pct}%)")

def build_report_html(scores, empresa, candidato, puesto, logo_b64):
    # Construye un HTML imprimible (para descargar), sin dependencias externas
    order = list(scores.keys())
    values = [scores[d] for d in order]
    # tabla simple
    rows = "".join(
        f"<tr><td>{d}</td><td style='text-align:right'>{scores[d]:.1f}</td></tr>"
        for d in order
    )
    logo_html = f"<img style='height:40px' src='data:image/png;base64,{logo_b64}'>" if logo_b64 else ""
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Informe Big Five</title>
<style>
body {{ font-family: Arial, sans-serif; color:#111; }}
.container {{ max-width: 960px; margin: 0 auto; padding: 20px; }}
.header {{ display:flex; align-items:center; gap:10px; border-bottom:1px solid #eee; padding-bottom:8px; margin-bottom:16px; }}
h1 {{ margin:.2rem 0; }}
.kpis {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin:14px 0; }}
.kpi {{ border:1px solid #eee; border-radius:12px; padding:12px; }}
table {{ width:100%; border-collapse: collapse; margin-top:10px; }}
td, th {{ border-bottom:1px solid #eee; padding:8px; }}
.footer {{ border-top:1px solid #eee; margin-top:20px; padding-top:10px; font-size:12px; color:#444; }}
</style>
</head>
<body>
<div class="container" id="report">
  <div class="header">{logo_html}
    <div>
      <div style="font-weight:800">{empresa} — Informe Big Five (OCEAN)</div>
      <div style="font-size:12px;color:#444">Candidato: <b>{candidato}</b> | Puesto: <b>{puesto}</b> | Fecha: <b>{datetime.now().strftime('%Y-%m-%d')}</b></div>
    </div>
  </div>
  <h1>Resumen</h1>
  <div class="kpis">
    <div class="kpi"><div style="font-size:12px;color:#666">Promedio global</div><div style="font-weight:800;font-size:20px">{np.mean(values):.1f}</div></div>
    <div class="kpi"><div style="font-size:12px;color:#666">Desviación estándar</div><div style="font-weight:800;font-size:20px">{np.std(values, ddof=1):.2f}</div></div>
    <div class="kpi"><div style="font-size:12px;color:#666">Dimensión más alta</div><div style="font-weight:800;font-size:20px">{max(scores, key=scores.get)}</div></div>
    <div class="kpi"><div style="font-size:12px;color:#666">Dimensión más baja</div><div style="font-weight:800;font-size:20px">{min(scores, key=scores.get)}</div></div>
  </div>
  <h2>Puntuaciones</h2>
  <table><tbody>{rows}</tbody></table>

  <div class="footer">{empresa} • Big Five • {candidato} • {datetime.now().strftime('%Y-%m-%d')}</div>
</div>
</body></html>"""
    return html.encode("utf-8")

def pantalla_resultados():
    scores = compute_scores(st.session_state.answers)
    order = list(scores.keys())
    values = [scores[d] for d in order]

    # Encabezado/Pie para impresión en navegador
    st.markdown(
        f"""
        <div class='print-header'>
          <div style="display:flex;align-items:center;gap:10px;">
            <div style="font-weight:800;">{st.session_state.empresa} — Informe Big Five</div>
            <div style="margin-left:auto;font-size:12px;color:#444;">
              Candidato: <b>{st.session_state.candidato}</b> &nbsp;|&nbsp; Puesto: <b>{st.session_state.puesto}</b> &nbsp;|&nbsp; Fecha: <b>{datetime.now().strftime('%Y-%m-%d')}</b>
            </div>
          </div>
        </div>
        <div class='print-spacer'></div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div id='report-root'>", unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='kpi-big'><div class='kpi-dot'></div><div><div class='kpi-title'>Promedio global</div><div class='kpi-value'>"+f"{np.mean(values):.1f} / 100"+"</div></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='kpi-big'><div class='kpi-dot'></div><div><div class='kpi-title'>Desviación estándar</div><div class='kpi-value'>"+f"{np.std(values, ddof=1):.2f}"+"</div></div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='kpi-big'><div class='kpi-dot'></div><div><div class='kpi-title'>Dimensión más alta</div><div class='kpi-value'>"+f"{max(scores, key=scores.get)}"+"</div></div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='kpi-big'><div class='kpi-dot'></div><div><div class='kpi-title'>Dimensión más baja</div><div class='kpi-value'>"+f"{min(scores, key=scores.get)}"+"</div></div></div>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Visualizaciones
    st.markdown("<div class='section-title'>Visualizaciones del perfil</div>", unsafe_allow_html=True)
    # Radar
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scat terpolar(
        r=values,
        theta=[f"{DIMENSIONES[d]['code']} {d}" for d in order],
        fill='toself', name='Perfil',
        line=dict(width=2, color="#111"),
        fillcolor='rgba(17,17,17,0.08)', marker=dict(size=7, color="#111")
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=520, template="plotly_white")

    # Barras
    df_bar = pd.DataFrame({"Dimensión": order, "Puntuación": values}).sort_values("Puntuación", ascending=True)
    fig_bar = px.bar(df_bar, x="Puntuación", y="Dimensión", orientation="h", text="Puntuación")
    fig_bar.update_traces(texttemplate="%{x:.1f}", marker_color="#111")
    fig_bar.update_layout(height=520, template="plotly_white")

    # Comparativo
    ref = 50
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=order, y=values, name="Tu perfil", marker_color="#111", text=[f"{v:.1f}" for v in values], textposition="outside"))
    fig_comp.add_trace(go.Bar(x=order, y=[ref]*5, name="Promedio referencia (50)", marker_color="#aaa", text=["50"]*5, textposition="outside"))
    fig_comp.update_layout(barmode="group", height=520, template="plotly_white", legend_orientation="h")

    t1, t2, t3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])
    with t1: st.plotly_chart(fig_radar, use_container_width=True)
    with t2: st.plotly_chart(fig_bar, use_container_width=True)
    with t3: st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Estadísticos & percentiles
    st.markdown("<div class='section-title'>Estadísticos por dimensión</div>", unsafe_allow_html=True)
    MU, SIG = 50, 15
    def z(x): return (x - MU) / SIG
    def cdf_norm(x): return 0.5 * (1 + erf(x / sqrt(2)))
    rows = []
    for d in DIM_LIST:
        s = scores[d]; Z = z(s); pct = round(cdf_norm(Z) * 100, 1)
        nivel, etiqueta = interprete(s)
        rows.append([DIMENSIONES[d]["code"], d, s, Z, pct, f"{nivel} ({etiqueta})"])
    df_stats = pd.DataFrame(rows, columns=["Código", "Dimensión", "Puntuación", "z-score", "Percentil (%)", "Clasificación"])
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Análisis cualitativo
    st.markdown("<div class='section-title'>Análisis cualitativo por dimensión</div>", unsafe_allow_html=True)
    QUALI = {
        "Apertura a la Experiencia": {
            "pros": ["Curiosidad intelectual", "Pensamiento creativo", "Flexibilidad cognitiva"],
            "contras": ["Puede dispersarse", "Sobre-innovación", "Dificultad con rutinas rígidas"],
            "roles_altos": ["Innovación", "I+D", "Diseño", "Estrategia"],
            "roles_bajos": ["Operaciones", "Calidad", "Procesos", "Compliance"],
        },
        "Responsabilidad": {
            "pros": ["Planificación y orden", "Seguimiento", "Orientación a objetivos"],
            "contras": ["Rigidez", "Perfeccionismo", "Sobrecarga por control"],
            "roles_altos": ["Gestión de Proyectos", "Auditoría", "Finanzas", "PMO"],
            "roles_bajos": ["Creativo freelance", "Exploración UX", "Labs de prototipado"],
        },
        "Extraversión": {
            "pros": ["Energía social", "Asertividad", "Influencia"],
            "contras": ["Impulsividad social", "Menos tolerancia a tareas solitarias", "Fatiga por sobreexposición"],
            "roles_altos": ["Ventas", "Relaciones Públicas", "Liderazgo de equipos"],
            "roles_bajos": ["Análisis de datos", "Investigación", "Desarrollo de software"],
        },
        "Amabilidad": {
            "pros": ["Empatía", "Cooperación", "Gestión de conflictos"],
            "contras": ["Evitar confrontación", "Dificultad para límites", "Complacencia"],
            "roles_altos": ["RR. HH.", "Atención al Cliente", "Mediación"],
            "roles_bajos": ["Negociación B2B", "Consultoría estratégica", "Gestión de riesgo"],
        },
        "Estabilidad Emocional": {
            "pros": ["Calma bajo presión", "Resiliencia", "Decisiones serenas"],
            "contras": ["Subestimación de riesgos", "Desconexión emocional", "Autoexigencia"],
            "roles_altos": ["Crisis/Operaciones", "Liderazgo ejecutivo", "Salud y seguridad"],
            "roles_bajos": ["Entornos muy volátiles", "Startups sin estructura", "Guardias 24/7"],
        },
    }

    for d in DIM_LIST:
        s = scores[d]; nivel, etiqueta = interprete(s)
        high = s >= 60
        with st.expander(f"{DIMENSIONES[d]['icon']} {d} — {s:.1f} ({nivel})", expanded=True):
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                st.markdown("**Fortalezas**")
                st.markdown("<div class='qualichips'>" + "".join([f"<span class='chip'>✅ {x}</span>" for x in QUALI[d]["pros"]]) + "</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("**Alertas**")
                st.markdown("<div class='qualichips'>" + "".join([f"<span class='chip'>⚠️ {x}</span>" for x in QUALI[d]["contras"]]) + "</div>", unsafe_allow_html=True)
            with c3:
                st.markdown("**Posibles cargos**")
                cargos = QUALI[d]["roles_altos"] if high else QUALI[d]["roles_bajos"]
                st.markdown("<div class='qualichips'>" + "".join([f"<span class='chip'>💼 {x}</span>" for x in cargos]) + "</div>", unsafe_allow_html=True)
            st.caption("Recomendación: alinear entorno, funciones y herramientas para potenciar fortalezas y mitigar riesgos.")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Exportar
    st.markdown("<div class='section-title'>Exportar informe</div>", unsafe_allow_html=True)
    export_df = pd.DataFrame({"Dimensión": order, "Puntuación": values})
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")

    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        st.download_button(
            "📄 CSV",
            data=csv_bytes,
            file_name=f"BigFive_Resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        # HTML imprimible (si el navegador bloquea el print directo)
        html_bytes = build_report_html(
            scores,
            st.session_state.empresa,
            st.session_state.candidato,
            st.session_state.puesto,
            st.session_state.logo_b64
        )
        st.download_button(
            "🧾 HTML imprimible",
            data=html_bytes,
            file_name=f"BigFive_Informe_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True
        )
    with c3:
        if st.button("🖨️ Guardar como PDF (imprimir)", use_container_width=True):
            st.markdown(
                "<script>window.setTimeout(function(){ window.print(); }, 100);</script>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)  # report-root

    # Pie para impresión
    st.markdown(
        f"""
        <div class='print-footer-spacer'></div>
        <div class='print-footer'>
          {st.session_state.empresa} • Big Five • {st.session_state.candidato} • {datetime.now().strftime('%Y-%m-%d')}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    if st.button("🔁 Nuevo test", use_container_width=True):
        reset_all()
        st.rerun()

# ============
# 7) ROUTER
# ============
if st.session_state.stage == "inicio":
    portada()
elif st.session_state.stage == "test":
    pantalla_test()
else:
    pantalla_resultados()
