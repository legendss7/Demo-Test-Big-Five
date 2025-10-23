# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
from datetime import datetime

# --------- OPCIONAL: PDF (auto-fallback) ----------
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False
# ---------------------------------------------------

# ================== CONFIG APP ==================
st.set_page_config(
    page_title="Big Five Pro Max | Evaluación Profesional",
    page_icon="🧠",
    layout="wide"
)

# ======== ESTILOS (blanco/negro, corporativo) ========
st.markdown("""
<style>
/* Fondo blanco y tipografía negra */
html, body, [data-testid="stAppViewContainer"] {
  background: #ffffff !important;
  color: #111 !important;
}

/* Títulos sobrios */
h1, h2, h3, h4, h5, h6 { color: #111; }

/* Tarjetas / contenedores */
.card {
  background: #fff;
  border: 1px solid #e9e9e9;
  border-radius: 14px;
  padding: 22px 22px;
  box-shadow: 0 3px 14px rgba(0,0,0,0.05);
}

/* Botones */
button[kind="primary"] {
  background: #111 !important;
  color: #fff !important;
  border: 1px solid #111 !important;
}
button[kind="secondary"] {
  background: #fff !important;
  color: #111 !important;
  border: 1px solid #111 !important;
}

/* Radio horizontal con más separación */
[data-testid="stRadio"] > div {
  gap: 8px;
}

/* Métricas compactas */
.metric-box {
  border: 1px solid #eee; border-radius: 12px; padding: 16px;
}
.small {
  font-size: 0.9rem; color:#444;
}
.caption-quiet {
  color:#666; font-size:0.85rem;
}
hr { border: none; border-top: 1px solid #eee; margin: 6px 0 18px 0;}
</style>
""", unsafe_allow_html=True)

# ====== DATA: Dimensiones, escala, preguntas ======
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O",
        "desc": "Imaginación, curiosidad intelectual, creatividad y aprecio por el arte y las nuevas experiencias.",
        "altas": "Creativo, curioso, aventurero, con mente abierta.",
        "bajas": "Práctico, enfocado en lo concreto, prefiere lo familiar."
    },
    "Responsabilidad": {
        "code": "C",
        "desc": "Autodisciplina, organización, cumplimiento de objetivos y sentido del deber.",
        "altas": "Organizado, confiable, disciplinado, planificado.",
        "bajas": "Flexible, espontáneo, le cuesta la estructura."
    },
    "Extraversión": {
        "code": "E",
        "desc": "Sociabilidad, asertividad, energía y búsqueda de estimulación social.",
        "altas": "Sociable, enérgico, expresivo.",
        "bajas": "Reservado, introspectivo, prefiere entornos tranquilos."
    },
    "Amabilidad": {
        "code": "A",
        "desc": "Cooperación, empatía, compasión, confianza y respeto.",
        "altas": "Colaborativo, empático, prosocial.",
        "bajas": "Competitivo, directo, objetivo."
    },
    "Estabilidad Emocional": {
        "code": "N",
        "desc": "Capacidad para mantener la calma y gestionar el estrés (opuesto a Neuroticismo).",
        "altas": "Sereno, estable, resiliente.",
        "bajas": "Sensible, ansioso, reactivo."
    },
}
DIM_KEYS = list(DIMENSIONES.keys())

ESCALA_LIKERT = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}
LIKERT = list(ESCALA_LIKERT.keys())

def reverse_score(x: int) -> int:
    return 6 - x

# 10 preguntas por dimensión (5 directas, 5 inversas)
PREGUNTAS = [
    # O
    {"key": "O1", "dim": DIM_KEYS[0], "text": "Tengo una imaginación muy activa.", "rev": False},
    {"key": "O2", "dim": DIM_KEYS[0], "text": "Me entusiasma aprender ideas complejas.", "rev": False},
    {"key": "O3", "dim": DIM_KEYS[0], "text": "Me atraen el arte y la cultura.", "rev": False},
    {"key": "O4", "dim": DIM_KEYS[0], "text": "Disfruto experimentar con enfoques novedosos.", "rev": False},
    {"key": "O5", "dim": DIM_KEYS[0], "text": "Valoro la creatividad y lo original.", "rev": False},
    {"key": "O6", "dim": DIM_KEYS[0], "text": "Prefiero la rutina a probar cosas nuevas.", "rev": True},
    {"key": "O7", "dim": DIM_KEYS[0], "text": "Me aburren las discusiones teóricas.", "rev": True},
    {"key": "O8", "dim": DIM_KEYS[0], "text": "Rara vez reflexiono sobre temas abstractos.", "rev": True},
    {"key": "O9", "dim": DIM_KEYS[0], "text": "Prefiero lo convencional a lo original.", "rev": True},
    {"key": "O10","dim": DIM_KEYS[0], "text": "No me gusta cambiar hábitos establecidos.", "rev": True},

    # C
    {"key": "C1", "dim": DIM_KEYS[1], "text": "Planifico antes de actuar.", "rev": False},
    {"key": "C2", "dim": DIM_KEYS[1], "text": "Cuido los detalles.", "rev": False},
    {"key": "C3", "dim": DIM_KEYS[1], "text": "Cumplo compromisos y plazos.", "rev": False},
    {"key": "C4", "dim": DIM_KEYS[1], "text": "Mantengo mis tareas ordenadas.", "rev": False},
    {"key": "C5", "dim": DIM_KEYS[1], "text": "Soy persistente con objetivos difíciles.", "rev": False},
    {"key": "C6", "dim": DIM_KEYS[1], "text": "Dejo cosas sin terminar.", "rev": True},
    {"key": "C7", "dim": DIM_KEYS[1], "text": "Evito responsabilidades cuando puedo.", "rev": True},
    {"key": "C8", "dim": DIM_KEYS[1], "text": "Me distraigo fácilmente.", "rev": True},
    {"key": "C9", "dim": DIM_KEYS[1], "text": "Desordeno mi espacio de trabajo.", "rev": True},
    {"key": "C10","dim": DIM_KEYS[1], "text": "Procrastino tareas importantes.", "rev": True},

    # E
    {"key": "E1", "dim": DIM_KEYS[2], "text": "Me energizan los entornos sociales.", "rev": False},
    {"key": "E2", "dim": DIM_KEYS[2], "text": "Hablo con soltura ante grupos.", "rev": False},
    {"key": "E3", "dim": DIM_KEYS[2], "text": "Busco activamente la compañía de otros.", "rev": False},
    {"key": "E4", "dim": DIM_KEYS[2], "text": "Iniciar conversaciones me resulta natural.", "rev": False},
    {"key": "E5", "dim": DIM_KEYS[2], "text": "Me siento cómodo con desconocidos.", "rev": False},
    {"key": "E6", "dim": DIM_KEYS[2], "text": "Prefiero estar solo a menudo.", "rev": True},
    {"key": "E7", "dim": DIM_KEYS[2], "text": "Soy una persona reservada.", "rev": True},
    {"key": "E8", "dim": DIM_KEYS[2], "text": "Evito ser el centro de atención.", "rev": True},
    {"key": "E9", "dim": DIM_KEYS[2], "text": "Me agotan las interacciones prolongadas.", "rev": True},
    {"key": "E10","dim": DIM_KEYS[2], "text": "Me cuesta expresarme en grupos grandes.", "rev": True},

    # A
    {"key": "A1", "dim": DIM_KEYS[3], "text": "Me preocupo genuinamente por otros.", "rev": False},
    {"key": "A2", "dim": DIM_KEYS[3], "text": "Trato a las personas con respeto.", "rev": False},
    {"key": "A3", "dim": DIM_KEYS[3], "text": "Ofrezco ayuda sin esperar retorno.", "rev": False},
    {"key": "A4", "dim": DIM_KEYS[3], "text": "Confío en la buena fe de la gente.", "rev": False},
    {"key": "A5", "dim": DIM_KEYS[3], "text": "Evito conflictos y facilito acuerdos.", "rev": False},
    {"key": "A6", "dim": DIM_KEYS[3], "text": "La gente me resulta indiferente.", "rev": True},
    {"key": "A7", "dim": DIM_KEYS[3], "text": "Soy cínico con las intenciones ajenas.", "rev": True},
    {"key": "A8", "dim": DIM_KEYS[3], "text": "A veces soy insensible sin querer.", "rev": True},
    {"key": "A9", "dim": DIM_KEYS[3], "text": "Primero pienso en mis objetivos.", "rev": True},
    {"key": "A10","dim": DIM_KEYS[3], "text": "Me cuesta empatizar con problemas ajenos.", "rev": True},

    # N (Estabilidad Emocional)
    {"key": "N1", "dim": DIM_KEYS[4], "text": "Mantengo la calma bajo presión.", "rev": False},
    {"key": "N2", "dim": DIM_KEYS[4], "text": "Gestiono bien el estrés.", "rev": False},
    {"key": "N3", "dim": DIM_KEYS[4], "text": "Me recupero rápido ante contratiempos.", "rev": False},
    {"key": "N4", "dim": DIM_KEYS[4], "text": "Suelo sentirme seguro de mí mismo.", "rev": False},
    {"key": "N5", "dim": DIM_KEYS[4], "text": "Tengo buena regulación emocional.", "rev": False},
    {"key": "N6", "dim": DIM_KEYS[4], "text": "Me preocupo en exceso por cosas.", "rev": True},
    {"key": "N7", "dim": DIM_KEYS[4], "text": "Me irrito con facilidad.", "rev": True},
    {"key": "N8", "dim": DIM_KEYS[4], "text": "A menudo me siento decaído.", "rev": True},
    {"key": "N9", "dim": DIM_KEYS[4], "text": "Tengo cambios de humor frecuentes.", "rev": True},
    {"key": "N10","dim": DIM_KEYS[4], "text": "El estrés me abruma con facilidad.", "rev": True},
]

# ============== SESSION STATE ==============
if "stage" not in st.session_state:
    st.session_state.stage = "test"  # test | results
if "answers" not in st.session_state:
    st.session_state.answers = {q["key"]: None for q in PREGUNTAS}
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "fecha_eval" not in st.session_state:
    st.session_state.fecha_eval = None
if "scroll_key" not in st.session_state:
    st.session_state.scroll_key = 0

# ======= UTILS =======
def scroll_top():
    # “nudges” the browser to go arriba sin azul ni libs extras
    st.session_state.scroll_key += 1
    st.components.v1.html(
        f"""
        <script>
          setTimeout(() => {{
            window.parent.scrollTo({{top:0, behavior:'auto'}});
          }}, 45);
        </script>
        """,
        height=0,
        key=f"scroll_{st.session_state.scroll_key}"
    )

def calc_scores(answers: dict) -> dict:
    # 1..5 -> promedio -> 0..100
    by_dim = {d: [] for d in DIM_KEYS}
    for q in PREGUNTAS:
        v = answers.get(q["key"])
        if v is None:  # nulos como neutral
            v = 3
        if q["rev"]:
            v = reverse_score(v)
        by_dim[q["dim"]].append(v)
    out = {}
    for d, vals in by_dim.items():
        avg = np.mean(vals)
        pct = (avg - 1) / 4 * 100.0
        out[d] = round(float(pct), 1)
    return out

def level(score: float):
    if score >= 75:  return "Muy alto"
    if score >= 60:  return "Alto"
    if score >= 40:  return "Promedio"
    if score >= 25:  return "Bajo"
    return "Muy bajo"

def random_fill_and_finish():
    st.session_state.answers = {q["key"]: random.choice(LIKERT) for q in PREGUNTAS}
    st.session_state.fecha_eval = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.stage = "results"
    scroll_top()
    st.rerun()

# ============== NAV BAR SUPERIOR ==============
c1, c2 = st.columns([1,1])
with c1:
    st.markdown("### 🧠 Big Five • Evaluación Profesional (Pro Max)")
with c2:
    colL, colR = st.columns([1,1])
    with colL:
        if st.button("🎲 Completar aleatoriamente", type="secondary", use_container_width=True):
            random_fill_and_finish()
    with colR:
        if st.button("🔄 Reiniciar", type="secondary", use_container_width=True):
            st.session_state.q_index = 0
            st.session_state.answers = {q["key"]: None for q in PREGUNTAS}
            st.session_state.stage = "test"
            scroll_top()
            st.rerun()

st.markdown("<hr/>", unsafe_allow_html=True)

# ============== PANTALLA DE TEST ==============
def view_test():
    scroll_top()

    # Estado
    idx = st.session_state.q_index
    q = PREGUNTAS[idx]
    total = len(PREGUNTAS)
    dim = q["dim"]
    dim_info = DIMENSIONES[dim]

    # Layout: lateral (izq resumen, der tarjeta pregunta)
    left, right = st.columns([1.1, 1.9])

    with left:
        st.markdown("#### Progreso")
        st.progress((idx+1)/total, text=f"{idx+1} / {total} preguntas")

        # Tarjeta resumen
