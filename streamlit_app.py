import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="Big Five PRO | Evaluación Profesional", page_icon="🧠", layout="wide")

# Estilos (fondo blanco, texto negro, colores suaves)
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
html, body, [data-testid="stAppViewContainer"] {
  background: #ffffff !important; color: #111 !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
.block-container { padding-top: 1.0rem; padding-bottom: 3rem; max-width: 1180px; }
.dim-title {
  font-size: clamp(1.7rem, 4.5vw, 2.8rem);
  font-weight: 900;
  letter-spacing: .25px; line-height: 1.15; margin: .2rem 0 .6rem 0;
  animation: fadeSlide .45s ease-out;
}
@keyframes fadeSlide { from {opacity:0; transform: translateY(6px);} to {opacity:1; transform: translateY(0);} }
.card {
  border: 1px solid #ececec; border-radius: 14px; padding: 18px 18px; background: #fff;
  box-shadow: 0 2px 0 rgba(0,0,0,0.02);
}
.kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin: 10px 0 6px 0; }
.kpi .k { border: 1px solid #ececec; border-radius: 14px; padding: 18px; background: #fff; }
.kpi .k .v { font-size: 1.8rem; font-weight: 800; }
.kpi .k .l { font-size: .95rem; opacity: .85; }
details summary { font-weight: 700; cursor: pointer; padding: 10px 0; }
#report-root { padding: 6px 8px; }

/* Acentos suaves (sin azul) */
.accent-bg { background: linear-gradient(135deg, #F4A261 0%, #F2CC8F 100%); color:#111; }
.btn-primary {
  padding:10px 16px; border:1px solid #111; background:#111; color:#fff; border-radius:10px; cursor:pointer; font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# UTILS
# ==============================
def scroll_top():
    st.markdown("""
    <script>
      setTimeout(() => {
        try {
          const appView = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
          if (appView) appView.scrollTo({ top: 0, behavior: 'auto' });
          window.parent.scrollTo({ top: 0, behavior: 'auto' });
        } catch (e) {}
      }, 60);
    </script>
    """, unsafe_allow_html=True)

def reverse_score(score: int) -> int:
    return 6 - score

# ==============================
# BIG FIVE MODEL
# ==============================
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O",
        "desc": "Imaginación, curiosidad intelectual, creatividad y aprecio por nuevas experiencias.",
        "pros": ["Alta creatividad e ideación.", "Ajuste a ambientes cambiantes.", "Curiosidad por aprender."],
        "contras": ["Puede dispersarse si no prioriza.", "Busca novedad cuando se requiere rutina."],
        "cargos": ["Innovación", "Diseño UX/UI", "Estrategia", "I+D", "Consultoría"]
    },
    "Responsabilidad": {
        "code": "C",
        "desc": "Autodisciplina, organización, cumplimiento de objetivos y sentido del deber.",
        "pros": ["Fiabilidad y consistencia.", "Orientación a resultados y detalle.", "Planificación eficaz."],
        "contras": ["Rigidez ante cambios súbitos.", "Perfeccionismo o sobrecarga."],
        "cargos": ["Gestión de Proyectos", "Finanzas", "Auditoría", "Operaciones", "Calidad"]
    },
    "Extraversión": {
        "code": "E",
        "desc": "Sociabilidad, asertividad, energía y búsqueda de estimulación social.",
        "pros": ["Habilidades de influencia y networking.", "Alta energía en equipos.", "Comunicación efectiva."],
        "contras": ["Puede dominar conversaciones.", "Menor preferencia por trabajo individual prolongado."],
        "cargos": ["Ventas", "Liderazgo Comercial", "Relaciones Públicas", "Desarrollo de Negocios"]
    },
    "Amabilidad": {
        "code": "A",
        "desc": "Cooperación, empatía, compasión, confianza y respeto.",
        "pros": ["Clima colaborativo y confianza.", "Resolución de conflictos y empatía.", "Buen servicio al cliente."],
        "contras": ["Dificultad para confrontar.", "Puede evitar decisiones impopulares."],
        "cargos": ["RR.HH.", "Servicio al Cliente", "Mediación", "Trabajo Social", "Customer Success"]
    },
    "Estabilidad Emocional": {
        "code": "N",
        "desc": "Gestión del estrés y calma bajo presión (opuesto a Neuroticismo).",
        "pros": ["Resiliencia ante la presión.", "Toma de decisiones serena.", "Estabilidad en crisis."],
        "contras": ["Puede subestimar riesgos emocionales ajenos.", "Menor urgencia ante problemas menores."],
        "cargos": ["Operaciones Críticas", "Liderazgo Ejecutivo", "Soporte de Incidentes", "Seguridad/Compliance"]
    },
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

LIKERT = {1: "Totalmente en desacuerdo", 2: "En desacuerdo", 3: "Neutral", 4: "De acuerdo", 5: "Totalmente de acuerdo"}
LIKERT_KEYS = list(LIKERT.keys())

# Preguntas (10 por dimensión: 5 directas + 5 inversas)
PREGUNTAS = [
    # O
    {"text": "Tengo una imaginación muy activa.", "dim": "Apertura a la Experiencia", "key": "O1", "rev": False},
    {"text": "Disfruto explorando ideas nuevas y complejas.", "dim": "Apertura a la Experiencia", "key": "O2", "rev": False},
    {"text": "Me atraen el arte, la música o la literatura.", "dim": "Apertura a la Experiencia", "key": "O3", "rev": False},
    {"text": "Busco experiencias poco convencionales.", "dim": "Apertura a la Experiencia", "key": "O4", "rev": False},
    {"text": "Valoro la creatividad por encima de la rutina.", "dim": "Apertura a la Experiencia", "key": "O5", "rev": False},
    {"text": "Prefiero mantener hábitos a probar cosas nuevas.", "dim": "Apertura a la Experiencia", "key": "O6", "rev": True},
    {"text": "Las discusiones filosóficas me resultan poco útiles.", "dim": "Apertura a la Experiencia", "key": "O7", "rev": True},
    {"text": "Rara vez reflexiono sobre conceptos abstractos.", "dim": "Apertura a la Experiencia", "key": "O8", "rev": True},
    {"text": "Me inclino por lo tradicional más que por lo original.", "dim": "Apertura a la Experiencia", "key": "O9", "rev": True},
    {"text": "Evito cambiar mis hábitos establecidos.", "dim": "Apertura a la Experiencia", "key": "O10", "rev": True},
    # C
    {"text": "Estoy bien preparado/a para mis tareas.", "dim": "Responsabilidad", "key": "C1", "rev": False},
    {"text": "Cuido los detalles al trabajar.", "dim": "Responsabilidad", "key": "C2", "rev": False},
    {"text": "Cumplo mis compromisos y plazos.", "dim": "Responsabilidad", "key": "C3", "rev": False},
    {"text": "Sigo un plan y un horario definidos.", "dim": "Responsabilidad", "key": "C4", "rev": False},
    {"text": "Me exijo altos estándares de calidad.", "dim": "Responsabilidad", "key": "C5", "rev": False},
    {"text": "Dejo mis cosas desordenadas.", "dim": "Responsabilidad", "key": "C6", "rev": True},
    {"text": "Evito responsabilidades cuando puedo.", "dim": "Responsabilidad", "key": "C7", "rev": True},
    {"text": "Me distraigo con facilidad.", "dim": "Responsabilidad", "key": "C8", "rev": True},
    {"text": "Olvido colocar las cosas en su lugar.", "dim": "Responsabilidad", "key": "C9", "rev": True},
    {"text": "Aplazo tareas importantes.", "dim": "Responsabilidad", "key": "C10", "rev": True},
    # E
    {"text": "Disfruto ser el centro de la reunión.", "dim": "Extraversión", "key": "E1", "rev": False},
    {"text": "Me siento a gusto con personas nuevas.", "dim": "Extraversión", "key": "E2", "rev": False},
    {"text": "Busco la compañía de otras personas.", "dim": "Extraversión", "key": "E3", "rev": False},
    {"text": "Participo activamente en conversaciones.", "dim": "Extraversión", "key": "E4", "rev": False},
    {"text": "Me energiza compartir con otros.", "dim": "Extraversión", "key": "E5", "rev": False},
    {"text": "Prefiero estar solo/a que rodeado/a de gente.", "dim": "Extraversión", "key": "E6", "rev": True},
    {"text": "Soy más bien reservado/a y callado/a.", "dim": "Extraversión", "key": "E7", "rev": True},
    {"text": "Me cuesta expresarme ante grupos grandes.", "dim": "Extraversión", "key": "E8", "rev": True},
    {"text": "Prefiero actuar en segundo plano.", "dim": "Extraversión", "key": "E9", "rev": True},
    {"text": "Me agotan las interacciones sociales prolongadas.", "dim": "Extraversión", "key": "E10", "rev": True},
    # A
    {"text": "Empatizo con las emociones de los demás.", "dim": "Amabilidad", "key": "A1", "rev": False},
    {"text": "Me preocupo por el bienestar ajeno.", "dim": "Amabilidad", "key": "A2", "rev": False},
    {"text": "Trato a otros con respeto y consideración.", "dim": "Amabilidad", "key": "A3", "rev": False},
    {"text": "Ayudo sin esperar nada a cambio.", "dim": "Amabilidad", "key": "A4", "rev": False},
    {"text": "Confío en las buenas intenciones de la gente.", "dim": "Amabilidad", "key": "A5", "rev": False},
    {"text": "No me interesa demasiado la gente.", "dim": "Amabilidad", "key": "A6", "rev": True},
    {"text": "Sospecho de las intenciones ajenas.", "dim": "Amabilidad", "key": "A7", "rev": True},
    {"text": "A veces soy poco considerado/a.", "dim": "Amabilidad", "key": "A8", "rev": True},
    {"text": "Pienso primero en mí antes que en otros.", "dim": "Amabilidad", "key": "A9", "rev": True},
    {"text": "Los problemas de otros no me afectan mucho.", "dim": "Amabilidad", "key": "A10", "rev": True},
    # N
    {"text": "Me mantengo calmado/a bajo presión.", "dim": "Estabilidad Emocional", "key": "N1", "rev": False},
    {"text": "Rara vez me siento ansioso/a o estresado/a.", "dim": "Estabilidad Emocional", "key": "N2", "rev": False},
    {"text": "Soy emocionalmente estable.", "dim": "Estabilidad Emocional", "key": "N3", "rev": False},
    {"text": "Me recupero rápido de contratiempos.", "dim": "Estabilidad Emocional", "key": "N4", "rev": False},
    {"text": "Me siento seguro/a de mí mismo/a.", "dim": "Estabilidad Emocional", "key": "N5", "rev": False},
    {"text": "Me preocupo demasiado por las cosas.", "dim": "Estabilidad Emocional", "key": "N6", "rev": True},
    {"text": "Me irrito con facilidad.", "dim": "Estabilidad Emocional", "key": "N7", "rev": True},
    {"text": "Con frecuencia me siento triste.", "dim": "Estabilidad Emocional", "key": "N8", "rev": True},
    {"text": "Tengo cambios de ánimo frecuentes.", "dim": "Estabilidad Emocional", "key": "N9", "rev": True},
    {"text": "El estrés me sobrepasa.", "dim": "Estabilidad Emocional", "key": "N10", "rev": True},
]

# ==============================
# STATE
# ==============================
if "stage" not in st.session_state:
    st.session_state.stage = "inicio"
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {p["key"]: None for p in PREGUNTAS}
if "fecha_eval" not in st.session_state:
    st.session_state.fecha_eval = None

# ==============================
# CÁLCULOS
# ==============================
def compute_scores(answers: dict) -> dict:
    buckets = {dim: [] for dim in DIMENSIONES_LIST}
    for p in PREGUNTAS:
        key = p["key"]
        raw = answers.get(key)
        v = 3 if raw is None else (reverse_score(raw) if p["rev"] else raw)
        buckets[p["dim"]].append(v)
    out = {}
    for dim, vals in buckets.items():
        avg = np.mean(vals)
        perc = ((avg - 1) / 4) * 100
        out[dim] = round(float(perc), 1)
    return out

def label_level(score: float):
    if score >= 75: return "Muy Alto", "Dominante"
    if score >= 60: return "Alto", "Marcado"
    if score >= 40: return "Promedio", "Moderado"
    if score >= 25: return "Bajo", "Suave"
    return "Muy Bajo", "Mínimo"

# ==============================
# CALLBACK (auto-avance sin st.rerun dentro)
# ==============================
def on_answer_change():
    i = st.session_state.q_index
    p = PREGUNTAS[i]
    val = st.session_state.get(f"resp_{p['key']}")
    st.session_state.answers[p["key"]] = val
    if i < len(PREGUNTAS) - 1:
        st.session_state.q_index = i + 1
        scroll_top()
        # NO st.rerun() aquí: Streamlit ya rerenderiza al cambiar el widget.
    else:
        st.session_state.stage = "resultados"
        st.session_state.fecha_eval = datetime.now().strftime("%d/%m/%Y %H:%M")
        scroll_top()

def restart():
    st.session_state.stage = "inicio"
    st.session_state.q_index = 0
    st.session_state.answers = {p["key"]: None for p in PREGUNTAS}
    st.session_state.fecha_eval = None

# ==============================
# VISTAS
# ==============================
def view_inicio():
    scroll_top()
    st.markdown(
        """
        <div class="card accent-bg" style="padding:26px; border-radius:16px; margin-bottom:18px;">
          <h1 style="margin:0 0 6px 0; font-size:clamp(1.9rem,3.8vw,2.8rem); font-weight:900;">🧠 Test Big Five (OCEAN)</h1>
          <p style="margin:0; font-size:1.06rem; opacity:.95;">Evaluación profesional con resultados accionables, métricas y visualizaciones.<br>Fondo blanco, alto contraste y diseño responsivo.</p>
        </div>
        """, unsafe_allow_html=True
    )
    col1, col2 = st.columns([1.4, 1])
    with col1:
        st.markdown(
            """
            <div class="card">
              <h3 style="margin-top:0">¿Qué mide?</h3>
              <ul style="margin-top:6px; line-height:1.6">
                <li><b>O</b> – Apertura a la Experiencia</li>
                <li><b>C</b> – Responsabilidad</li>
                <li><b>E</b> – Extraversión</li>
                <li><b>A</b> – Amabilidad</li>
                <li><b>N</b> – Estabilidad Emocional</li>
              </ul>
              <p style="opacity:.9">Duración estimada: <b>8–12 min</b> · 50 ítems Likert (1–5) · Avance automático al responder.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="card">
              <h3 style="margin-top:0">Cómo funciona</h3>
              <ol style="margin-top:6px; line-height:1.6">
                <li>Verás una pregunta por pantalla.</li>
                <li>Elige tu opción (1 a 5) y pasarás automáticamente.</li>
                <li>Al finalizar, verás resultados, KPIs y podrás descargar PDF.</li>
              </ol>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("🚀 Iniciar evaluación", type="primary", use_container_width=True):
            st.session_state.stage = "test"
            st.session_state.q_index = 0
            scroll_top()

def view_test():
    scroll_top()
    i = st.session_state.q_index
    p = PREGUNTAS[i]
    dim = p["dim"]
    code = DIMENSIONES[dim]["code"]

    # Progreso
    pct = (i+1)/len(PREGUNTAS)
    st.progress(pct, text=f"Progreso: {i+1}/{len(PREGUNTAS)} preguntas")

    # Título de dimensión (grande y animado)
    st.markdown(f"<div class='dim-title'>{code} — {dim}</div>", unsafe_allow_html=True)
    st.caption(DIMENSIONES[dim]["desc"])
    st.markdown("---")

    # Pregunta (una por vez)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {i+1}. {p['text']}")

    prev = st.session_state.answers.get(p["key"])
    prev_index = None if prev is None else LIKERT_KEYS.index(prev)

    st.radio(
        "Selecciona una opción",
        options=LIKERT_KEYS,
        index=prev_index,
        format_func=lambda x: LIKERT[x],
        key=f"resp_{p['key']}",
        horizontal=True,
        label_visibility="collapsed",
        on_change=on_answer_change
    )
    st.markdown("</div>", unsafe_allow_html=True)

def view_resultados():
    scroll_top()
    results = compute_scores(st.session_state.answers)
    order = list(results.keys())
    values = [results[d] for d in order]
    promedio_total = round(float(np.mean(values)), 1)
    dispersion = round(float(np.std(values, ddof=1)), 2) if len(values) > 1 else 0.0
    rango = round(float(np.max(values) - np.min(values)), 2)

    # Encabezado + KPIs
    st.markdown("<div id='report-root'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card" style="padding:26px; border-radius:16px; margin-bottom:18px;">
          <h1 style="margin:0 0 6px 0; font-size:clamp(1.9rem,3.8vw,2.8rem); font-weight:900;">📊 Informe de Personalidad Big Five</h1>
          <p style="margin:0; font-size:1.05rem; opacity:.9;">Fecha de evaluación: <b>{st.session_state.fecha_eval}</b></p>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{promedio_total:.1f}</div><div class='l'>Promedio general (0–100)</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{dispersion:.2f}</div><div class='l'>Desviación estándar</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{rango:.2f}</div><div class='l'>Rango</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{max(results, key=results.get)}</div><div class='l'>Dimensión destacada</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Colores suaves para gráficos (sin azules fuertes)
    palette = ["#E07A5F", "#81B29A", "#F2CC8F", "#9C6644", "#6D597A"]

    # Radar
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=[f"{DIMENSIONES[d]['code']} {d}" for d in order],
        fill='toself',
        name='Perfil',
        line=dict(width=2, color="#6D597A"),
        fillcolor='rgba(109, 89, 122, 0.12)',
        marker=dict(size=7, color="#6D597A")
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, height=520, template="plotly_white"
    )

    # Barras
    dfb = pd.DataFrame({"Dimensión": order, "Puntuación": values}).sort_values("Puntuación", ascending=True)
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=dfb["Dimensión"], x=dfb["Puntuación"],
        orientation='h',
        marker=dict(color=[palette[i % len(palette)] for i in range(len(dfb))]),
        text=[f"{v:.1f}" for v in dfb["Puntuación"]],
        textposition="outside"
    ))
    fig_bar.update_layout(
        height=520, template="plotly_white",
        xaxis=dict(range=[0, 105], title="Puntuación (0-100)"),
        yaxis=dict(title="")
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Radar del perfil")
        st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")
    with c2:
        st.subheader("📊 Puntuaciones por dimensión")
        st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")

    st.markdown("---")
    st.subheader("📋 Resumen de resultados")
    tabla = pd.DataFrame({
        "Código": [DIMENSIONES[d]["code"] for d in order],
        "Dimensión": order,
        "Puntuación": [f"{results[d]:.1f}" for d in order],
        "Nivel": [label_level(results[d])[0] for d in order],
        "Etiqueta": [label_level(results[d])[1] for d in order],
    })
    st.dataframe(tabla, use_container_width=True, hide_index=True, key="df_resumen")

    st.markdown("---")
    st.subheader("🔍 Análisis cualitativo por dimensión")

    # Bloques por dimensión con gauge + pros/contras/cargos (keys únicos)
    for idx, d in enumerate(DIMENSIONES_LIST):
        score = results[d]
        lvl, tag = label_level(score)
        info = DIMENSIONES[d]
        with st.expander(f"{info['code']} — {d}: {score:.1f} ({lvl})", expanded=True):
            colA, colB = st.columns([1, 2])
            with colA:
                gauge = go.Figure()
                gauge.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#E07A5F"},
                        "bgcolor": "white",
                        "borderwidth": 1,
                        "bordercolor": "#eaeaea",
                        "steps": [
                            {"range": [0, 25], "color": "#f7ede2"},
                            {"range": [25, 40], "color": "#f3e7d3"},
                            {"range": [40, 60], "color": "#efe1c5"},
                            {"range": [60, 75], "color": "#e9dbc0"},
                            {"range": [75, 100], "color": "#e4d4b8"},
                        ],
                    },
                    number={"font": {"size": 36}}
                ))
                gauge.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(gauge, use_container_width=True, key=f"gauge_{info['code']}_{idx}")

            with colB:
                st.markdown(f"**Descripción**: {info['desc']}")
                st.markdown(f"**Nivel**: **{lvl}** · **{tag}**")

                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.markdown("**Fortalezas**")
                    st.markdown("<ul>" + "".join([f"<li>{p}</li>" for p in info["pros"]]) + "</ul>", unsafe_allow_html=True)
                with cc2:
                    st.markdown("**Oportunidades**")
                    st.markdown("<ul>" + "".join([f"<li>{c}</li>" for c in info["contras"]]) + "</ul>", unsafe_allow_html=True)
                with cc3:
                    st.markdown("**Cargos sugeridos**")
                    st.markdown("<ul>" + "".join([f"<li>{c}</li>" for c in info["cargos"]]) + "</ul>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📥 Exportar informe (PDF)")
    st.caption("El archivo incluye los gráficos y todo lo visible en esta página de resultados.")

    st.markdown("""
    <div class="card">
      <button id="btn-pdf" class="btn-primary">Descargar PDF</button>
      <span style="margin-left:10px; opacity:.8;">Si no descarga, espera un segundo y vuelve a intentar.</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # cierre #report-root

    # Carga de librerías y generación PDF en cliente (sin libs server)
    st.markdown("""
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>
    <script>
      const clickBtn = () => {
        const { jsPDF } = window.jspdf;
        const target = document.querySelector('#report-root');
        if (!target) return;
        html2canvas(target, {scale: 2, backgroundColor: '#ffffff'}).then(canvas => {
            const imgData = canvas.toDataURL('image/png', 1.0);
            const pdf = new jsPDF('p', 'pt', 'a4');
            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();
            const imgWidth = pageWidth;
            const imgHeight = canvas.height * imgWidth / canvas.width;
            if (imgHeight <= pageHeight) {
                pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
            } else {
                let heightLeft = imgHeight;
                let y = 0;
                while (heightLeft > 0) {
                    pdf.addImage(imgData, 'PNG', 0, y, imgWidth, imgHeight);
                    heightLeft -= pageHeight;
                    y -= pageHeight;
                    if (heightLeft > 0) pdf.addPage();
                }
            }
            pdf.save('Informe_BigFive.pdf');
        });
      };
      setTimeout(() => {
        const btn = window.parent.document.querySelector('#btn-pdf') || document.querySelector('#btn-pdf');
        if (btn) btn.onclick = clickBtn;
      }, 500);
    </script>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Realizar nueva evaluación", type="primary", use_container_width=True):
        restart()

# ==============================
# FLOW
# ==============================
if st.session_state.stage == "inicio":
    view_inicio()
elif st.session_state.stage == "test":
    view_test()
else:
    view_resultados()
