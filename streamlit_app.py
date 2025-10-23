import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

# Para PDF (sin librerías externas): usamos matplotlib + PdfPages
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ==============================
# CONFIGURACIÓN BÁSICA
# ==============================
st.set_page_config(page_title="Big Five PRO | Evaluación Profesional", page_icon="🧠", layout="wide")

# Estilos (fondo blanco, texto negro, suavidad visual; sin sidebar)
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
html, body, [data-testid="stAppViewContainer"] {
  background: #ffffff !important; color: #111 !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
.block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1180px; }
.dim-title {
  font-size: clamp(1.9rem, 5vw, 3rem);
  font-weight: 900; letter-spacing: .25px; line-height: 1.12;
  margin: .2rem 0 .6rem 0; animation: fadeSlide .45s ease-out;
}
@keyframes fadeSlide { from {opacity:0; transform: translateY(6px);} to {opacity:1; transform: translateY(0);} }
.card { border: 1px solid #ececec; border-radius: 14px; padding: 18px 18px; background: #fff; box-shadow: 0 2px 0 rgba(0,0,0,0.02); }
.kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin: 10px 0 6px 0; }
.kpi .k { border: 1px solid #ececec; border-radius: 14px; padding: 18px; background: #fff; }
.kpi .k .v { font-size: 1.8rem; font-weight: 800; }
.kpi .k .l { font-size: .95rem; opacity: .85; }
details summary { font-weight: 700; cursor: pointer; padding: 10px 0; }
.small { font-size:.95rem; opacity:.9; }
.accent { background: linear-gradient(135deg, #F2CC8F 0%, #E9C46A 100%); border: 1px solid #eee; }
hr { border: none; border-top: 1px solid #eee; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# ==============================
# MODELO BIG FIVE
# ==============================
def reverse_score(v: int) -> int:
    return 6 - v

DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O",
        "desc": "Imaginación, curiosidad intelectual, creatividad y apertura a la novedad.",
        "pros_high": ["Generación de ideas originales", "Aprendizaje autodirigido", "Flexibilidad cognitiva"],
        "risks_low": ["Preferencia por lo conocido", "Menor curiosidad por conceptos abstractos", "Resistencia a cambios"],
        "recs_low": ["Micro-experimentos semanales", "Lecturas breves de temas nuevos", "Sesiones guiadas de ideación"],
        "roles_high": ["Innovación", "Diseño", "Estrategia", "I+D", "Consultoría"],
        "roles_low": ["Operaciones estandarizadas", "Back Office", "Control de Calidad"]
    },
    "Responsabilidad": {
        "code": "C",
        "desc": "Autodisciplina, orden, planificación y cumplimiento de objetivos.",
        "pros_high": ["Alta fiabilidad", "Gestión del tiempo sólida", "Orientación a estándares"],
        "risks_low": ["Procrastinación", "Desorden y olvidos", "Baja finalización de tareas"],
        "recs_low": ["Checklists diarios", "Timeboxing", "Revisión semanal de prioridades"],
        "roles_high": ["Gestión de Proyectos", "Finanzas", "Auditoría", "Operaciones"],
        "roles_low": ["Ideación temprana sin plazos", "Exploración creativa abierta"]
    },
    "Extraversión": {
        "code": "E",
        "desc": "Sociabilidad, asertividad, energía en interacción y visibilidad pública.",
        "pros_high": ["Networking efectivo", "Energía en equipos", "Comunicación en público"],
        "risks_low": ["Incomodidad en grupos grandes", "Preferencia por trabajo solitario", "Evita exposición pública"],
        "recs_low": ["Exposición gradual", "Reuniones 1:1 previas a plenarias", "Guiones breves para presentaciones"],
        "roles_high": ["Ventas", "Liderazgo Comercial", "Relaciones Públicas", "BD"],
        "roles_low": ["Análisis", "Investigación", "Programación", "Data"]
    },
    "Amabilidad": {
        "code": "A",
        "desc": "Cooperación, empatía, confianza y respeto por los demás.",
        "pros_high": ["Clima de confianza", "Gestión de conflictos con empatía", "Orientación a servicio"],
        "risks_low": ["Estilo directo/escéptico", "Relaciones sensibles desafiantes", "Menor tolerancia a ambigüedad emocional"],
        "recs_low": ["Escucha activa", "Reformular juicios por hipótesis", "Feedback con método SBI"],
        "roles_high": ["RR.HH.", "Customer Success", "Mediación", "Servicio al Cliente"],
        "roles_low": ["Negociación dura", "Trading", "Toma de decisiones impopulares"]
    },
    "Estabilidad Emocional": {
        "code": "N",
        "desc": "Gestión del estrés, resiliencia y calma bajo presión (opuesto a Neuroticismo).",
        "pros_high": ["Serenidad ante presión", "Recuperación rápida", "Decisiones estables"],
        "risks_low": ["Estrés/rumiación", "Cambios de ánimo", "Sobrecarga ante incertidumbre"],
        "recs_low": ["Respiración 4-7-8", "Rutina de sueño/pausas", "Journaling breve"],
        "roles_high": ["Operaciones Críticas", "Dirección", "Soporte Incidentes", "Compliance"],
        "roles_low": ["Ambientes caóticos sin soporte", "Creativo con deadlines difusos"]
    },
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

LIKERT = {1: "Totalmente en desacuerdo", 2: "En desacuerdo", 3: "Neutral", 4: "De acuerdo", 5: "Totalmente de acuerdo"}
LIKERT_KEYS = list(LIKERT.keys())

# 10 preguntas por dimensión (5 directas + 5 inversas)
PREGUNTAS = [
    # O
    {"text": "Tengo una imaginación muy activa.", "dim": "Apertura a la Experiencia", "key": "O1", "rev": False},
    {"text": "Me atraen ideas nuevas y complejas.", "dim": "Apertura a la Experiencia", "key": "O2", "rev": False},
    {"text": "Disfruto del arte y la cultura.", "dim": "Apertura a la Experiencia", "key": "O3", "rev": False},
    {"text": "Busco experiencias poco convencionales.", "dim": "Apertura a la Experiencia", "key": "O4", "rev": False},
    {"text": "Valoro la creatividad sobre la rutina.", "dim": "Apertura a la Experiencia", "key": "O5", "rev": False},
    {"text": "Prefiero mantener hábitos antes que probar cosas nuevas.", "dim": "Apertura a la Experiencia", "key": "O6", "rev": True},
    {"text": "Las discusiones filosóficas me parecen poco útiles.", "dim": "Apertura a la Experiencia", "key": "O7", "rev": True},
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
    {"text": "Disfruto ser visible en reuniones.", "dim": "Extraversión", "key": "E1", "rev": False},
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
        raw = answers.get(p["key"])
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

def dynamic_lists(dim_name: str, score: float):
    info = DIMENSIONES[dim_name]
    if score >= 60:
        fortalezas = info["pros_high"]
        # oportunidades específicas según dimensión alta
        if dim_name == "Apertura a la Experiencia":
            oportunidades = ["Evitar dispersión en demasiadas iniciativas", "Aterrizar ideas en planes ejecutables"]
        elif dim_name == "Responsabilidad":
            oportunidades = ["Evitar perfeccionismo paralizante", "Mantener flexibilidad cuando cambian las prioridades"]
        elif dim_name == "Extraversión":
            oportunidades = ["Cuidar espacios de escucha activa", "Dejar hablar a los más reservados"]
        elif dim_name == "Amabilidad":
            oportunidades = ["Poner límites sanos", "Resolver conflictos sin evitar conversaciones difíciles"]
        else:  # Estabilidad Emocional
            oportunidades = ["Evitar exceso de confianza ante riesgos", "No subestimar señales tempranas de estrés del equipo"]
        recomendaciones = ["OKRs trimestrales con métricas de resultado", "Revisiones quincenales de foco y prioridades"]
        roles = info["roles_high"]
    elif score < 40:
        # bajo
        if dim_name == "Apertura a la Experiencia":
            fortalezas = ["Enfoque práctico y realista"]
        elif dim_name == "Responsabilidad":
            fortalezas = ["Espontaneidad y reacción rápida ante cambios"]
        elif dim_name == "Extraversión":
            fortalezas = ["Profundidad en trabajo individual y concentrado"]
        elif dim_name == "Amabilidad":
            fortalezas = ["Objetividad y comunicación directa"]
        else:
            fortalezas = ["Sensibilidad que potencia la creatividad"]
        oportunidades = info["risks_low"]
        recomendaciones = info["recs_low"]
        roles = info["roles_low"]
    else:
        # promedio
        fortalezas = ["Buen balance situacional", "Adaptabilidad según contexto"]
        oportunidades = ["Identificar cuándo subir/bajar esta palanca conductual", "Consolidar rituales que mantengan el equilibrio"]
        recomendaciones = ["Micro-hábitos 2–3 por semana", "Feedback mensual con pares o líder"]
        roles = info["roles_high"][:2] + info["roles_low"][:1]
    return fortalezas, oportunidades, recomendaciones, roles

# ==============================
# CALLBACKS
# ==============================
def on_answer_change():
    i = st.session_state.q_index
    p = PREGUNTAS[i]
    val = st.session_state.get(f"resp_{p['key']}")
    st.session_state.answers[p["key"]] = val
    if i < len(PREGUNTAS) - 1:
        st.session_state.q_index = i + 1
    else:
        st.session_state.stage = "resultados"
        st.session_state.fecha_eval = datetime.now().strftime("%d/%m/%Y %H:%M")

def restart():
    st.session_state.stage = "inicio"
    st.session_state.q_index = 0
    st.session_state.answers = {p["key"]: None for p in PREGUNTAS}
    st.session_state.fecha_eval = None

# ==============================
# VISTAS
# ==============================
def view_inicio():
    st.markdown(
        """
        <div class="card accent">
          <h1 style="margin:0 0 6px 0; font-size:clamp(1.9rem,3.8vw,2.8rem); font-weight:900;">🧠 Test Big Five (OCEAN)</h1>
          <p class="small" style="margin:0;">Evaluación profesional con resultados accionables, métricas y visualizaciones. Fondo blanco, alto contraste, diseño responsivo.</p>
        </div>
        """, unsafe_allow_html=True
    )
    col1, col2 = st.columns([1.35, 1])
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
              <p class="small">Duración estimada: <b>8–12 min</b> · 50 ítems Likert (1–5) · Avance automático al responder.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="card">
              <h3 style="margin-top:0">Cómo funciona</h3>
              <ol style="margin-top:6px; line-height:1.6">
                <li>Verás una pregunta por pantalla (con su dimensión).</li>
                <li>Elige tu opción (1 a 5) y pasarás automáticamente.</li>
                <li>Al finalizar, verás resultados, KPIs y podrás descargar el PDF.</li>
              </ol>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("🚀 Iniciar evaluación", type="primary", use_container_width=True):
            st.session_state.stage = "test"
            st.session_state.q_index = 0

def view_test():
    i = st.session_state.q_index
    p = PREGUNTAS[i]
    dim = p["dim"]
    code = DIMENSIONES[dim]["code"]

    pct = (i+1)/len(PREGUNTAS)
    st.progress(pct, text=f"Progreso: {i+1}/{len(PREGUNTAS)} preguntas")

    st.markdown(f"<div class='dim-title'>{code} — {dim}</div>", unsafe_allow_html=True)
    st.caption(DIMENSIONES[dim]["desc"])
    st.markdown("---")

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

def make_plotly_radar(results: dict):
    order = list(results.keys())
    values = [results[d] for d in order]
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
    return fig_radar

def make_plotly_bar(results: dict):
    palette = ["#E07A5F", "#81B29A", "#F2CC8F", "#9C6644", "#6D597A"]
    dfb = pd.DataFrame({"Dimensión": list(results.keys()), "Puntuación": list(results.values())}).sort_values("Puntuación", ascending=True)
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
    return fig_bar, dfb

def build_pdf_bytes(results: dict, fecha_eval: str):
    """
    Genera un PDF (bytes) con matplotlib PdfPages:
    - Portada con KPIs
    - Radar y Barras (recreados en matplotlib)
    - Tabla
    - Análisis por dimensión
    """
    buf = BytesIO()
    with PdfPages(buf) as pdf:
        order = list(results.keys())
        values = [results[d] for d in order]
        promedio_total = np.mean(values)
        std = np.std(values, ddof=1) if len(values) > 1 else 0.0
        rango = np.max(values) - np.min(values)
        top_dim = max(results, key=results.get)

        # Página 1: Portada / KPIs
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 en pulgadas
        plt.axis('off')
        plt.text(0.5, 0.92, "Informe de Personalidad Big Five", ha='center', va='center', fontsize=20, fontweight='bold')
        plt.text(0.5, 0.88, f"Fecha: {fecha_eval}", ha='center', fontsize=11)
        plt.text(0.15, 0.78, f"Promedio general: {promedio_total:.1f}", fontsize=14)
        plt.text(0.15, 0.74, f"Desviación estándar: {std:.2f}", fontsize=14)
        plt.text(0.15, 0.70, f"Rango: {rango:.2f}", fontsize=14)
        plt.text(0.15, 0.66, f"Dimensión destacada: {top_dim}", fontsize=14)
        plt.text(0.5, 0.58, "Dimensiones", ha='center', fontsize=14, fontweight='bold')
        for idx, d in enumerate(order):
            plt.text(0.15, 0.54 - idx*0.04, f"{DIMENSIONES[d]['code']} — {d}: {results[d]:.1f}", fontsize=12)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # Página 2: Barras (matplotlib)
        fig2 = plt.figure(figsize=(8.27, 11.69))
        ax = fig2.add_subplot(111)
        y = np.arange(len(order))
        vals = [results[d] for d in order]
        ax.barh(y, vals, color="#81B29A")
        ax.set_yticks(y)
        ax.set_yticklabels(order)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Puntuación (0-100)")
        ax.set_title("Puntuaciones por dimensión")
        for i, v in enumerate(vals):
            ax.text(v + 1, i, f"{v:.1f}", va='center', fontsize=9)
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

        # Página 3+: Análisis por dimensión
        for d in order:
            score = results[d]
            lvl, tag = label_level(score)
            f, o, r, roles = dynamic_lists(d, score)
            fig3 = plt.figure(figsize=(8.27, 11.69))
            plt.axis('off')
            plt.text(0.5, 0.95, f"{DIMENSIONES[d]['code']} — {d}", ha='center', fontsize=16, fontweight='bold')
            plt.text(0.5, 0.92, f"Puntuación: {score:.1f} · Nivel: {lvl} ({tag})", ha='center', fontsize=11)
            plt.text(0.08, 0.86, "Descripción", fontsize=13, fontweight='bold')
            plt.text(0.08, 0.83, DIMENSIONES[d]["desc"], fontsize=11, wrap=True)

            def draw_list(y, title, items):
                plt.text(0.08, y, title, fontsize=13, fontweight='bold')
                yy = y - 0.03
                for it in items:
                    plt.text(0.10, yy, f"• {it}", fontsize=11)
                    yy -= 0.03
                return yy - 0.02

            yy = 0.78
            yy = draw_list(yy, "Fortalezas", f)
            yy = draw_list(yy, "Oportunidades", o)
            yy = draw_list(yy, "Recomendaciones", r)
            draw_list(yy, "Cargos sugeridos", roles)

            pdf.savefig(fig3, bbox_inches='tight')
            plt.close(fig3)

    buf.seek(0)
    return buf.read()

def view_resultados():
    results = compute_scores(st.session_state.answers)
    order = list(results.keys())
    values = [results[d] for d in order]
    promedio_total = round(float(np.mean(values)), 1)
    dispersion = round(float(np.std(values, ddof=1)), 2) if len(values) > 1 else 0.0
    rango = round(float(np.max(values) - np.min(values)), 2)

    st.markdown(
        f"""
        <div class="card">
          <h1 style="margin:0 0 6px 0; font-size:clamp(1.9rem,3.8vw,2.8rem); font-weight:900;">📊 Informe de Personalidad Big Five</h1>
          <p class="small" style="margin:0;">Fecha de evaluación: <b>{st.session_state.fecha_eval}</b></p>
        </div>
        """, unsafe_allow_html=True
    )

    # KPIs
    st.markdown("<div class='kpi'>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{promedio_total:.1f}</div><div class='l'>Promedio general (0–100)</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{dispersion:.2f}</div><div class='l'>Desviación estándar</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{rango:.2f}</div><div class='l'>Rango</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='k'><div class='v'>{max(results, key=results.get)}</div><div class='l'>Dimensión destacada</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Gráficos (Plotly)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Radar del perfil")
        st.plotly_chart(make_plotly_radar(results), use_container_width=True)
    with c2:
        st.subheader("📊 Puntuaciones por dimensión")
        fig_bar, dfb = make_plotly_bar(results)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Resumen de resultados")
    tabla = pd.DataFrame({
        "Código": [DIMENSIONES[d]["code"] for d in order],
        "Dimensión": order,
        "Puntuación": [f"{results[d]:.1f}" for d in order],
        "Nivel": [label_level(results[d])[0] for d in order],
        "Etiqueta": [label_level(results[d])[1] for d in order],
    })
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔍 Análisis cualitativo por dimensión")
    # Bloques por dimensión (dinámico, basado en resultados)
    for d in DIMENSIONES_LIST:
        score = results[d]
        lvl, tag = label_level(score)
        fortalezas, oportunidades, recomendaciones, roles = dynamic_lists(d, score)
        info = DIMENSIONES[d]
        with st.expander(f"{info['code']} — {d}: {score:.1f} ({lvl})", expanded=True):
            colA, colB = st.columns([1, 2])
            with colA:
                # medidor simple textual
                st.markdown("**Indicador (0–100)**")
                st.markdown(f"<div class='card'><div style='font-size:2rem; font-weight:800'>{score:.1f}</div><div class='small'>{lvl} · {tag}</div></div>", unsafe_allow_html=True)
            with colB:
                st.markdown(f"**Descripción:** {info['desc']}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**Fortalezas**")
                    st.markdown("<ul>" + "".join([f"<li>{x}</li>" for x in fortalezas]) + "</ul>", unsafe_allow_html=True)
                with c2:
                    st.markdown("**Oportunidades**")
                    st.markdown("<ul>" + "".join([f"<li>{x}</li>" for x in oportunidades]) + "</ul>", unsafe_allow_html=True)
                with c3:
                    st.markdown("**Recomendaciones**")
                    st.markdown("<ul>" + "".join([f"<li>{x}</li>" for x in recomendaciones]) + "</ul>", unsafe_allow_html=True)
                st.markdown("**Cargos sugeridos**")
                st.markdown("<ul>" + "".join([f"<li>{x}</li>" for x in roles]) + "</ul>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📥 Exportar informe")

    # Generar PDF (server-side, sin blanco)
    pdf_bytes = build_pdf_bytes(results, st.session_state.fecha_eval)
    st.download_button(
        "⬇️ Descargar PDF",
        data=pdf_bytes,
        file_name="Informe_BigFive.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.caption("El PDF incluye KPIs, barras, tabla y análisis por dimensión.")

    st.markdown("---")
    if st.button("🔄 Realizar nueva evaluación", type="primary", use_container_width=True):
        restart()

# ==============================
# FLUJO
# ==============================
if st.session_state.stage == "inicio":
    view_inicio()
elif st.session_state.stage == "test":
    view_test()
else:
    view_resultados()
