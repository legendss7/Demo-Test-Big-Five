# streamlit_app.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
from datetime import datetime
from io import BytesIO

# -------- PDF (ReportLab) --------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image

# ------------------ CONFIG ------------------
st.set_page_config(
    layout="wide",
    page_title="Test Big Five (OCEAN) | RRHH Corporativo",
    page_icon="🧠"
)

# ------------------ THEME / CSS ------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: #ffffff;
  color: #000000;
}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
hr {border-top: 1px solid #e0e0e0;}
h1, h2, h3, h4 { color: #111111; }
.block {
  background: #fafafa; border: 1px solid #ddd; border-radius: 12px;
  padding: 18px 20px; box-shadow: 0 4px 10px rgba(0,0,0,.05);
}
button[kind="primary"] {
  background-color: #1a73e8 !important;
  color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ------------------ CONSTANTES ------------------
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O", "color": "#0ea5e9", "icon": "💡",
        "desc": "Imaginación, curiosidad intelectual y aprecio por lo nuevo.",
        "caracteristicas_altas": "Creativo, curioso, aventurero, mente abierta",
        "caracteristicas_bajas": "Práctico, convencional, prefiere lo familiar"
    },
    "Responsabilidad": {
        "code": "C", "color": "#22c55e", "icon": "🎯",
        "desc": "Autodisciplina, organización y orientación a resultados.",
        "caracteristicas_altas": "Organizado, confiable, disciplinado, planificado",
        "caracteristicas_bajas": "Flexible, espontáneo, despreocupado"
    },
    "Extraversión": {
        "code": "E", "color": "#f59e0b", "icon": "🗣️",
        "desc": "Energía social, asertividad y búsqueda de estimulación.",
        "caracteristicas_altas": "Sociable, hablador, asertivo, enérgico",
        "caracteristicas_bajas": "Reservado, tranquilo, independiente"
    },
    "Amabilidad": {
        "code": "A", "color": "#a78bfa", "icon": "🤝",
        "desc": "Cooperación, empatía, confianza y respeto interpersonal.",
        "caracteristicas_altas": "Compasivo, cooperativo, confiado, altruista",
        "caracteristicas_bajas": "Competitivo, escéptico, directo, objetivo"
    },
    "Estabilidad Emocional": {
        "code": "N", "color": "#f43f5e", "icon": "🧘",
        "desc": "Calma y manejo del estrés (opuesto a Neuroticismo).",
        "caracteristicas_altas": "Estable, calmado, resiliente, seguro",
        "caracteristicas_bajas": "Sensible, ansioso, reactivo emocionalmente"
    },
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

ESCALA_LIKERT = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}
LIKERT_OPTIONS = list(ESCALA_LIKERT.keys())

def reverse_score(score: int) -> int:
    return 6 - score

# --------- 50 Ítems (10 por dimensión; 5 directos + 5 inversos) ----------
PREGUNTAS = [
    # O
    {"text": "Tengo una imaginación muy activa", "dim": "Apertura a la Experiencia", "key": "O1", "reverse": False},
    {"text": "Me atraen los retos intelectuales complejos", "dim": "Apertura a la Experiencia", "key": "O2", "reverse": False},
    {"text": "Disfruto el arte y la cultura (museos, cine, música)", "dim": "Apertura a la Experiencia", "key": "O3", "reverse": False},
    {"text": "Me entusiasma experimentar con ideas nuevas", "dim": "Apertura a la Experiencia", "key": "O4", "reverse": False},
    {"text": "Valoro la creatividad y la originalidad", "dim": "Apertura a la Experiencia", "key": "O5", "reverse": False},
    {"text": "Prefiero rutinas conocidas a probar cosas nuevas", "dim": "Apertura a la Experiencia", "key": "O6", "reverse": True},
    {"text": "Evito discusiones filosóficas o abstractas", "dim": "Apertura a la Experiencia", "key": "O7", "reverse": True},
    {"text": "Rara vez reflexiono sobre temas complejos", "dim": "Apertura a la Experiencia", "key": "O8", "reverse": True},
    {"text": "Me inclino por lo convencional frente a lo original", "dim": "Apertura a la Experiencia", "key": "O9", "reverse": True},
    {"text": "No me gusta cambiar hábitos establecidos", "dim": "Apertura a la Experiencia", "key": "O10", "reverse": True},
    # C
    {"text": "Llego preparado y con antelación a mis compromisos", "dim": "Responsabilidad", "key": "C1", "reverse": False},
    {"text": "Cuido los detalles y sigo procesos definidos", "dim": "Responsabilidad", "key": "C2", "reverse": False},
    {"text": "Cumplo con plazos y metas de forma consistente", "dim": "Responsabilidad", "key": "C3", "reverse": False},
    {"text": "Planifico mi trabajo con estructura", "dim": "Responsabilidad", "key": "C4", "reverse": False},
    {"text": "Me exijo altos estándares de calidad", "dim": "Responsabilidad", "key": "C5", "reverse": False},
    {"text": "Dejo tareas o espacios desordenados", "dim": "Responsabilidad", "key": "C6", "reverse": True},
    {"text": "Evito responsabilidades cuando puedo", "dim": "Responsabilidad", "key": "C7", "reverse": True},
    {"text": "Me distraigo con facilidad al trabajar", "dim": "Responsabilidad", "key": "C8", "reverse": True},
    {"text": "Olvido con frecuencia devolver cosas a su lugar", "dim": "Responsabilidad", "key": "C9", "reverse": True},
    {"text": "Procrastino tareas importantes", "dim": "Responsabilidad", "key": "C10", "reverse": True},
    # E
    {"text": "Me energizan las interacciones sociales", "dim": "Extraversión", "key": "E1", "reverse": False},
    {"text": "Me siento cómodo con personas nuevas", "dim": "Extraversión", "key": "E2", "reverse": False},
    {"text": "Busco activamente espacios de colaboración", "dim": "Extraversión", "key": "E3", "reverse": False},
    {"text": "Participo y hablo con facilidad en reuniones", "dim": "Extraversión", "key": "E4", "reverse": False},
    {"text": "Me gusta liderar conversaciones o proyectos", "dim": "Extraversión", "key": "E5", "reverse": False},
    {"text": "Prefiero estar solo que con mucha gente", "dim": "Extraversión", "key": "E6", "reverse": True},
    {"text": "Soy más bien reservado y callado", "dim": "Extraversión", "key": "E7", "reverse": True},
    {"text": "Me cuesta expresarme en grupos grandes", "dim": "Extraversión", "key": "E8", "reverse": True},
    {"text": "Prefiero trabajar en segundo plano", "dim": "Extraversión", "key": "E9", "reverse": True},
    {"text": "Las interacciones sociales prolongadas me agotan", "dim": "Extraversión", "key": "E10", "reverse": True},
    # A
    {"text": "Empatizo con facilidad con los demás", "dim": "Amabilidad", "key": "A1", "reverse": False},
    {"text": "Me preocupa genuinamente el bienestar ajeno", "dim": "Amabilidad", "key": "A2", "reverse": False},
    {"text": "Trato a todas las personas con respeto", "dim": "Amabilidad", "key": "A3", "reverse": False},
    {"text": "Ayudo sin esperar retribución inmediata", "dim": "Amabilidad", "key": "A4", "reverse": False},
    {"text": "Confío en la buena intención de las personas", "dim": "Amabilidad", "key": "A5", "reverse": False},
    {"text": "No me interesa demasiado la gente en general", "dim": "Amabilidad", "key": "A6", "reverse": True},
    {"text": "Sospecho de las intenciones de los demás", "dim": "Amabilidad", "key": "A7", "reverse": True},
    {"text": "Puedo ser insensible en ocasiones", "dim": "Amabilidad", "key": "A8", "reverse": True},
    {"text": "Suelo priorizarme por encima de otros", "dim": "Amabilidad", "key": "A9", "reverse": True},
    {"text": "Los problemas ajenos rara vez me conmueven", "dim": "Amabilidad", "key": "A10", "reverse": True},
    # N (Estabilidad)
    {"text": "Mantengo la calma bajo presión", "dim": "Estabilidad Emocional", "key": "N1", "reverse": False},
    {"text": "Me siento poco ansioso en el día a día", "dim": "Estabilidad Emocional", "key": "N2", "reverse": False},
    {"text": "Me percibo emocionalmente estable", "dim": "Estabilidad Emocional", "key": "N3", "reverse": False},
    {"text": "Me recupero rápido de contratiempos", "dim": "Estabilidad Emocional", "key": "N4", "reverse": False},
    {"text": "Confío en mis recursos ante la presión", "dim": "Estabilidad Emocional", "key": "N5", "reverse": False},
    {"text": "Me preocupo excesivamente por las cosas", "dim": "Estabilidad Emocional", "key": "N6", "reverse": True},
    {"text": "Me irrito con facilidad", "dim": "Estabilidad Emocional", "key": "N7", "reverse": True},
    {"text": "Siento tristeza o desánimo con frecuencia", "dim": "Estabilidad Emocional", "key": "N8", "reverse": True},
    {"text": "Tengo cambios de humor marcados", "dim": "Estabilidad Emocional", "key": "N9", "reverse": True},
    {"text": "El estrés me abruma con facilidad", "dim": "Estabilidad Emocional", "key": "N10", "reverse": True},
]

# ------------------ STATE ------------------
if 'stage' not in st.session_state: st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state: st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
if 'resultados' not in st.session_state: st.session_state.resultados = None
if 'current_dimension_index' not in st.session_state: st.session_state.current_dimension_index = 0
if 'fecha_evaluacion' not in st.session_state: st.session_state.fecha_evaluacion = None

# ------------------ HELPERS ------------------
def calcular_resultados(respuestas: dict) -> dict:
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    for p in PREGUNTAS:
        r = respuestas.get(p['key'])
        if r is None: score = 3
        elif p['reverse']: score = reverse_score(r)
        else: score = r
        scores[p['dim']].append(score)
    resultados = {}
    for dim, score_list in scores.items():
        avg = np.mean(score_list)
        resultados[dim] = round(((avg - 1) / 4) * 100, 1)  # 1..5 -> 0..100
    return resultados

def nivel_interpretacion(score: float):
    if score >= 75: return "Muy Alto", "#10b981", "Dominante"
    if score >= 60: return "Alto", "#38bdf8", "Marcado"
    if score >= 40: return "Promedio", "#fbbf24", "Moderado"
    if score >= 25: return "Bajo", "#fb923c", "Suave"
    return "Muy Bajo", "#ef4444", "Mínimo"

def grafico_radar(resultados: dict):
    categories = [f"{DIMENSIONES[d]['code']} - {d}" for d in resultados]
    values = list(resultados.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself', name='Perfil',
        line=dict(color='#0ea5e9', width=3), fillcolor='rgba(14,165,233,.25)',
        marker=dict(size=8)
    ))
    fig.update_layout(
        template="plotly_dark",
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        showlegend=False, height=520, margin=dict(l=20,r=20,t=50,b=20),
        paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        title=dict(text="Radar de Personalidad (OCEAN)", x=0.5)
    )
    return fig

def grafico_barras(resultados: dict):
    df = pd.DataFrame({"Dimensión": list(resultados.keys()), "Puntuación": list(resultados.values())}).sort_values("Puntuación")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Dimensión"], x=df["Puntuación"], orientation='h',
        marker=dict(color=df["Puntuación"], colorscale='Bluered', showscale=True),
        text=df["Puntuación"].round(1), textposition='outside'
    ))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        xaxis=dict(range=[0,110]), height=520, margin=dict(l=180,r=20,t=50,b=20),
        title=dict(text="Puntuaciones por Dimensión", x=0.5)
    )
    return fig

def grafico_comparativo(resultados: dict):
    dims = list(resultados.keys())
    y1 = list(resultados.values())
    y2 = [50]*len(dims)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Perfil', x=dims, y=y1, marker=dict(color='#0ea5e9')))
    fig.add_trace(go.Bar(name='Promedio Poblacional', x=dims, y=y2, marker=dict(color='#334155')))
    fig.update_layout(
        template="plotly_dark", barmode='group',
        paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
        yaxis=dict(range=[0,110]), height=520, title=dict(text="Comparativo con Promedio", x=0.5)
    )
    return fig

def iniciar_test():
    st.session_state.stage = 'test_activo'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None

def completar_azar():
    st.session_state.respuestas = {p['key']: random.choice(LIKERT_OPTIONS) for p in PREGUNTAS}
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.stage = 'resultados'

def reiniciar():
    st.session_state.stage = 'inicio'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None
    st.session_state.fecha_evaluacion = None

# ------------------ PDF GENERATION ------------------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
from PIL import Image

def generar_pdf(empresa, fecha, resultados, recomendaciones, logo_bytes=None) -> bytes:
    """Genera un PDF simple y funcional sin errores de ReportLab."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    margin = 2 * cm

    # Logo si se subió
    if logo_bytes:
        try:
            img = Image.open(BytesIO(logo_bytes))
            aspect = img.height / img.width
            w = 3.5 * cm
            h = w * aspect
            tmp = BytesIO()
            img.save(tmp, format="PNG")
            tmp.seek(0)
            c.drawImage(tmp, margin, H - margin - h, width=w, height=h, mask='auto')
        except Exception:
            pass

    # Encabezado
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(W - margin, H - margin, f"Informe Big Five — {empresa}")
    c.setFont("Helvetica", 10)
    c.drawRightString(W - margin, H - margin - 12, f"Fecha: {fecha}")

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, H - 4*cm, "Resultados Generales")
    c.setFont("Helvetica", 11)

    y = H - 5*cm
    for dim, score in resultados.items():
        c.drawString(margin, y, f"{dim}: {score:.1f}/100")
        y -= 0.5 * cm
        if y < 3 * cm:
            c.showPage()
            y = H - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y - 1*cm, "Roles Profesionales Sugeridos")
    c.setFont("Helvetica", 11)
    y -= 1.5 * cm
    for rec in recomendaciones:
        c.drawString(margin, y, f"- {rec}")
        y -= 0.5 * cm
        if y < 3 * cm:
            c.showPage()
            y = H - margin

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.gray)
    c.drawString(margin, 1.5*cm, "Este informe es orientativo. No sustituye una evaluación profesional.")
    c.save()
    buffer.seek(0)
    return buffer.read()


# ------------------ VISTAS ------------------
def vista_inicio():
    st.title("🧠 Test Big Five (OCEAN) — RRHH Corporativo")
    st.write("")
    colA, colB = st.columns([2,1], gap="large")
    with colA:
        st.markdown("""
        <div class="block">
        <h3>¿Qué mide este test?</h3>
        <p class="small">
        El modelo Big Five (OCEAN) es el marco más validado para describir la personalidad en cinco factores:
        <b>O</b> (Apertura), <b>C</b> (Responsabilidad), <b>E</b> (Extraversión), <b>A</b> (Amabilidad) y <b>N</b> (Estabilidad Emocional).
        </p>
        <ul class="small">
          <li><b>50 ítems</b> (10 por dimensión)</li>
          <li>Escala Likert de 1 a 5</li>
          <li>Informe interpretativo para RRHH</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with colB:
        st.markdown('<div class="kpi"><h2 style="margin:0;">Listo para evaluar</h2><p style="opacity:.9;margin:.4rem 0 0;">Candidatos, equipos y desarrollo interno</p></div>', unsafe_allow_html=True)
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 Iniciar Test", use_container_width=True, type="primary"):
                iniciar_test()
                st.rerun()
        with c2:
            if st.button("🎲 Demo (Respuestas aleatorias)", use_container_width=True):
                completar_azar()
                st.rerun()

def vista_test():
    idx = st.session_state.current_dimension_index
    dim = DIMENSIONES_LIST[idx]
    info = DIMENSIONES[dim]
    st.subheader(f"{info['icon']} Dimensión {idx+1} de {len(DIMENSIONES_LIST)}: {dim}")
    st.caption(info["desc"])
    st.progress(sum(v is not None for v in st.session_state.respuestas.values())/len(PREGUNTAS))

    preguntas = [p for p in PREGUNTAS if p['dim'] == dim]
    with st.form(f"form_{idx}"):
        for p in preguntas:
            with st.container():
                st.markdown(f"**{p['text']}**")
                current = st.session_state.respuestas.get(p['key'])
                current_idx = LIKERT_OPTIONS.index(current) if current in LIKERT_OPTIONS else None
                st.session_state.respuestas[p['key']] = st.radio(
                    "Selecciona tu respuesta",
                    LIKERT_OPTIONS, format_func=lambda x: ESCALA_LIKERT[x],
                    index=current_idx, horizontal=True, label_visibility="collapsed",
                    key=f"radio_{p['key']}"
                )
                st.divider()

        if idx == len(DIMENSIONES_LIST)-1:
            label = "✅ Finalizar y ver resultados"
        else:
            label = f"➡️ Continuar a {DIMENSIONES_LIST[idx+1]}"

        submitted = st.form_submit_button(label, use_container_width=True, type="primary")
        if submitted:
            if any(st.session_state.respuestas[p['key']] is None for p in preguntas):
                st.error("Por favor responde todas las preguntas de esta sección.")
            else:
                if idx < len(DIMENSIONES_LIST)-1:
                    st.session_state.current_dimension_index += 1
                    st.rerun()
                else:
                    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
                    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.stage = 'resultados'
                    st.rerun()

def vista_resultados():
    resultados = st.session_state.resultados
    if not resultados:
        st.warning("No hay resultados. Vuelve al inicio.")
        if st.button("Volver al inicio"): reiniciar(); st.rerun()
        return

    st.title("📊 Informe Corporativo — Big Five (OCEAN)")
    st.caption(f"Fecha de evaluación: {st.session_state.fecha_evaluacion}")
    st.write("")

    # KPI
    prom = np.mean(list(resultados.values()))
    st.markdown(f'<div class="kpi"><h2 style="margin:0;">Puntuación promedio: {prom:.1f}/100</h2><p style="opacity:.95;margin-top:.35rem;">Perfil general del candidato/colaborador</p></div>', unsafe_allow_html=True)
    st.write("")

    tab1, tab2, tab3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])
    with tab1:
        st.plotly_chart(grafico_radar(resultados), use_container_width=True)
    with tab2:
        st.plotly_chart(grafico_barras(resultados), use_container_width=True)
    with tab3:
        st.plotly_chart(grafico_comparativo(resultados), use_container_width=True)

    st.divider()

    # Detalle por dimensión
    st.subheader("🔍 Análisis por Dimensión")
    for dim in DIMENSIONES_LIST:
        score = resultados[dim]
        nivel, color, etiqueta = nivel_interpretacion(score)
        d = DIMENSIONES[dim]
        with st.expander(f"{d['icon']} {dim}: {score:.1f} ({nivel})", expanded=True):
            col1, col2 = st.columns([1,2])
            with col1:
                # gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=score,
                    gauge={'axis': {'range': [0, 100]},
                           'bar': {'color': d['color']},
                           'steps': [{'range':[0,25],'color':'#1f2937'},
                                     {'range':[25,40],'color':'#334155'},
                                     {'range':[40,60],'color':'#4b5563'},
                                     {'range':[60,75],'color':'#64748b'},
                                     {'range':[75,100],'color':'#94a3b8'}]},
                    title={'text': d['code']}
                ))
                fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", height=240, margin=dict(l=15,r=15,t=30,b=15))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown(f"**Descripción:** {d['desc']}")
                st.markdown(f"**Nivel:** <span style='color:{color}'>{nivel} ({etiqueta})</span>", unsafe_allow_html=True)
                if score >= 60:
                    st.success(f"Características destacadas: {d['caracteristicas_altas']}")
                elif score >= 40:
                    st.info("Rango promedio; equilibrio funcional para la mayoría de roles.")
                else:
                    st.warning(f"Características probables: {d['caracteristicas_bajas']}")

                st.markdown("**💼 Implicaciones profesionales:**")
                if dim == "Apertura a la Experiencia":
                    if score >= 60:
                        st.markdown("- Innovación, estrategia, I+D, diseño. Alta adaptabilidad.")
                    elif score <= 40:
                        st.markdown("- Entornos con procedimientos estables. Requiere soporte en ambigüedad.")
                    else:
                        st.markdown("- Roles híbridos: creatividad con procesos.")
                elif dim == "Responsabilidad":
                    if score >= 60:
                        st.markdown("- Gestión de proyectos, control, finanzas. Fiabilidad y foco.")
                    elif score <= 40:
                        st.markdown("- Proyectos creativos/ágiles. Beneficia estructura externa.")
                    else:
                        st.markdown("- Desempeño sólido con supervisión moderada.")
                elif dim == "Extraversión":
                    if score >= 60:
                        st.markdown("- Ventas, liderazgo, RRPP. Influencia y networking.")
                    elif score <= 40:
                        st.markdown("- Análisis, investigación, programación. Trabajo concentrado.")
                    else:
                        st.markdown("- Adaptable a trabajo en equipo o individual.")
                elif dim == "Amabilidad":
                    if score >= 60:
                        st.markdown("- RRHH, servicio al cliente, mediación. Clima colaborativo.")
                    elif score <= 40:
                        st.markdown("- Negociación y decisiones difíciles. Objetividad.")
                    else:
                        st.markdown("- Diplomacia con firmeza.")
                elif dim == "Estabilidad Emocional":
                    if score >= 60:
                        st.markdown("- Gestión de crisis, operaciones críticas, liderazgo.")
                    elif score <= 40:
                        st.markdown("- Ambientes predecibles. Cuidado en alta presión.")
                    else:
                        st.markdown("- Regulación emocional adecuada para la mayoría de contextos.")

    st.divider()

    # Fortalezas y áreas
    st.subheader("💪 Fortalezas y Áreas de Desarrollo")
    order = sorted(resultados.items(), key=lambda x: x[1], reverse=True)
    top3, low3 = order[:3], order[-3:]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Top 3 Fortalezas**")
        for i,(dim,score) in enumerate(top3,1):
            st.markdown(f"- **{i}. {DIMENSIONES[dim]['icon']} {dim}** — {score:.1f}/100")
    with c2:
        st.markdown("**Áreas de Desarrollo**")
        for i,(dim,score) in enumerate(low3,1):
            nivel,_,_ = nivel_interpretacion(score)
            st.markdown(f"- **{i}. {DIMENSIONES[dim]['icon']} {dim}** — {score:.1f}/100 ({nivel})")

    st.divider()

    # Tabla resumen
    st.subheader("📋 Tabla Resumen")
    df_res = pd.DataFrame({
        "Dimensión": list(resultados.keys()),
        "Código": [DIMENSIONES[d]["code"] for d in resultados.keys()],
        "Puntuación": [f"{v:.1f}" for v in resultados.values()],
        "Nivel": [nivel_interpretacion(v)[0] for v in resultados.values()],
        "Etiqueta": [nivel_interpretacion(v)[2] for v in resultados.values()],
    })
    st.dataframe(df_res, use_container_width=True, hide_index=True)

    # Reglas para sugerencias de roles
    sugerencias = []
    if resultados["Apertura a la Experiencia"] >= 60 and resultados["Responsabilidad"] >= 60:
        sugerencias.append("**Consultoría Estratégica** — Creatividad + disciplina para resolver problemas complejos.")
    if resultados["Extraversión"] >= 60 and resultados["Amabilidad"] >= 60:
        sugerencias.append("**Gestión de RRHH / People Partner** — Interacción, empatía e influencia positiva.")
    if resultados["Responsabilidad"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        sugerencias.append("**Dirección de Proyectos** — Organización y resiliencia bajo presión.")
    if resultados["Apertura a la Experiencia"] >= 60 and resultados["Extraversión"] <= 40:
        sugerencias.append("**Investigación / Análisis** — Originalidad con foco individual.")
    if resultados["Amabilidad"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        sugerencias.append("**Coaching / Mentoría** — Empatía estable y criterio.")
    if resultados["Extraversión"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        sugerencias.append("**Dirección Comercial** — Impacto social y manejo de presión.")
    if resultados["Responsabilidad"] >= 60 and resultados["Apertura a la Experiencia"] <= 40:
        sugerencias.append("**Operaciones / Cumplimiento** — Procesos, control y fiabilidad.")
    if not sugerencias:
        sugerencias.append("**Perfil versátil** — Ajuste a múltiples funciones según intereses y experiencia.")

    st.subheader("🎯 Roles Profesionales Sugeridos")
    for s in sugerencias:
        st.markdown(f"- {s}")

    st.divider()

    # Exportaciones
    st.subheader("📥 Exportar")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        csv_data = df_res.to_csv(index=False).encode("utf-8")
        st.download_button("📊 Descargar CSV", csv_data, file_name=f"BigFive_Resultados_{st.session_state.fecha_evaluacion.replace(':','-')}.csv", mime="text/csv", use_container_width=True)
    with c2:
        empresa = st.text_input("Nombre de la empresa (para el PDF)", value="Tu Empresa")
        logo_file = st.file_uploader("Logo corporativo (PNG/JPG opcional)", type=["png","jpg","jpeg"])
        logo_bytes = logo_file.read() if logo_file else None
        if st.button("🧾 Descargar Informe PDF", use_container_width=True, type="primary"):
            pdf_bytes = generar_pdf(
                empresa=empresa,
                fecha=st.session_state.fecha_evaluacion,
                resultados=resultados,
                recomendaciones=sugerencias,
                logo_bytes=logo_bytes
            )
            st.download_button(
                label="⬇️ Guardar PDF",
                data=pdf_bytes,
                file_name=f"Informe_BigFive_{empresa.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.info("**Aviso**: Este informe es orientativo. Para toma de decisiones formales, compleméntalo con entrevistas y pruebas estandarizadas administradas por profesionales.", icon="ℹ️")

# ------------------ ROUTER ------------------
st.markdown("<div id='top-anchor'></div>", unsafe_allow_html=True)

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test()
elif st.session_state.stage == 'resultados':
    vista_resultados()

st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#64748b;'>© 2025 · Suite RRHH · Big Five (OCEAN) — Dashboard Corporativo</p>",
    unsafe_allow_html=True
)

