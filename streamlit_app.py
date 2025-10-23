# streamlit_app.py
# Big Five (OCEAN) - App corporativa en Streamlit
# Fondo blanco, texto negro, flujo por pasos con progreso, visualizaciones y exportación PDF/CSV

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
from datetime import datetime
from io import BytesIO
from PIL import Image

# PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors

# =========================
# 1) CONFIGURACIÓN Y ESTILO
# =========================
st.set_page_config(
    page_title="Test Big Five (OCEAN) | Corporativo",
    page_icon="🧠",
    layout="wide"
)

# Estilo corporativo (blanco/negro, sin azules)
st.markdown("""
<style>
:root { --text: #111111; --muted: #666666; --border: #e5e5e5; --card: #fafafa; }
html, body, [data-testid="stAppViewContainer"] { background: #ffffff; color: var(--text); }
[data-testid="stHeader"] { background: rgba(255,255,255,0); }
hr { border: 0; border-top: 1px solid var(--border); }
h1, h2, h3, h4, h5 { color: var(--text); }
.block {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,.04);
}
button[kind="primary"], .stButton > button {
  background-color: #000000 !important;
  color: #ffffff !important;
  border: 1px solid #000000 !important;
  border-radius: 10px !important;
}
.stDownloadButton > button {
  background-color: #000000 !important;
  color: #ffffff !important;
  border: 1px solid #000000 !important;
  border-radius: 10px !important;
}
.stRadio > label, .stCheckbox > label, .stSelectbox > label { color: var(--text) !important; }
.stProgress > div > div > div { background: #000000 !important; }
.small { font-size: .92rem; color: var(--muted); }
.kpi {
  border: 1px solid var(--border); border-radius: 10px; padding: 16px; text-align: center;
}
.kpi h2 { margin: 0; font-size: 2.2rem; }
.kpi p { margin: 8px 0 0 0; color: var(--muted); }
</style>
""", unsafe_allow_html=True)

# Ancla para scroll top
st.markdown("<a id='top-anchor'></a>", unsafe_allow_html=True)

def scroll_top():
    """Sube el scroll al inicio (funciona en Cloud/local)."""
    st.components.v1.html("""
    <script>
      setTimeout(() => {
        const c = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (c) c.scrollTo({top: 0, behavior: 'smooth'});
        window.parent.scrollTo({top: 0, behavior: 'smooth'});
      }, 200);
    </script>
    """, height=0, scrolling=False)

# =========================
# 2) MODELO Y PREGUNTAS
# =========================
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O", "icon": "💡",
        "desc": "Imaginación, curiosidad intelectual y apertura a nuevas ideas.",
        "color": "#111111",
        "caracteristicas_altas": "Creativo, curioso, aventurero, con mente abierta",
        "caracteristicas_bajas": "Práctico, convencional, prefiere lo familiar"
    },
    "Responsabilidad": {
        "code": "C", "icon": "🎯",
        "desc": "Autodisciplina, organización, orientación al logro y al detalle.",
        "color": "#111111",
        "caracteristicas_altas": "Organizado, confiable, disciplinado, planificado",
        "caracteristicas_bajas": "Flexible, espontáneo, despreocupado"
    },
    "Extraversión": {
        "code": "E", "icon": "🗣️",
        "desc": "Energía social, asertividad, búsqueda de estimulación con otros.",
        "color": "#111111",
        "caracteristicas_altas": "Sociable, hablador, enérgico",
        "caracteristicas_bajas": "Reservado, tranquilo, independiente, reflexivo"
    },
    "Amabilidad": {
        "code": "A", "icon": "🤝",
        "desc": "Cooperación, empatía, compasión y confianza hacia los demás.",
        "color": "#111111",
        "caracteristicas_altas": "Compasivo, cooperativo, confiado, altruista",
        "caracteristicas_bajas": "Competitivo, escéptico, directo, objetivo"
    },
    "Estabilidad Emocional": {
        "code": "N", "icon": "🧘",
        "desc": "Calma y capacidad de gestionar el estrés (opuesto a neuroticismo).",
        "color": "#111111",
        "caracteristicas_altas": "Estable, calmado, resiliente, seguro",
        "caracteristicas_bajas": "Sensible, ansioso, reactivo emocionalmente"
    },
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

LIKERT = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}
LIKERT_OPS = list(LIKERT.keys())

def reverse_score(v: int) -> int:
    return 6 - v

# 10 preguntas por dimensión (5 directas + 5 inversas)
PREGUNTAS = [
    # O (10)
    {"text": "Tengo una imaginación activa.", "dim": "Apertura a la Experiencia", "key": "O1", "reverse": False},
    {"text": "Me atraen ideas complejas o poco convencionales.", "dim": "Apertura a la Experiencia", "key": "O2", "reverse": False},
    {"text": "Valoro la creatividad y la originalidad.", "dim": "Apertura a la Experiencia", "key": "O3", "reverse": False},
    {"text": "Disfruto aprender sobre arte o cultura.", "dim": "Apertura a la Experiencia", "key": "O4", "reverse": False},
    {"text": "Me entusiasma explorar nuevos enfoques.", "dim": "Apertura a la Experiencia", "key": "O5", "reverse": False},
    {"text": "Prefiero no cambiar mis hábitos.", "dim": "Apertura a la Experiencia", "key": "O6", "reverse": True},
    {"text": "Las discusiones abstractas me aburren.", "dim": "Apertura a la Experiencia", "key": "O7", "reverse": True},
    {"text": "Evito lo desconocido cuando es posible.", "dim": "Apertura a la Experiencia", "key": "O8", "reverse": True},
    {"text": "Me siento más cómodo con lo tradicional que con lo innovador.", "dim": "Apertura a la Experiencia", "key": "O9", "reverse": True},
    {"text": "Rara vez experimento con nuevas ideas.", "dim": "Apertura a la Experiencia", "key": "O10", "reverse": True},
    # C (10)
    {"text": "Planifico con antelación mis tareas.", "dim": "Responsabilidad", "key": "C1", "reverse": False},
    {"text": "Cumplo plazos de forma constante.", "dim": "Responsabilidad", "key": "C2", "reverse": False},
    {"text": "Presto atención a los detalles.", "dim": "Responsabilidad", "key": "C3", "reverse": False},
    {"text": "Mantengo orden en mi trabajo.", "dim": "Responsabilidad", "key": "C4", "reverse": False},
    {"text": "Me esfuerzo por alcanzar estándares altos.", "dim": "Responsabilidad", "key": "C5", "reverse": False},
    {"text": "Dejo las cosas para después.", "dim": "Responsabilidad", "key": "C6", "reverse": True},
    {"text": "Me distraigo con facilidad en tareas importantes.", "dim": "Responsabilidad", "key": "C7", "reverse": True},
    {"text": "Me cuesta seguir rutinas.", "dim": "Responsabilidad", "key": "C8", "reverse": True},
    {"text": "Olvido completar tareas sencillas.", "dim": "Responsabilidad", "key": "C9", "reverse": True},
    {"text": "Evito responsabilidades cuando puedo.", "dim": "Responsabilidad", "key": "C10", "reverse": True},
    # E (10)
    {"text": "Disfruto ser el centro de las conversaciones.", "dim": "Extraversión", "key": "E1", "reverse": False},
    {"text": "Me energiza interactuar con mucha gente.", "dim": "Extraversión", "key": "E2", "reverse": False},
    {"text": "Tomo la iniciativa en entornos sociales.", "dim": "Extraversión", "key": "E3", "reverse": False},
    {"text": "Me siento cómodo con desconocidos.", "dim": "Extraversión", "key": "E4", "reverse": False},
    {"text": "Busco activamente actividades grupales.", "dim": "Extraversión", "key": "E5", "reverse": False},
    {"text": "Prefiero pasar tiempo a solas.", "dim": "Extraversión", "key": "E6", "reverse": True},
    {"text": "Me incomodan los grupos grandes.", "dim": "Extraversión", "key": "E7", "reverse": True},
    {"text": "Suelo permanecer en segundo plano.", "dim": "Extraversión", "key": "E8", "reverse": True},
    {"text": "Las conversaciones prolongadas me agotan.", "dim": "Extraversión", "key": "E9", "reverse": True},
    {"text": "Evito hablar en reuniones.", "dim": "Extraversión", "key": "E10", "reverse": True},
    # A (10)
    {"text": "Me preocupo por el bienestar de los demás.", "dim": "Amabilidad", "key": "A1", "reverse": False},
    {"text": "Trato a las personas con respeto.", "dim": "Amabilidad", "key": "A2", "reverse": False},
    {"text": "Confío en las buenas intenciones de otros.", "dim": "Amabilidad", "key": "A3", "reverse": False},
    {"text": "Ayudo sin esperar nada a cambio.", "dim": "Amabilidad", "key": "A4", "reverse": False},
    {"text": "Busco cooperar antes que competir.", "dim": "Amabilidad", "key": "A5", "reverse": False},
    {"text": "Soy escéptico con las intenciones ajenas.", "dim": "Amabilidad", "key": "A6", "reverse": True},
    {"text": "Puedo ser directo aunque suene duro.", "dim": "Amabilidad", "key": "A7", "reverse": True},
    {"text": "Me cuesta empatizar con problemas ajenos.", "dim": "Amabilidad", "key": "A8", "reverse": True},
    {"text": "Primero pienso en mis objetivos.", "dim": "Amabilidad", "key": "A9", "reverse": True},
    {"text": "Rara vez me afectan las dificultades de otros.", "dim": "Amabilidad", "key": "A10", "reverse": True},
    # N (10)
    {"text": "Mantengo la calma bajo presión.", "dim": "Estabilidad Emocional", "key": "N1", "reverse": False},
    {"text": "Gestiono el estrés de forma efectiva.", "dim": "Estabilidad Emocional", "key": "N2", "reverse": False},
    {"text": "Me recupero rápido de los contratiempos.", "dim": "Estabilidad Emocional", "key": "N3", "reverse": False},
    {"text": "Me siento seguro y confiado habitualmente.", "dim": "Estabilidad Emocional", "key": "N4", "reverse": False},
    {"text": "Suelo mantener la serenidad en crisis.", "dim": "Estabilidad Emocional", "key": "N5", "reverse": False},
    {"text": "Me preocupo con facilidad.", "dim": "Estabilidad Emocional", "key": "N6", "reverse": True},
    {"text": "Me irrito por pequeñas cosas.", "dim": "Estabilidad Emocional", "key": "N7", "reverse": True},
    {"text": "Tengo cambios de humor frecuentes.", "dim": "Estabilidad Emocional", "key": "N8", "reverse": True},
    {"text": "Me siento abrumado por el estrés.", "dim": "Estabilidad Emocional", "key": "N9", "reverse": True},
    {"text": "Siento ansiedad con relativa frecuencia.", "dim": "Estabilidad Emocional", "key": "N10", "reverse": True},
]

# =========================
# 3) ESTADO
# =========================
if "stage" not in st.session_state:
    st.session_state.stage = "inicio"
if "respuestas" not in st.session_state:
    st.session_state.respuestas = {p["key"]: None for p in PREGUNTAS}
if "current_dim_idx" not in st.session_state:
    st.session_state.current_dim_idx = 0
if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "fecha_eval" not in st.session_state:
    st.session_state.fecha_eval = None

# =========================
# 4) LÓGICA
# =========================
def calcular_resultados(respuestas: dict) -> dict:
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    for p in PREGUNTAS:
        v = respuestas.get(p["key"])
        if v is None:
            v = 3
        v = reverse_score(v) if p["reverse"] else v
        scores[p["dim"]].append(v)
    resultados = {}
    for dim, vals in scores.items():
        avg = float(np.mean(vals))
        percent = ((avg - 1) / 4) * 100
        resultados[dim] = round(percent, 1)
    return resultados

def nivel(score: float):
    if score >= 75:  return "Muy Alto", "Dominante"
    if score >= 60:  return "Alto", "Marcado"
    if score >= 40:  return "Promedio", "Moderado"
    if score >= 25:  return "Bajo", "Suave"
    return "Muy Bajo", "Mínimo"

def grafico_radar(resultados: dict):
    cats = [f"{DIMENSIONES[d]['code']} - {d}" for d in resultados.keys()]
    vals = list(resultados.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=cats, fill="toself", name="Perfil",
        line=dict(color="#111111", width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        height=520,
        polar=dict(radialaxis=dict(visible=True, range=[0,100]))
    )
    return fig

def grafico_barras(resultados: dict):
    df = pd.DataFrame({"Dimensión": list(resultados.keys()), "Puntuación": list(resultados.values())})
    df = df.sort_values("Puntuación", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["Puntuación"], y=df["Dimensión"], orientation="h",
        marker=dict(color="#111111"),
        text=[f"{v:.1f}" for v in df["Puntuación"]],
        textposition="outside"
    ))
    fig.update_layout(template="plotly_white", height=520, xaxis=dict(range=[0,110], title="Puntuación (0-100)"))
    return fig

def grafico_comparativo(resultados: dict):
    dims = list(resultados.keys())
    vals = list(resultados.values())
    avg = [50]*len(dims)
    fig = go.Figure()
    fig.add_bar(name="Tu perfil", x=dims, y=vals, marker=dict(color="#111111"), text=[f"{v:.1f}" for v in vals], textposition="outside")
    fig.add_bar(name="Promedio", x=dims, y=avg, marker=dict(color="#c7c7c7"), text=["50.0"]*len(dims), textposition="outside")
    fig.update_layout(template="plotly_white", barmode="group", height=520, yaxis=dict(range=[0,110]))
    return fig

def generar_pdf(empresa, fecha, resultados, recomendaciones, logo_bytes=None) -> bytes:
    """PDF simple, estable y corporativo (blanco/negro)."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4
    margin = 2 * cm

    # Logo opcional
    if logo_bytes:
        try:
            img = Image.open(BytesIO(logo_bytes))
            aspect = img.height / img.width if img.width else 1
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
        y -= 0.55 * cm
        if y < 3 * cm:
            c.showPage()
            y = H - margin

    # Recomendaciones
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y - 1*cm, "Roles Profesionales Sugeridos")
    c.setFont("Helvetica", 11)
    y -= 1.6 * cm
    for rec in recomendaciones:
        c.drawString(margin, y, f"- {rec}")
        y -= 0.5 * cm
        if y < 3 * cm:
            c.showPage()
            y = H - margin

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.grey)
    c.drawString(margin, 1.5*cm, "Este informe es orientativo y no sustituye una evaluación profesional.")
    c.save()
    buffer.seek(0)
    return buffer.read()

# =========================
# 5) VISTAS
# =========================
def vista_inicio():
    scroll_top()
    st.title("🧠 Test de Personalidad Big Five (OCEAN)")
    st.caption("Evaluación corporativa — fondo blanco, texto negro, enfoque profesional.")

    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("""
        **Información del test**
        - Duración: 10–15 min  
        - Ítems: 50 (10 por dimensión)  
        - Escala: Likert 1–5  
        - Dimensiones: O, C, E, A, N  
        """)
        st.markdown("<hr/>", unsafe_allow_html=True)
        with st.expander("¿Qué mide cada dimensión?", expanded=True):
            for dim in DIMENSIONES_LIST:
                st.markdown(f"**{DIMENSIONES[dim]['icon']} {dim}** — {DIMENSIONES[dim]['desc']}")
    with col2:
        st.markdown("<div class='block'>", unsafe_allow_html=True)
        st.subheader("Comenzar")
        if st.button("📝 Iniciar test", type="primary", use_container_width=True):
            st.session_state.stage = "test"
            st.session_state.current_dim_idx = 0
            st.session_state.respuestas = {p["key"]: None for p in PREGUNTAS}
            scroll_top()
            st.rerun()
        st.divider()
        if st.button("🎲 Modo demo (autocompletar)", use_container_width=True):
            st.session_state.respuestas = {p["key"]: random.choice(LIKERT_OPS) for p in PREGUNTAS}
            st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
            st.session_state.fecha_eval = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.session_state.stage = "resultados"
            scroll_top()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def vista_test():
    idx = st.session_state.current_dim_idx
    dim_name = DIMENSIONES_LIST[idx]
    dim = DIMENSIONES[dim_name]

    # Progreso general
    respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None)
    total = len(PREGUNTAS)
    progreso = respondidas/total if total else 0.0

    st.progress(progreso, text=f"Progreso: {respondidas}/{total} ({progreso*100:.0f}%)")
    st.title(f"{dim['icon']} {dim_name}")
    st.caption(dim["desc"])
    st.markdown("<hr/>", unsafe_allow_html=True)

    # Preguntas de la dimensión actual (10)
    preguntas_dim = [p for p in PREGUNTAS if p["dim"] == dim_name]
    with st.form(f"form_{idx}"):
        for p in preguntas_dim:
            st.markdown(f"**{p['text']}**")
            current = st.session_state.respuestas.get(p["key"])
            current_idx = LIKERT_OPS.index(current) if current in LIKERT_OPS else None
            sel = st.radio(
                label=f"Respuesta {p['key']}",
                options=LIKERT_OPS,
                index=current_idx,
                format_func=lambda x: LIKERT[x],
                horizontal=True,
                key=f"radio_{p['key']}"
            )
            st.session_state.respuestas[p["key"]] = sel
            st.markdown("<hr/>", unsafe_allow_html=True)

        cols = st.columns([1,1])
        with cols[0]:
            back = st.form_submit_button("⬅️ Anterior", use_container_width=True)
        with cols[1]:
            if idx == len(DIMENSIONES_LIST)-1:
                forward_label = "✅ Finalizar y ver resultados"
            else:
                forward_label = "➡️ Siguiente"
            forward = st.form_submit_button(forward_label, type="primary", use_container_width=True)

        if back:
            if idx > 0:
                st.session_state.current_dim_idx -= 1
            scroll_top()
            st.rerun()

        if forward:
            # Validación: todas contestadas en este bloque
            incompletas = [p for p in preguntas_dim if st.session_state.respuestas.get(p["key"]) is None]
            if incompletas:
                st.error("Responde todas las preguntas de esta sección antes de continuar.")
            else:
                if idx < len(DIMENSIONES_LIST)-1:
                    st.session_state.current_dim_idx += 1
                    scroll_top()
                    st.rerun()
                else:
                    # Finalizar
                    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
                    st.session_state.fecha_eval = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.stage = "resultados"
                    scroll_top()
                    st.rerun()

def vista_resultados():
    scroll_top()
    resultados = st.session_state.resultados
    if not resultados:
        st.warning("No hay resultados para mostrar.")
        if st.button("Volver al inicio"):
            st.session_state.stage = "inicio"
            st.rerun()
        return

    st.title("📊 Informe de Personalidad Big Five (OCEAN)")
    st.caption(f"Fecha de evaluación: {st.session_state.fecha_eval}")
    st.markdown("<hr/>", unsafe_allow_html=True)

    # KPIs
    prom_total = float(np.mean(list(resultados.values())))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.markdown("<p>Puntuación Promedio</p>", unsafe_allow_html=True)
        st.markdown(f"<h2>{prom_total:.1f}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        top_dim = max(resultados, key=lambda k: resultados[k])
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.markdown("<p>Dimensión más fuerte</p>", unsafe_allow_html=True)
        st.markdown(f"<h2>{DIMENSIONES[top_dim]['code']}</h2><p>{top_dim}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        low_dim = min(resultados, key=lambda k: resultados[k])
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.markdown("<p>Mayor oportunidad</p>", unsafe_allow_html=True)
        st.markdown(f"<h2>{DIMENSIONES[low_dim]['code']}</h2><p>{low_dim}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Visualizaciones")
    t1, t2, t3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])
    with t1:
        st.plotly_chart(grafico_radar(resultados), use_container_width=True)
    with t2:
        st.plotly_chart(grafico_barras(resultados), use_container_width=True)
    with t3:
        st.plotly_chart(grafico_comparativo(resultados), use_container_width=True)

    st.markdown("---")
    st.markdown("### Detalle por dimensión")
    for dim in DIMENSIONES_LIST:
        score = resultados[dim]
        nivel_txt, etiqueta = nivel(score)
        with st.expander(f"{DIMENSIONES[dim]['icon']} {dim} — {score:.1f} ({nivel_txt})", expanded=True):
            c1, c2 = st.columns([1,2])
            with c1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    gauge={
                        "axis":{"range":[0,100]},
                        "bar":{"color":"#111111"},
                        "steps":[
                            {"range":[0,25], "color":"#f2f2f2"},
                            {"range":[25,40], "color":"#e8e8e8"},
                            {"range":[40,60], "color":"#dedede"},
                            {"range":[60,75], "color":"#d4d4d4"},
                            {"range":[75,100], "color":"#c9c9c9"},
                        ],
                    },
                    number={"font":{"size":38}},
                    title={"text": DIMENSIONES[dim]["code"]}
                ))
                fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10), template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown("**Descripción:**")
                st.write(DIMENSIONES[dim]["desc"])
                st.markdown(f"**Nivel:** {nivel_txt} ({etiqueta})")
                if score >= 60:
                    st.success("Perfil alto. " + DIMENSIONES[dim]["caracteristicas_altas"])
                elif score >= 40:
                    st.info("Perfil medio. Equilibrio funcional.")
                else:
                    st.warning("Perfil bajo. " + DIMENSIONES[dim]["caracteristicas_bajas"])

    st.markdown("---")
    st.markdown("### Fortalezas & Desarrollo")
    sorted_dims = sorted(resultados.items(), key=lambda x: x[1], reverse=True)
    top3 = sorted_dims[:3]; bottom3 = sorted_dims[-3:]
    cL, cR = st.columns(2)
    with cL:
        st.subheader("🌟 Fortalezas principales")
        for i, (dim, s) in enumerate(top3, 1):
            st.markdown(f"**{i}. {dim}** — {s:.1f}/100")
            st.progress(int(s))
    with cR:
        st.subheader("📈 Áreas de desarrollo")
        for i, (dim, s) in enumerate(bottom3, 1):
            st.markdown(f"**{i}. {dim}** — {s:.1f}/100")
            st.progress(int(s))

    st.markdown("---")
    st.markdown("### Recomendaciones profesionales")
    recs = []
    if resultados["Responsabilidad"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        recs.append("Dirección de Proyectos — organizado y resiliente.")
    if resultados["Extraversión"] >= 60 and resultados["Amabilidad"] >= 60:
        recs.append("Gestión de RR. HH. — social y empático.")
    if resultados["Apertura a la Experiencia"] >= 60 and resultados["Responsabilidad"] >= 60:
        recs.append("Consultoría estratégica — creatividad con ejecución.")
    if resultados["Apertura a la Experiencia"] >= 60 and resultados["Extraversión"] <= 40:
        recs.append("Investigación/Análisis — creativo e independiente.")
    if resultados["Amabilidad"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        recs.append("Coaching/Mentoring — empatía y estabilidad.")
    if resultados["Extraversión"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        recs.append("Dirección Comercial — influencia y control emocional.")
    if not recs:
        recs.append("Perfil versátil: apto para múltiples roles según intereses y experiencia.")
    for r in recs:
        st.markdown(f"- {r}")

    st.markdown("---")
    st.caption("Este informe es orientativo y no sustituye una evaluación profesional.")

    # Exportar CSV/PDF
    df_res = pd.DataFrame({
        "Dimensión": list(resultados.keys()),
        "Código": [DIMENSIONES[d]["code"] for d in resultados.keys()],
        "Puntuación": [f"{v:.1f}" for v in resultados.values()]
    })

    st.subheader("Exportar resultados")
    colL, colR = st.columns(2)
    with colL:
        st.download_button(
            "📊 Descargar CSV",
            data=df_res.to_csv(index=False).encode("utf-8"),
            mime="text/csv",
            file_name=f"BigFive_Resultados_{st.session_state.fecha_eval.replace(':','-').replace(' ','_')}.csv",
            use_container_width=True
        )
    with colR:
        empresa = st.text_input("Nombre de la empresa/área (opcional)", value="Corporativo")
        logo = st.file_uploader("Logo (PNG/JPG opcional)", type=["png","jpg","jpeg"])
        logo_bytes = logo.read() if logo else None
        if st.button("🧾 Descargar PDF", use_container_width=True):
            pdf = generar_pdf(empresa, st.session_state.fecha_eval, resultados, recs, logo_bytes)
            st.download_button(
                "Descargar Informe PDF",
                data=pdf,
                file_name=f"Informe_BigFive_{st.session_state.fecha_eval.replace(':','-').replace(' ','_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("---")
    if st.button("🔄 Nueva evaluación", type="primary"):
        st.session_state.stage = "inicio"
        st.session_state.current_dim_idx = 0
        st.session_state.respuestas = {p["key"]: None for p in PREGUNTAS}
        st.session_state.resultados = None
        st.session_state.fecha_eval = None
        scroll_top()
        st.rerun()

# =========================
# 6) ROUTER
# =========================
stage = st.session_state.stage
if stage == "inicio":
    vista_inicio()
elif stage == "test":
    vista_test()
elif stage == "resultados":
    vista_resultados()
