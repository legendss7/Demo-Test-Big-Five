# bigfive_app.py
# -------------------------------------------------
# 🧠 TEST PROFESIONAL DE PERSONALIDAD BIG FIVE (OCEAN)
# Desarrollado por José Ignacio Taj-Taj | 2025
# -------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
from datetime import datetime

# -------------------------------------------------
# 🔹 CONFIGURACIÓN GENERAL
# -------------------------------------------------
st.set_page_config(
    page_title="Test Big Five (OCEAN) | Evaluación Profesional",
    page_icon="🧠",
    layout="wide"
)

# -------------------------------------------------
# 🔹 FUNCIÓN DE SCROLL AUTOMÁTICO
# -------------------------------------------------
def forzar_scroll_al_top():
    js_code = """
        <script>
            setTimeout(() => {
                const app = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (app) app.scrollTo({ top: 0, behavior: 'auto' });
                window.parent.scrollTo({ top: 0, behavior: 'auto' });
            }, 300);
        </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# -------------------------------------------------
# 🔹 DEFINICIÓN DE LAS DIMENSIONES
# -------------------------------------------------
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O", "color": "#0077b6", "icon": "💡",
        "desc": "Curiosidad, imaginación, creatividad y apertura mental."
    },
    "Responsabilidad": {
        "code": "C", "color": "#00b4d8", "icon": "🎯",
        "desc": "Autodisciplina, organización y compromiso con los objetivos."
    },
    "Extraversión": {
        "code": "E", "color": "#48cae4", "icon": "🗣️",
        "desc": "Sociabilidad, energía y tendencia a interactuar con otros."
    },
    "Amabilidad": {
        "code": "A", "color": "#90e0ef", "icon": "🤝",
        "desc": "Empatía, cooperación y sensibilidad hacia los demás."
    },
    "Estabilidad Emocional": {
        "code": "N", "color": "#0096c7", "icon": "🧘",
        "desc": "Control emocional y capacidad para enfrentar el estrés."
    },
}

DIMENSIONES_LIST = list(DIMENSIONES.keys())

ESCALA_LIKERT = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo"
}
LIKERT_OPTIONS = list(ESCALA_LIKERT.keys())

# -------------------------------------------------
# 🔹 BANCO DE PREGUNTAS – 10 por dimensión (50 total)
# -------------------------------------------------
PREGUNTAS = [
    # 💡 Apertura a la Experiencia
    {"text": "Disfruto aprendiendo cosas nuevas.", "dim": "Apertura a la Experiencia", "key": "O1", "reverse": False},
    {"text": "Me interesa la música, el arte o la literatura.", "dim": "Apertura a la Experiencia", "key": "O2", "reverse": False},
    {"text": "Pienso con frecuencia en ideas poco convencionales.", "dim": "Apertura a la Experiencia", "key": "O3", "reverse": False},
    {"text": "Soy curioso sobre temas poco comunes.", "dim": "Apertura a la Experiencia", "key": "O4", "reverse": False},
    {"text": "Me gusta probar cosas nuevas.", "dim": "Apertura a la Experiencia", "key": "O5", "reverse": False},
    {"text": "Prefiero las rutinas conocidas a las nuevas experiencias.", "dim": "Apertura a la Experiencia", "key": "O6", "reverse": True},
    {"text": "No me interesa explorar nuevas ideas.", "dim": "Apertura a la Experiencia", "key": "O7", "reverse": True},
    {"text": "Evito los cambios en mi vida.", "dim": "Apertura a la Experiencia", "key": "O8", "reverse": True},
    {"text": "Me cuesta imaginar soluciones creativas.", "dim": "Apertura a la Experiencia", "key": "O9", "reverse": True},
    {"text": "Rara vez reflexiono sobre temas abstractos.", "dim": "Apertura a la Experiencia", "key": "O10", "reverse": True},

    # 🎯 Responsabilidad
    {"text": "Cumplo con mis compromisos.", "dim": "Responsabilidad", "key": "C1", "reverse": False},
    {"text": "Soy organizado con mis tareas diarias.", "dim": "Responsabilidad", "key": "C2", "reverse": False},
    {"text": "Planifico mi trabajo antes de hacerlo.", "dim": "Responsabilidad", "key": "C3", "reverse": False},
    {"text": "Me considero una persona confiable.", "dim": "Responsabilidad", "key": "C4", "reverse": False},
    {"text": "Presto atención a los detalles.", "dim": "Responsabilidad", "key": "C5", "reverse": False},
    {"text": "A menudo dejo cosas sin terminar.", "dim": "Responsabilidad", "key": "C6", "reverse": True},
    {"text": "Pierdo el tiempo fácilmente.", "dim": "Responsabilidad", "key": "C7", "reverse": True},
    {"text": "Me cuesta seguir un horario fijo.", "dim": "Responsabilidad", "key": "C8", "reverse": True},
    {"text": "Evito mis responsabilidades cuando puedo.", "dim": "Responsabilidad", "key": "C9", "reverse": True},
    {"text": "Soy desorganizado en mi trabajo.", "dim": "Responsabilidad", "key": "C10", "reverse": True},

    # 🗣️ Extraversión
    {"text": "Disfruto estando rodeado de gente.", "dim": "Extraversión", "key": "E1", "reverse": False},
    {"text": "Me siento cómodo hablando en público.", "dim": "Extraversión", "key": "E2", "reverse": False},
    {"text": "Tiendo a iniciar conversaciones.", "dim": "Extraversión", "key": "E3", "reverse": False},
    {"text": "Me considero una persona sociable.", "dim": "Extraversión", "key": "E4", "reverse": False},
    {"text": "Me energiza interactuar con los demás.", "dim": "Extraversión", "key": "E5", "reverse": False},
    {"text": "Prefiero pasar tiempo solo.", "dim": "Extraversión", "key": "E6", "reverse": True},
    {"text": "Me incomodan los grupos grandes.", "dim": "Extraversión", "key": "E7", "reverse": True},
    {"text": "Evito conocer personas nuevas.", "dim": "Extraversión", "key": "E8", "reverse": True},
    {"text": "Rara vez comparto mis pensamientos.", "dim": "Extraversión", "key": "E9", "reverse": True},
    {"text": "Me cuesta expresar mis emociones.", "dim": "Extraversión", "key": "E10", "reverse": True},

    # 🤝 Amabilidad
    {"text": "Trato a las personas con respeto.", "dim": "Amabilidad", "key": "A1", "reverse": False},
    {"text": "Me preocupo por el bienestar de los demás.", "dim": "Amabilidad", "key": "A2", "reverse": False},
    {"text": "Escucho con atención a los demás.", "dim": "Amabilidad", "key": "A3", "reverse": False},
    {"text": "Soy empático con los problemas ajenos.", "dim": "Amabilidad", "key": "A4", "reverse": False},
    {"text": "Me considero una persona amable.", "dim": "Amabilidad", "key": "A5", "reverse": False},
    {"text": "No me interesa mucho ayudar a otros.", "dim": "Amabilidad", "key": "A6", "reverse": True},
    {"text": "Tiendo a ser impaciente con la gente.", "dim": "Amabilidad", "key": "A7", "reverse": True},
    {"text": "Me cuesta confiar en los demás.", "dim": "Amabilidad", "key": "A8", "reverse": True},
    {"text": "Soy muy crítico con los errores de los demás.", "dim": "Amabilidad", "key": "A9", "reverse": True},
    {"text": "No suelo mostrar compasión.", "dim": "Amabilidad", "key": "A10", "reverse": True},

    # 🧘 Estabilidad Emocional
    {"text": "Mantengo la calma en situaciones difíciles.", "dim": "Estabilidad Emocional", "key": "N1", "reverse": False},
    {"text": "Manejo bien el estrés.", "dim": "Estabilidad Emocional", "key": "N2", "reverse": False},
    {"text": "Me considero emocionalmente estable.", "dim": "Estabilidad Emocional", "key": "N3", "reverse": False},
    {"text": "Rara vez me enojo con facilidad.", "dim": "Estabilidad Emocional", "key": "N4", "reverse": False},
    {"text": "Me recupero rápido de los problemas.", "dim": "Estabilidad Emocional", "key": "N5", "reverse": False},
    {"text": "Me preocupo por todo.", "dim": "Estabilidad Emocional", "key": "N6", "reverse": True},
    {"text": "Soy muy sensible a las críticas.", "dim": "Estabilidad Emocional", "key": "N7", "reverse": True},
    {"text": "A menudo me siento nervioso o tenso.", "dim": "Estabilidad Emocional", "key": "N8", "reverse": True},
    {"text": "Cambio de ánimo con frecuencia.", "dim": "Estabilidad Emocional", "key": "N9", "reverse": True},
    {"text": "Me resulta difícil relajarme.", "dim": "Estabilidad Emocional", "key": "N10", "reverse": True},
]

# -------------------------------------------------
# 🔹 FUNCIONES DE CÁLCULO
# -------------------------------------------------
def reverse_score(score): return 6 - score

def calcular_resultados(respuestas):
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    for p in PREGUNTAS:
        score = respuestas.get(p['key'])
        if p['reverse']:
            score = reverse_score(score)
        scores[p['dim']].append(score)
    return {dim: round(np.mean(vals) * 20, 1) for dim, vals in scores.items()}

# -------------------------------------------------
# 🔹 SESSION STATE
# -------------------------------------------------
if "etapa" not in st.session_state:
    st.session_state.etapa = "inicio"
if "respuestas" not in st.session_state:
    st.session_state.respuestas = {p["key"]: 3 for p in PREGUNTAS}

# -------------------------------------------------
# 🔹 VISTAS
# -------------------------------------------------
def vista_inicio():
    st.title("🧠 Test de Personalidad Big Five (OCEAN)")
    st.markdown("""
    Evalúa los **cinco grandes rasgos de personalidad**:
    **Apertura, Responsabilidad, Extraversión, Amabilidad y Estabilidad Emocional.**
    """)
    st.info("Duración: 10-15 minutos | Escala: Likert de 5 puntos")

    if st.button("🚀 Iniciar Evaluación", use_container_width=True):
        st.session_state.etapa = "test"
        forzar_scroll_al_top()
        st.rerun()

def vista_test():
    st.header("📋 Responde las siguientes afirmaciones:")

    for p in PREGUNTAS:
        st.radio(
            label=f"**{p['text']}**",
            options=LIKERT_OPTIONS,
            format_func=lambda x: ESCALA_LIKERT[x],
            key=p['key'],
            horizontal=True
        )

    if st.button("✅ Finalizar Test y Ver Resultados", use_container_width=True):
        st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
        st.session_state.etapa = "resultados"
        st.rerun()

def vista_resultados():
    resultados = st.session_state.resultados
    st.title("📊 Resultados del Test Big Five")

    st.plotly_chart(grafico_radar(resultados), use_container_width=True)
    st.plotly_chart(grafico_barras(resultados), use_container_width=True)

    df = pd.DataFrame({
        "Dimensión": resultados.keys(),
        "Puntaje": resultados.values()
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("🔄 Realizar Nuevamente", use_container_width=True):
        st.session_state.etapa = "inicio"
        st.rerun()

# -------------------------------------------------
# 🔹 GRÁFICOS
# -------------------------------------------------
def grafico_radar(resultados):
    categorias = [DIMENSIONES[dim]["code"] for dim in resultados]
    valores = list(resultados.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=valores, theta=categorias, fill='toself', name='Perfil',
        line=dict(color="#0077b6", width=3),
        fillcolor='rgba(0,119,182,0.2)'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    return fig

def grafico_barras(resultados):
    df = pd.DataFrame({'Dimensión': resultados.keys(), 'Puntaje': resultados.values()})
    fig = go.Figure(go.Bar(
        x=df['Puntaje'], y=df['Dimensión'], orientation='h',
        marker=dict(color=df['Puntaje'], colorscale='RdYlGn', showscale=True)
    ))
    fig.update_layout(height=500, title="Puntuaciones por Dimensión")
    return fig

# -------------------------------------------------
# 🔹 FLUJO PRINCIPAL
# -------------------------------------------------
if st.session_state.etapa == "inicio":
    vista_inicio()
elif st.session_state.etapa == "test":
    vista_test()
elif st.session_state.etapa == "resultados":
    vista_resultados()

# -------------------------------------------------
# 🔹 FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: gray;'>
© 2025 | Test de Personalidad Big Five (OCEAN) desarrollado por <b>José Ignacio Taj-Taj</b><br>
Versión profesional académica – Evaluación psicológica orientativa.<br>
No sustituye diagnósticos clínicos formales.
</p>
""", unsafe_allow_html=True)
