# streamlit_app.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import random
from math import erf, sqrt

# ========== 0) CONFIG ==========
st.set_page_config(
    page_title="Big Five (OCEAN) | Evaluación Profesional",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo minimal: blanco / negro
MINIMAL_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] {
  background: #ffffff !important;
  color: #111 !important;
}
h1, h2, h3, h4, h5, h6, p, label, span, div { color: #111 !important; }
.block-container { padding-top: 1.5rem; }
.metric-card {
  border: 1px solid #eaeaea; border-radius: 14px; padding: 16px; background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,.05);
}
.dim-badge {
  display:inline-block; border:1px solid #e3e3e3; border-radius:12px; padding:3px 10px; font-size:12px;
}
.stRadio > div { gap: .75rem; }
[data-baseweb="radio"] label { color: #111; }
hr { border: none; border-top: 1px solid #eee; margin: 1.2rem 0; }
.small { font-size:.92rem; color:#333 !important; }
.muted { color:#666 !important; }
.badge {
  border:1px solid #e3e3e3; border-radius: 999px; padding:2px 10px; font-size:.75rem; margin-left:6px;
}
.question-card {
  border:1px solid #eee; border-radius:12px; padding:14px; margin-bottom:10px;
  background:#fff;
}
</style>
"""
st.markdown(MINIMAL_CSS, unsafe_allow_html=True)
st.markdown("<a id='top'></a>", unsafe_allow_html=True)

# ========== 1) DATA MODEL ==========
DIMENSIONES = {
    "Apertura a la Experiencia": {"code": "O", "icon": "💡"},
    "Responsabilidad": {"code": "C", "icon": "🎯"},
    "Extraversión": {"code": "E", "icon": "🗣️"},
    "Amabilidad": {"code": "A", "icon": "🤝"},
    "Estabilidad Emocional": {"code": "N", "icon": "🧘"},  # (opuesto a Neuroticismo)
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
        ("Disfruto ser el centro de atención a veces.", False),
        ("Prefiero estar solo la mayor parte del tiempo.", True),
        ("Soy reservado y callado.", True),
        ("Evito reuniones sociales prolongadas.", True),
        ("Me incomodan los desconocidos.", True),
        ("Prefiero trabajar en segundo plano.", True),
    ])
    add("Amabilidad", "A", [
        ("Empatizo con facilidad con los demás.", False),
        ("Confío en las buenas intenciones de la gente.", False),
        ("Colaboro y doy apoyo a mi equipo.", False),
        ("Trato a las personas con respeto y cortesía.", False),
        ("Me esfuerzo por resolver conflictos.", False),
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

# Indices de inicio/fin por dimensión (para modo secciones)
DIM_RANGES = {}
start = 0
for dim in DIM_LIST:
    DIM_RANGES[dim] = (start, start + 10)  # 10 ítems por dimensión
    start += 10

# ========== 2) STATE ==========
if "stage" not in st.session_state:
    st.session_state.stage = "inicio"            # inicio | test | resultados
if "mode" not in st.session_state:
    st.session_state.mode = "1x1"                # "1x1" | "secciones"
if "q_index" not in st.session_state:
    st.session_state.q_index = 0                 # índice global 0..49 (para modo 1x1)
if "sec_index" not in st.session_state:
    st.session_state.sec_index = 0               # 0..4 (para modo secciones)
if "answers" not in st.session_state:
    st.session_state.answers = {q["key"]: None for q in PREGUNTAS}
if "started_at" not in st.session_state:
    st.session_state.started_at = None
if "finished_at" not in st.session_state:
    st.session_state.finished_at = None

# helpers
def current_question():
    return PREGUNTAS[st.session_state.q_index]

def go_results():
    st.session_state.stage = "resultados"
    st.session_state.finished_at = datetime.now().strftime("%Y-%m-%d %H:%M")

def reset_all():
    st.session_state.stage = "inicio"
    st.session_state.mode = st.session_state.mode  # mantiene modo actual
    st.session_state.q_index = 0
    st.session_state.sec_index = 0
    st.session_state.answers = {q["key"]: None for q in PREGUNTAS}
    st.session_state.started_at = None
    st.session_state.finished_at = None

# ========== 3) SCORING ==========
def compute_scores(answers: dict) -> dict:
    buckets = {d: [] for d in DIM_LIST}
    for q in PREGUNTAS:
        val = answers.get(q["key"])
        if val is None:
            continue
        score_1_5 = reverse_score(val) if q["reverse"] else val
        buckets[q["dim"]].append(score_1_5)
    for d in DIM_LIST:
        if len(buckets[d]) < 10:
            buckets[d] += [3] * (10 - len(buckets[d]))
    scores_0_100 = {d: round(((np.mean(buckets[d]) - 1) / 4) * 100, 1) for d in DIM_LIST}
    return scores_0_100

def interprete(score):
    if score >= 75: return "Muy alto", "Dominante"
    if score >= 60: return "Alto", "Marcado"
    if score >= 40: return "Promedio", "Moderado"
    if score >= 25: return "Bajo", "Suave"
    return "Muy bajo", "Mínimo"

# ========== 4) SIDEBAR ==========
with st.sidebar:
    st.markdown("### 🧠 Big Five (OCEAN)")
    st.markdown("<span class='muted'>Modo visual minimal (blanco/negro)</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.selectbox(
        "Modo de aplicación",
        options=["Pregunta por pregunta (auto-avance)", "Por secciones (10 por dimensión)"],
        index=(0 if st.session_state.mode == "1x1" else 1),
        key="mode_selector",
        help="Puedes cambiar el modo antes o durante el test.",
    )
    st.session_state.mode = "1x1" if st.session_state.mode_selector.startswith("Pregunta") else "secciones"

    if st.session_state.stage != "resultados":
        total = len(PREGUNTAS)
        if st.session_state.mode == "1x1":
            idx = st.session_state.q_index
            pct = int((idx / total) * 100)
            st.progress(pct/100, text=f"Progreso: {idx}/{total} ({pct}%)")
            if st.session_state.stage == "test":
                q = current_question()
                st.markdown(f"**Dimensión actual**: {DIMENSIONES[q['dim']]['icon']} {q['dim']}")
                st.caption(f"Ítem {idx+1} de {total}")
        else:
            sidx = st.session_state.sec_index
            dim = DIM_LIST[sidx]
            a, b = DIM_RANGES[dim]
            answered = sum(1 for i in range(a, b) if st.session_state.answers[PREGUNTAS[i]["key"]] is not None)
            st.progress(answered/10, text=f"{DIMENSIONES[dim]['icon']} {dim} — {answered}/10 respondidas")
            st.caption(f"Sección {sidx+1} de 5")

        st.markdown("---")
        if st.button("🎲 Completar al azar", use_container_width=True):
            st.session_state.answers = {q["key"]: random.choice(LIKERT) for q in PREGUNTAS}
            go_results()
            st.rerun()

        if st.button("🔄 Reiniciar", use_container_width=True):
            reset_all()
            st.rerun()
    else:
        st.success("Test completado")
        st.markdown(f"**Finalizado:** {st.session_state.finished_at or ''}")
        if st.button("🔁 Nuevo test", use_container_width=True):
            reset_all()
            st.rerun()

# ========== 5) PANTALLAS ==========
def pantalla_inicio():
    st.title("Test de Personalidad Big Five (OCEAN)")
    st.subheader("Evaluación profesional de los Cinco Grandes factores de personalidad")
    st.write(
        "Responde **50 afirmaciones** en una escala de 1 a 5. "
        "Puedes usar el modo **pregunta por pregunta (auto-avance)** o **por secciones (10 por dimensión)**."
    )
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown("#### ¿Qué mide?")
        st.markdown(
            "- **O**: Apertura a la Experiencia  \n"
            "- **C**: Responsabilidad  \n"
            "- **E**: Extraversión  \n"
            "- **A**: Amabilidad  \n"
            "- **N**: Estabilidad Emocional"
        )
    with c2:
        st.markdown("#### Escala de respuesta")
        for k in LIKERT:
            st.markdown(f"- **{k}**: {LIKERT_LABELS[k]}")
    with c3:
        st.markdown("#### Modo rápido")
        st.markdown("En la barra lateral puedes **completar al azar** y saltar directo a **Resultados**.")

    st.markdown("---")
    if st.button("🚀 Comenzar ahora", type="primary"):
        st.session_state.stage = "test"
        st.session_state.started_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.rerun()

# ---- Modo 1x1 (auto-avance) ----
def pantalla_test_1x1():
    q = current_question()
    idx = st.session_state.q_index
    total = len(PREGUNTAS)
    dim = q["dim"]
    code = DIMENSIONES[dim]["code"]
    icon = DIMENSIONES[dim]["icon"]

    st.markdown(f"<div class='dim-badge'>{icon} {code} — {dim}</div>", unsafe_allow_html=True)
    st.title(f"Pregunta {idx+1} de {total}")
    st.write(q["text"])
    st.caption("Selecciona una opción para avanzar automáticamente")

    def _on_select():
        if st.session_state.q_index < total - 1:
            st.session_state.q_index += 1
            st.rerun()
        else:
            go_results()
            st.rerun()

    current_val = st.session_state.answers.get(q["key"], None)
    st.radio(
        "Tu respuesta",
        options=LIKERT,
        index=(LIKERT.index(current_val) if current_val in LIKERT else None),
        format_func=lambda k: f"{k} — {LIKERT_LABELS[k]}",
        key=f"radio_{q['key']}",
        horizontal=True,
        label_visibility="collapsed",
        on_change=lambda: (
            st.session_state.answers.__setitem__(q["key"], st.session_state[f"radio_{q['key']}"]),
            _on_select()
        )
    )

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1,1,4,1])
    with cols[0]:
        if st.session_state.q_index > 0 and st.button("⬅️ Anterior", use_container_width=True):
            st.session_state.q_index -= 1
            st.rerun()
    with cols[1]:
        if st.button("⏭️ Saltar (marca Neutral)", use_container_width=True):
            st.session_state.answers[q["key"]] = 3
            _on_select()
    with cols[-1]:
        st.caption(f"{idx+1}/{total}")

# ---- Modo secciones (10 por dimensión) ----
def pantalla_test_secciones():
    sidx = st.session_state.sec_index
    dim = DIM_LIST[sidx]
    code = DIMENSIONES[dim]["code"]
    icon = DIMENSIONES[dim]["icon"]
    a, b = DIM_RANGES[dim]
    subset = PREGUNTAS[a:b]

    st.markdown(f"<div class='dim-badge'>{icon} {code} — {dim}</div>", unsafe_allow_html=True)
    st.title(f"Sección {sidx+1} de 5 — {dim}")
    st.caption("Responde las 10 afirmaciones de esta dimensión")

    with st.form(f"form_{dim}"):
        answered = 0
        for q in subset:
            with st.container():
                st.markdown(f"<div class='question-card'><b>{q['text']}</b></div>", unsafe_allow_html=True)
                key_r = f"radio_{q['key']}"
                current_val = st.session_state.answers.get(q["key"], None)
                sel = st.radio(
                    q["text"],
                    options=LIKERT,
                    index=(LIKERT.index(current_val) if current_val in LIKERT else None),
                    format_func=lambda k: f"{k} — {LIKERT_LABELS[k]}",
                    key=key_r,
                    horizontal=True,
                    label_visibility="collapsed",
                )
                if sel is not None:
                    st.session_state.answers[q["key"]] = sel
                    answered += 1

        st.progress(answered/10, text=f"Respondidas: {answered}/10")

        c1, c2, c3 = st.columns([1,1,6])
        with c1:
            back = st.form_submit_button("⬅️ Sección anterior", use_container_width=True)
        with c2:
            nxt = st.form_submit_button(("✅ Finalizar" if sidx == 4 else "➡️ Siguiente sección"), use_container_width=True)

    # navegación secciones
    if back:
        if sidx > 0:
            st.session_state.sec_index -= 1
            st.rerun()
    if nxt:
        if answered < 10:
            st.warning("Por favor, responde las 10 afirmaciones antes de continuar.")
        else:
            if sidx < 4:
                st.session_state.sec_index += 1
                st.rerun()
            else:
                go_results()
                st.rerun()

# ---- Resultados ----
def pantalla_resultados():
    st.title("Resultados del Test Big Five (OCEAN)")
    st.caption(f"Inicio: {st.session_state.started_at or '-'}  •  Fin: {st.session_state.finished_at or '-'}")

    scores = compute_scores(st.session_state.answers)
    order = list(scores.keys())
    values = [scores[d] for d in order]

    # Métricas ejecutivas
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Promedio global (0-100)", f"{np.mean(values):.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Desv. estándar", f"{np.std(values, ddof=1):.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Dimensión más alta", max(scores, key=scores.get))
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Dimensión más baja", min(scores, key=scores.get))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Visualizaciones
    st.subheader("Visualizaciones")
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=[f"{DIMENSIONES[d]['code']} {d}" for d in order],
        fill='toself', name='Perfil',
        line=dict(width=2, color="#111"),
        fillcolor='rgba(17,17,17,0.08)', marker=dict(size=7, color="#111")
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=520, template="plotly_white")

    df_bar = pd.DataFrame({"Dimensión": order, "Puntuación": values}).sort_values("Puntuación", ascending=True)
    fig_bar = px.bar(df_bar, x="Puntuación", y="Dimensión", orientation="h", text="Puntuación")
    fig_bar.update_traces(texttemplate="%{x:.1f}", marker_color="#111")
    fig_bar.update_layout(height=520, template="plotly_white")

    ref = 50
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=order, y=values, name="Tu perfil", marker_color="#111", text=[f"{v:.1f}" for v in values], textposition="outside"))
    fig_comp.add_trace(go.Bar(x=order, y=[ref]*5, name="Promedio referencia (50)", marker_color="#aaa", text=["50"]*5, textposition="outside"))
    fig_comp.update_layout(barmode="group", height=520, template="plotly_white", legend_orientation="h")

    t1, t2, t3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])
    with t1: st.plotly_chart(fig_radar, use_container_width=True)
    with t2: st.plotly_chart(fig_bar, use_container_width=True)
    with t3: st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # Estadísticos y percentiles
    st.subheader("Estadísticos por dimensión")
    MU, SIG = 50, 15
    def z(x): return (x - MU) / SIG
    def cdf_norm(x): return 0.5 * (1 + erf(x / sqrt(2)))

    table = []
    for d in DIM_LIST:
        s = scores[d]; Z = z(s); pct = round(cdf_norm(Z) * 100, 1)
        nivel, etiqueta = interprete(s)
        table.append([DIMENSIONES[d]["code"], d, s, Z, pct, f"{nivel} ({etiqueta})"])
    df = pd.DataFrame(table, columns=["Código", "Dimensión", "Puntuación (0-100)", "z-score", "Percentil (%)", "Clasificación"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Distribución ilustrativa
    st.markdown("#### Distribución ilustrativa (ref. μ=50, σ=15)")
    gcol = st.columns(5)
    xs = np.linspace(0, 100, 200)
    ys = (1/(SIG*np.sqrt(2*np.pi))) * np.exp(-0.5*((xs-MU)/SIG)**2)
    for i, d in enumerate(DIM_LIST):
        with gcol[i]:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Referencia", line=dict(color="#aaa")))
            yv = (1/(SIG*np.sqrt(2*np.pi))) * np.exp(-0.5*((scores[d]-MU)/SIG)**2)
            fig.add_trace(go.Scatter(x=[scores[d]], y=[yv], mode="markers", marker=dict(size=10, color="#111"), name="Tú"))
            fig.update_layout(height=220, margin=dict(l=20,r=10,t=10,b=20), xaxis_title=DIMENSIONES[d]["code"], yaxis_title="", template="plotly_white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Interpretaciones cualitativas
    st.subheader("Análisis cualitativo por dimensión")
    INTERP = {
        "Apertura a la Experiencia": {
            "alta": ["Curiosidad intelectual", "Pensamiento creativo", "Flexibilidad cognitiva"],
            "baja": ["Preferencia por lo conocido", "Orientación práctica", "Adherencia a procesos"],
            "roles_alta": ["Innovación", "I+D", "Diseño", "Estrategia"],
            "roles_baja": ["Operaciones", "Calidad", "Procesos", "Compliance"],
        },
        "Responsabilidad": {
            "alta": ["Planificación y orden", "Seguimiento y disciplina", "Orientación a objetivos"],
            "baja": ["Espontaneidad", "Adaptación rápida", "Exploración sin estructura"],
            "roles_alta": ["Gestión de Proyectos", "Auditoría", "Finanzas", "PMO"],
            "roles_baja": ["Creativo freelance", "Exploración UX", "Labs de prototipado"],
        },
        "Extraversión": {
            "alta": ["Energía social", "Asertividad", "Networking"],
            "baja": ["Enfoque profundo", "Trabajo independiente", "Comunicación escrita"],
            "roles_alta": ["Ventas", "Relaciones Públicas", "Liderazgo de equipos"],
            "roles_baja": ["Análisis de datos", "Investigación", "Desarrollo de software"],
        },
        "Amabilidad": {
            "alta": ["Empatía", "Cooperación", "Gestión de conflictos"],
            "baja": ["Claridad directa", "Negociación dura", "Objetividad fría"],
            "roles_alta": ["RR. HH.", "Atención al Cliente", "Mediación"],
            "roles_baja": ["Negociación B2B", "Consultoría estratégica", "Gestión de riesgo"],
        },
        "Estabilidad Emocional": {
            "alta": ["Calma bajo presión", "Resiliencia", "Decisiones serenas"],
            "baja": ["Sensibilidad al estrés", "Vulnerabilidad emocional", "Reactividad"],
            "roles_alta": ["Crisis/Operaciones", "Liderazgo ejecutivo", "Salud y seguridad"],
            "roles_baja": ["Entornos predecibles", "Trabajo artesanal", "Producción tranquila"],
        },
    }
    for d in DIM_LIST:
        s = scores[d]
        nivel, etiqueta = interprete(s)
        with st.expander(f"{DIMENSIONES[d]['icon']} {d} — {s:.1f} ({nivel})", expanded=True):
            c1, c2 = st.columns([1,2])
            with c1:
                st.markdown("**Rasgos sobresalientes**")
                st.write(", ".join(INTERP[d]["alta"] if s>=60 else INTERP[d]["baja"]))
                st.markdown("**Sugerencias de entornos**")
                st.write(", ".join(INTERP[d]["roles_alta"] if s>=60 else INTERP[d]["roles_baja"]))
            with c2:
                st.markdown("**Recomendaciones prácticas**")
                if d == "Responsabilidad" and s < 60:
                    st.write("- Listas priorizadas y timeboxing.\n- Hitos pequeños.\n- Revisión semanal.")
                elif d == "Extraversión" and s < 60:
                    st.write("- Comunicación asincrónica.\n- Bloques de foco.\n- Ensayos grabados.")
                elif d == "Amabilidad" and s < 60:
                    st.write("- Feedback asertivo.\n- Criterios objetivos previos a negociar.\n- Escucha activa estructurada.")
                elif d == "Apertura a la Experiencia" and s < 60:
                    st.write("- Mejoras incrementales.\n- Experimentar en sandbox.\n- Usar plantillas antes de innovar.")
                elif d == "Estabilidad Emocional" and s < 60:
                    st.write("- Rutinas de recuperación.\n- Diario de estrés.\n- Planes A/B.")
                else:
                    st.write("- Mantén y comparte prácticas efectivas.\n- Apoya a otros.\n- Documenta tus métodos.")

    st.markdown("---")

    # Descargas
    st.subheader("Descargar resultados")
    export_df = df.copy()
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    json_bytes = export_df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "📄 Descargar CSV",
            data=csv_bytes,
            file_name=f"BigFive_Resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "🧾 Descargar JSON",
            data=json_bytes,
            file_name=f"BigFive_Resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")
    st.caption("**Aviso**: Este informe es orientativo y depende de respuestas autorreportadas. No sustituye evaluaciones clínicas o procesos formales de selección.")

# ========== 6) ROUTER ==========
if st.session_state.stage == "inicio":
    pantalla_inicio()
elif st.session_state.stage == "test":
    if st.session_state.mode == "1x1":
        pantalla_test_1x1()
    else:
        pantalla_test_secciones()
else:
    pantalla_resultados()
