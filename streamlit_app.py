# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ========= CONFIG =========
st.set_page_config(
    page_title="Test Big Five (OCEAN) · Evaluación Profesional",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ========= ESTILO GLOBAL (blanco/negro + toques suaves) =========
# Sin barra lateral, tipografía limpia y tarjetas suaves
BASE_CSS = """
<style>
    /* Global */
    .stApp { background: #ffffff; color: #111111; }
    h1, h2, h3, h4, h5 { color: #111; }
    .big-title { font-size: 2.0rem; font-weight: 800; margin: 0 0 4px 0;}
    .dim-badge { font-size: 0.95rem; letter-spacing: .5px; opacity:.85; }
    .question { font-size: 1.35rem; font-weight: 700; margin: 10px 0 6px 0; }
    .soft-card {border: 1px solid #eee; background: #fff; border-radius: 14px; padding: 16px;}
    .kpi-card {border: 1px solid #eee; background: #fff; border-radius: 12px; padding: 14px; min-height: 92px;}
    .chip { display:inline-block; padding:4px 10px; border-radius:999px; background:#f3f3f3; font-size:.85rem; }
    .section-title { font-weight:800; font-size:1.2rem; margin: 6px 0 4px 0;}
    .subtle { color:#444; font-size:.95rem; }
    .divider { border-top: 1px solid #eee; margin: 18px 0; }
    /* Botones: negros sobrios, contrastados */
    div.stButton > button[kind="primary"] { background:#111 !important; color:#fff !important; border-radius:10px; }
    div.stButton > button { border-radius:10px; }
    /* Ocultar barra lateral si existiera */
    section[data-testid="stSidebar"] { display:none !important; }
    /* Tab headers más claros */
    div[data-baseweb="tab-list"] { gap: 4px; }
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)

# ========= MODELO BIG FIVE =========
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O",
        "desc": "Imaginación, curiosidad, creatividad y aprecio por lo nuevo.",
        "color": "#8FB996",
    },
    "Responsabilidad": {
        "code": "C",
        "desc": "Organización, disciplina, orientación a objetivos y confiabilidad.",
        "color": "#A1C3D1",
    },
    "Extraversión": {
        "code": "E",
        "desc": "Sociabilidad, asertividad, energía y gusto por la interacción.",
        "color": "#F2C6B4",
    },
    "Amabilidad": {
        "code": "A",
        "desc": "Cooperación, empatía, confianza y respeto por los demás.",
        "color": "#E8D6CB",
    },
    "Estabilidad Emocional": {
        "code": "N",
        "desc": "Manejo del estrés, calma y resiliencia (opuesto a Neuroticismo).",
        "color": "#D6EADF",
    },
}
DIM_LIST = list(DIMENSIONES.keys())

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

# 10 preguntas por dimensión (5 directas + 5 inversas)
# Puedes personalizarlas si lo deseas.
PREGUNTAS = []
# O
PREGUNTAS += [
    {"dim": "Apertura a la Experiencia", "key":"O1","text":"Disfruto aprendiendo conceptos nuevos.", "rev":False},
    {"dim": "Apertura a la Experiencia", "key":"O2","text":"Tengo una imaginación muy activa.", "rev":False},
    {"dim": "Apertura a la Experiencia", "key":"O3","text":"Me interesan el arte y la cultura.", "rev":False},
    {"dim": "Apertura a la Experiencia", "key":"O4","text":"Me atraen los retos intelectuales.", "rev":False},
    {"dim": "Apertura a la Experiencia", "key":"O5","text":"Valoro la creatividad y la originalidad.", "rev":False},
    {"dim": "Apertura a la Experiencia", "key":"O6","text":"Prefiero la rutina a probar cosas nuevas.", "rev":True},
    {"dim": "Apertura a la Experiencia", "key":"O7","text":"Rara vez reflexiono sobre ideas abstractas.", "rev":True},
    {"dim": "Apertura a la Experiencia", "key":"O8","text":"No me interesan debates sobre ideas.", "rev":True},
    {"dim": "Apertura a la Experiencia", "key":"O9","text":"Me cuesta aceptar cambios en métodos.", "rev":True},
    {"dim": "Apertura a la Experiencia", "key":"O10","text":"Evito experiencias poco conocidas.", "rev":True},
]
# C
PREGUNTAS += [
    {"dim": "Responsabilidad", "key":"C1","text":"Cumplo plazos y compromisos.", "rev":False},
    {"dim": "Responsabilidad", "key":"C2","text":"Soy organizado/a en mis tareas.", "rev":False},
    {"dim": "Responsabilidad", "key":"C3","text":"Planifico antes de ejecutar.", "rev":False},
    {"dim": "Responsabilidad", "key":"C4","text":"Soy constante y disciplinado/a.", "rev":False},
    {"dim": "Responsabilidad", "key":"C5","text":"Me esfuerzo por la excelencia.", "rev":False},
    {"dim": "Responsabilidad", "key":"C6","text":"Procrastino actividades importantes.", "rev":True},
    {"dim": "Responsabilidad", "key":"C7","text":"Me distraigo con facilidad.", "rev":True},
    {"dim": "Responsabilidad", "key":"C8","text":"Evito responsabilidades cuando puedo.", "rev":True},
    {"dim": "Responsabilidad", "key":"C9","text":"Dejo mi área de trabajo desordenada.", "rev":True},
    {"dim": "Responsabilidad", "key":"C10","text":"Me cuesta seguir procedimientos.", "rev":True},
]
# E
PREGUNTAS += [
    {"dim": "Extraversión", "key":"E1","text":"Disfruto hablar en público.", "rev":False},
    {"dim": "Extraversión", "key":"E2","text":"Tomo la iniciativa en grupos.", "rev":False},
    {"dim": "Extraversión", "key":"E3","text":"Me energiza trabajar con otras personas.", "rev":False},
    {"dim": "Extraversión", "key":"E4","text":"Me siento cómodo/a con desconocidos.", "rev":False},
    {"dim": "Extraversión", "key":"E5","text":"Me gusta liderar conversaciones.", "rev":False},
    {"dim": "Extraversión", "key":"E6","text":"Prefiero trabajar en silencio y solo/a.", "rev":True},
    {"dim": "Extraversión", "key":"E7","text":"Evito interacciones sociales prolongadas.", "rev":True},
    {"dim": "Extraversión", "key":"E8","text":"Soy una persona más bien reservada.", "rev":True},
    {"dim": "Extraversión", "key":"E9","text":"Me cuesta expresar mis puntos en grupos.", "rev":True},
    {"dim": "Extraversión", "key":"E10","text":"Prefiero observar a participar.", "rev":True},
]
# A
PREGUNTAS += [
    {"dim": "Amabilidad", "key":"A1","text":"Empatizo con facilidad.", "rev":False},
    {"dim": "Amabilidad", "key":"A2","text":"Me importa el bienestar de otros.", "rev":False},
    {"dim": "Amabilidad", "key":"A3","text":"Colaboro y busco consensos.", "rev":False},
    {"dim": "Amabilidad", "key":"A4","text":"Confío en la buena intención de los demás.", "rev":False},
    {"dim": "Amabilidad", "key":"A5","text":"Mantengo respeto en desacuerdos.", "rev":False},
    {"dim": "Amabilidad", "key":"A6","text":"Soy cínico/a respecto a las intenciones ajenas.", "rev":True},
    {"dim": "Amabilidad", "key":"A7","text":"Puedo ser directo/a hasta lo brusco.", "rev":True},
    {"dim": "Amabilidad", "key":"A8","text":"Me cuesta ponerme en el lugar del otro.", "rev":True},
    {"dim": "Amabilidad", "key":"A9","text":"Suelo priorizar mis intereses por encima del equipo.", "rev":True},
    {"dim": "Amabilidad", "key":"A10","text":"La cooperación no es una prioridad para mí.", "rev":True},
]
# N (Estabilidad Emocional)
PREGUNTAS += [
    {"dim": "Estabilidad Emocional", "key":"N1","text":"Mantengo la calma bajo presión.", "rev":False},
    {"dim": "Estabilidad Emocional", "key":"N2","text":"Me recupero rápido de contratiempos.", "rev":False},
    {"dim": "Estabilidad Emocional", "key":"N3","text":"Gestiono el estrés de forma saludable.", "rev":False},
    {"dim": "Estabilidad Emocional", "key":"N4","text":"Suelo mantener el foco aun con presión.", "rev":False},
    {"dim": "Estabilidad Emocional", "key":"N5","text":"Me siento seguro/a de mis capacidades.", "rev":False},
    {"dim": "Estabilidad Emocional", "key":"N6","text":"Me preocupo en exceso por pequeñas cosas.", "rev":True},
    {"dim": "Estabilidad Emocional", "key":"N7","text":"Me irrito con facilidad.", "rev":True},
    {"dim": "Estabilidad Emocional", "key":"N8","text":"Mi estado de ánimo fluctúa con frecuencia.", "rev":True},
    {"dim": "Estabilidad Emocional", "key":"N9","text":"El estrés me sobrepasa habitualmente.", "rev":True},
    {"dim": "Estabilidad Emocional", "key":"N10","text":"Me cuesta recuperar la calma.", "rev":True},
]

# ========= STATE =========
if "stage" not in st.session_state:
    st.session_state.stage = "inicio"
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {p["key"]: None for p in PREGUNTAS}
if "result" not in st.session_state:
    st.session_state.result = None
if "fecha" not in st.session_state:
    st.session_state.fecha = None

# ========= UTIL =========
def as_percent(value_1_to_5: float) -> float:
    # 1..5 -> 0..100
    return round(((value_1_to_5 - 1.0) / 4.0) * 100.0, 1)

def compute_scores(answers: dict) -> dict:
    per_dim = {d: [] for d in DIM_LIST}
    for p in PREGUNTAS:
        v = answers.get(p["key"])
        if v is None:
            v = 3
        if p["rev"]:
            v = reverse_score(v)
        per_dim[p["dim"]].append(v)
    res = {}
    for d, vals in per_dim.items():
        avg = float(np.mean(vals)) if vals else 3.0
        res[d] = as_percent(avg)
    return res

def level_label(score: float):
    if score >= 75: return "Muy Alto", "Dominante"
    if score >= 60: return "Alto", "Marcado"
    if score >= 40: return "Promedio", "Moderado"
    if score >= 25: return "Bajo", "Suave"
    return "Muy Bajo", "Mínimo"

# ========= GAUGES (SEMICIRCULAR PLOTLY) =========
def semi_gauge_plotly(value: float, title: str = "", color="#6D597A"):
    """
    Medidor semicircular (0–100) construido con sectores + aguja.
    Colores suaves por rango.
    """
    v = max(0, min(100, float(value)))

    # Sectores (0-25-40-60-75-100) -> 5 segmentos
    bounds = [0, 25, 40, 60, 75, 100]
    colors = ["#fde2e1", "#fff0c2", "#e9f2fb", "#e7f6e8", "#d9f2db"]
    vals = [bounds[i+1]-bounds[i] for i in range(len(bounds)-1)]

    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=vals,
        hole=0.6,
        rotation=180,
        direction="clockwise",
        text=[f"{bounds[i]}–{bounds[i+1]}" for i in range(5)],
        textinfo="none",
        marker=dict(colors=colors, line=dict(color="#ffffff", width=1)),
        hoverinfo="skip",
        showlegend=False,
        sort=False
    ))

    # Aguja
    theta = (180 * (v/100.0))  # 0->100 maps 0..180 degrees
    # End point (in unit circle coords)
    import math
    r = 0.95
    x0, y0 = 0.5, 0.5
    xe = x0 + r*math.cos(math.radians(180 - theta))
    ye = y0 + r*math.sin(math.radians(180 - theta))

    fig.add_shape(
        type="line", x0=x0, y0=y0, x1=xe, y1=ye,
        line=dict(color=color, width=4)
    )
    fig.add_shape(
        type="circle", x0=x0-0.02, y0=y0-0.02, x1=x0+0.02, y1=y0+0.02,
        line=dict(color=color), fillcolor=color
    )

    fig.update_layout(
        annotations=[
            dict(text=f"<b>{v:.1f}</b>", x=0.5, y=0.32, showarrow=False, font=dict(size=24, color="#111")),
            dict(text=title, x=0.5, y=0.16, showarrow=False, font=dict(size=13, color="#333")),
        ],
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        height=220
    )
    return fig

# ========= PDF (matplotlib) con medidores semicirculares =========
def build_pdf(results: dict, fecha: str) -> bytes:
    """
    PDF A4 con:
    - Portada + KPIs
    - Tabla resumen + barras
    - Páginas por dimensión con medidor semicircular y análisis laboral
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from io import BytesIO
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.patches import Wedge, Circle, FancyBboxPatch

    order = list(results.keys())
    vals = np.array([results[d] for d in order], dtype=float)
    avg = float(np.mean(vals))
    std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    rng = float(np.max(vals) - np.min(vals)) if len(vals) > 1 else 0.0
    top_dim = max(results, key=results.get)
    low_dim = min(results, key=results.get)

    def semicircle(ax, value, cx=0.5, cy=0.5, r=0.45):
        v = max(0, min(100, float(value)))
        # bandas
        bands = [(0,25,"#fde2e1"), (25,40,"#fff0c2"), (40,60,"#e9f2fb"), (60,75,"#e7f6e8"), (75,100,"#d9f2db")]
        for a,b,c in bands:
            ang1 = 180*(a/100.0)
            ang2 = 180*(b/100.0)
            w = Wedge((cx,cy), r, 180-ang2, 180-ang1, facecolor=c, edgecolor="#fff", lw=1)
            ax.add_patch(w)
        # aguja
        import math
        theta = math.radians(180*(v/100.0))
        x2 = cx + r*0.95*math.cos(math.pi - theta)
        y2 = cy + r*0.95*math.sin(math.pi - theta)
        ax.plot([cx, x2], [cy, y2], color="#6D597A", lw=3)
        ax.add_patch(Circle((cx,cy), 0.02, color="#6D597A"))
        ax.text(cx, cy-0.12, f"{v:.1f}", ha="center", va="center", fontsize=16, color="#111")

    buf = BytesIO()
    with PdfPages(buf) as pdf:
        # PORTADA
        fig = plt.figure(figsize=(8.27, 11.69))
        ax = fig.add_axes([0,0,1,1]); ax.axis("off")
        ax.text(.5,.95,"Informe Big Five — Evaluación Laboral", ha="center", fontsize=20, fontweight="bold")
        ax.text(.5,.92,f"Fecha: {fecha}", ha="center", fontsize=11)

        # KPIs
        def kpi(ax, x, y, w, h, title, val):
            box = FancyBboxPatch((x,y), w,h, boxstyle="round,pad=0.02,rounding_size=0.02",
                                 facecolor="#fff", edgecolor="#e6e6e6")
            ax.add_patch(box)
            ax.text(x+w*0.06, y+h*0.63, title, fontsize=10, color="#333")
            ax.text(x+w*0.06, y+h*0.23, val, fontsize=20, fontweight="bold", color="#111")

        Y0, H, W, GAP = .82, .10, .40, .02
        kpi(ax, .06, Y0, W, H, "Promedio (0–100)", f"{avg:.1f}")
        kpi(ax, .54, Y0, W, H, "Desviación estándar", f"{std:.2f}")
        kpi(ax, .06, Y0-(H+GAP), W, H, "Rango entre dimensiones", f"{rng:.2f}")
        kpi(ax, .54, Y0-(H+GAP), W, H, "Dimensión destacada", f"{top_dim}")

        # Resumen
        ax.text(.06, .60, "Resumen profesional", fontsize=14, fontweight="bold")
        bullets = [
            f"Fortaleza clave: {top_dim} ({results[top_dim]:.1f})",
            f"Área a potenciar: {low_dim} ({results[low_dim]:.1f})",
            "Perfil global equilibrado" if 40 <= avg <= 60 else (
                "Perfil con tendencia alta para ambientes exigentes" if avg>60 else
                "Perfil conservador, ideal para entornos estables y normados"
            ),
            f"Variabilidad entre rasgos: DE={std:.2f} · Rango={rng:.2f}",
        ]
        yy = .56
        for b in bullets:
            ax.text(.08, yy, f"• {b}", fontsize=11); yy -= .03

        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

        # TABLA + BARRAS
        fig2 = plt.figure(figsize=(8.27, 11.69))
        ax2 = fig2.add_axes([0,0,1,1]); ax2.axis("off")
        ax2.text(.06,.96,"Tabla resumen de puntuaciones", fontsize=14, fontweight="bold")
        y = .92
        ax2.text(.06, y, "Cod.", fontsize=11, fontweight="bold")
        ax2.text(.14, y, "Dimensión", fontsize=11, fontweight="bold")
        ax2.text(.56, y, "Puntaje", fontsize=11, fontweight="bold")
        ax2.text(.70, y, "Nivel", fontsize=11, fontweight="bold")
        ax2.text(.82, y, "Etiqueta", fontsize=11, fontweight="bold")
        y -= .03
        for d in order:
            lvl, tag = level_label(results[d])
            ax2.text(.06, y, DIMENSIONES[d]["code"], fontsize=10)
            ax2.text(.14, y, d, fontsize=10)
            ax2.text(.56, y, f"{results[d]:.1f}", fontsize=10)
            ax2.text(.70, y, f"{lvl}", fontsize=10)
            ax2.text(.82, y, f"{tag}", fontsize=10)
            y -= .026

        # Barras
        ax2.text(.06, y-.02, "Puntuaciones por dimensión", fontsize=14, fontweight="bold")
        axbar = fig2.add_axes([.06, y-.42, .88, .36])
        ypos = np.arange(len(order))[::-1]
        vals_order = [results[d] for d in order]
        axbar.barh(ypos, vals_order, color="#81B29A")
        axbar.set_yticks(ypos); axbar.set_yticklabels(order)
        axbar.set_xlim(0,100); axbar.set_xlabel("0–100")
        for i,v in enumerate(vals_order):
            axbar.text(v+1, i, f"{v:.1f}", va="center", fontsize=9)
        pdf.savefig(fig2, bbox_inches="tight"); plt.close(fig2)

        # PÁGINAS POR DIMENSIÓN (con medidor)
        for d in order:
            score = results[d]; lvl, tag = level_label(score)
            fort, risk, recs, roles, notapt, expl = build_dimension_blocks(d, score)

            fig3 = plt.figure(figsize=(8.27, 11.69))
            ax3 = fig3.add_axes([0,0,1,1]); ax3.axis("off")
            ax3.text(.5,.95, f"{DIMENSIONES[d]['code']} — {d}", ha="center", fontsize=18, fontweight="bold")
            ax3.text(.5,.92, f"Puntuación {score:.1f} · {lvl} ({tag})", ha="center", fontsize=11)

            # Medidor semicircular
            axg = fig3.add_axes([.18, .78, .64, .16]); axg.axis("off")
            semicircle(axg, score, cx=0.5, cy=0.0, r=0.9)

            def block(ax, y, title, items=None, text=None):
                ax.text(.06, y, title, fontsize=13, fontweight="bold"); y-=.03
                if text:
                    ax.text(.06, y, text, fontsize=11); y-=.035
                if items:
                    for it in items:
                        ax.text(.06, y, f"• {it}", fontsize=11); y-=.026
                return y-.005

            yb = .74
            yb = block(ax3, yb, "Descripción", text=DIMENSIONES[d]["desc"])
            yb = block(ax3, yb, "Explicativo del KPI", text=expl)
            yb = block(ax3, yb, "Fortalezas (laborales)", items=fort)
            yb = block(ax3, yb, "Riesgos / Cosas a cuidar", items=risk)
            yb = block(ax3, yb, "Recomendaciones", items=recs)
            yb = block(ax3, yb, "Roles sugeridos", items=roles)
            yb = block(ax3, yb, "No recomendado para", items=(notapt if notapt else ["—"]))

            pdf.savefig(fig3, bbox_inches="tight"); plt.close(fig3)

    buf.seek(0)
    return buf.read()

# ========= BLOQUES LABORALES (fortalezas, riesgos...) =========
def build_dimension_blocks(dim: str, score: float):
    lvl, tag = level_label(score)
    # Catálogo base por dimensión (puedes afinar los textos a tu gusto)
    base = {
        "Apertura a la Experiencia": dict(
            high=[
                "Genera ideas originales y mejora procesos.",
                "Aprende rápido y se adapta a cambios.",
                "Explora alternativas antes de decidir.",
            ],
            low=[
                "Puede apegarse demasiado a lo conocido.",
                "Menor interés por explorar enfoques nuevos.",
                "Riesgo de estancamiento en contextos dinámicos.",
            ],
            roles_high=["I+D", "Innovación", "Estrategia", "Consultoría", "Producto"],
            roles_low=["Operaciones tradicionales", "Roles de cumplimiento estricto"],
            not_apt_low=["Puestos que exigen alta creatividad disruptiva"],
            explain="Indica preferencia por lo nuevo versus lo convencional; útil para innovación o mantenimiento de procesos."
        ),
        "Responsabilidad": dict(
            high=[
                "Fiable, orientado a la ejecución y al detalle.",
                "Planificación consistente y disciplina.",
                "Excelente seguimiento de plazos y estándares.",
            ],
            low=[
                "Riesgo de procrastinar o perder foco.",
                "Necesita supervisión externa y recordatorios.",
                "Dificultad para sostener rutinas de control.",
            ],
            roles_high=["Gestión de Proyectos", "Calidad", "Finanzas", "PMO"],
            roles_low=["Creativos sin estructura", "Entornos caóticos"],
            not_apt_low=["Puestos críticos de control normativo sin apoyo"],
            explain="Refleja orden, disciplina y confiabilidad; clave para roles con procesos y estándares."
        ),
        "Extraversión": dict(
            high=[
                "Capacidad para influir y hacer networking.",
                "Energía en contextos colaborativos.",
                "Comunicación fluida con clientes y equipos.",
            ],
            low=[
                "Prefiere trabajo individual y concentrado.",
                "Menor espontaneidad en grandes grupos.",
                "Riesgo de sub-exposición en espacios políticos.",
            ],
            roles_high=["Ventas", "Relaciones Públicas", "Liderazgo de Equipos"],
            roles_low=["Análisis profundo individual", "I+D técnico aislado"],
            not_apt_low=["Roles de alta exposición pública permanente"],
            explain="Mide energía social y asertividad; útil para relación con clientes o coordinación ampliada."
        ),
        "Amabilidad": dict(
            high=[
                "Facilita la colaboración y la confianza.",
                "Capacidad de escucha y negociación.",
                "Gestiona conflictos con tacto.",
            ],
            low=[
                "Comunicación más directa y competitiva.",
                "Riesgo de fricción en equipos sensibles.",
                "Puede priorizar resultados sobre relaciones.",
            ],
            roles_high=["RR. HH.", "Servicio al Cliente", "Mediación", "Cultura"],
            roles_low=["Negociación dura", "Ambientes altamente competitivos"],
            not_apt_low=["Puestos que requieren fuerte diplomacia con alta sensibilidad social"],
            explain="Describe cooperación y empatía vs. franqueza competitiva; ajusta el estilo de influencia."
        ),
        "Estabilidad Emocional": dict(
            high=[
                "Mantiene la calma bajo presión.",
                "Toma decisiones serenas en crisis.",
                "Alta resiliencia ante contratiempos.",
            ],
            low=[
                "Vulnerable al estrés y a la reactividad.",
                "Necesita contención en picos de demanda.",
                "Riesgo de desgaste en plazos críticos.",
            ],
            roles_high=["Gestión de Crisis", "Operaciones de Alto Estrés", "Dirección"],
            roles_low=["Ambientes impredecibles sin soporte"],
            not_apt_low=["Puestos con exposición constante a conflicto o crisis severa"],
            explain="Evalúa manejo del estrés y regulación emocional; esencial para entornos demandantes."
        ),
    }
    b = base[dim]
    if score >= 60:
        fort = b["high"]
        risk = b["low"][:1] + ["Evitar la sobrecarga por asumir demasiadas interacciones." if dim=="Extraversión" else
                               "Evitar sobrerresponsabilizarse y no delegar."]  # matiz
        recs = [
            "Definir objetivos medibles y celebrar hitos.",
            "Compartir buenas prácticas con el equipo.",
            "Equilibrar producción con espacios de recuperación.",
        ]
        roles = b["roles_high"]
        not_apt = []
    elif score <= 40:
        fort = ["Potencial de foco profundo y consistencia cuando hay estructura."] if dim!="Extraversión" else \
               ["Mayor autonomía en tareas individuales de alta concentración."]
        fort += ["Aporta mirada realista y práctica."] if dim=="Apertura a la Experiencia" else []
        risk = b["low"]
        recs = [
            "Establecer rutinas y checklists.",
            "Uso de recordatorios y gestión visual del trabajo.",
            "Mentoría o pairing para sostener hábitos clave.",
        ]
        roles = b["roles_low"]
        not_apt = b["not_apt_low"]
    else:
        fort = ["Perfil balanceado; adapta su estilo al contexto."]
        risk = ["Atender picos de demanda con planificación anticipada."]
        recs = ["Clarificar expectativas y límites por proyecto.",
                "Solicitar feedback regular de pares y clientes."]
        roles = ["Roles mixtos (individual y colaborativo)", "Proyectos con interacción moderada"]
        not_apt = []
    explain = b["explain"]
    return fort, risk, recs, roles, not_apt, explain

# ========= CALLBACK (auto-avance) =========
def on_select():
    # Guardamos la respuesta actual y avanzamos
    idx = st.session_state.q_index
    if 0 <= idx < len(PREGUNTAS):
        q = PREGUNTAS[idx]
        sel = st.session_state.get(f"sel_{q['key']}")
        if sel is not None:
            st.session_state.answers[q["key"]] = sel
            st.session_state.q_index = idx + 1
            if st.session_state.q_index >= len(PREGUNTAS):
                st.session_state.result = compute_scores(st.session_state.answers)
                st.session_state.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.session_state.stage = "resultados"

# ========= VISTAS =========
def view_inicio():
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<div class="big-title">🧠 Test de Personalidad Big Five (OCEAN)</div>', unsafe_allow_html=True)
    st.caption("Evaluación profesional para contextos laborales (RR. HH., selección, desarrollo).")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.2,1,1])
    with c1:
        st.markdown("**Cómo funciona**")
        st.markdown("- 50 ítems (10 por dimensión), escala Likert 1 a 5.")
        st.markdown("- **Auto-avance:** al responder, pasa a la siguiente pregunta.")
        st.markdown("- Resultados: **KPIs**, medidores, radar, barras, comparativo y **análisis laboral**.")
    with c2:
        st.markdown("**Dimensiones**")
        for d in DIM_LIST:
            st.markdown(f"- **{DIMENSIONES[d]['code']}** · {d}")
    with c3:
        st.markdown("**Tiempo estimado**")
        st.markdown("- 8–12 minutos")
        st.markdown("- Puedes salir y volver; guardamos tu progreso en esta sesión.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    _, m, _ = st.columns([1,1,1])
    with m:
        if st.button("Iniciar evaluación", type="primary", use_container_width=True):
            st.session_state.stage = "test"
            st.session_state.q_index = 0
    st.markdown('</div>', unsafe_allow_html=True)

def view_test():
    idx = st.session_state.q_index
    if idx >= len(PREGUNTAS):
        # Cierre automático (por si el usuario recarga en la última)
        st.session_state.result = compute_scores(st.session_state.answers)
        st.session_state.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.session_state.stage = "resultados"
        st.rerun()

    q = PREGUNTAS[idx]
    dim = q["dim"]
    code = DIMENSIONES[dim]["code"]
    color = DIMENSIONES[dim]["color"]

    # Cabecera grande
    st.markdown(
        f"""
        <div class="soft-card">
            <div style="font-size:2.2rem;font-weight:900;margin-bottom:2px;">{code} · {dim}</div>
            <div class="dim-badge">{DIMENSIONES[dim]['desc']}</div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("")

    # Progreso
    prog = (idx)/len(PREGUNTAS)
    st.progress(prog, text=f"Progreso: {idx}/{len(PREGUNTAS)}")

    # Tarjeta de pregunta
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="question">{q["text"]}</div>', unsafe_allow_html=True)

    # Radio con callback de auto-advance
    st.radio(
        label="",
        options=LIKERT,
        format_func=lambda x: ESCALA_LIKERT[x],
        key=f"sel_{q['key']}",
        horizontal=True,
        on_change=on_select,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Selecciona una alternativa para continuar automáticamente.")

def view_resultados():
    res = st.session_state.result
    if not res:
        st.session_state.stage = "inicio"
        st.rerun()

    # KPIs superiores
    vals = np.array([res[d] for d in DIM_LIST], dtype=float)
    avg = float(np.mean(vals))
    std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    rng = float(np.max(vals) - np.min(vals)) if len(vals) > 1 else 0.0
    best = max(res, key=res.get)
    worst = min(res, key=res.get)

    st.markdown('<div class="big-title">📊 Resultados · Informe Profesional</div>', unsafe_allow_html=True)
    st.caption(f"Fecha de evaluación: {st.session_state.fecha}")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown('<div class="kpi-card"><div class="section-title">Promedio</div><div style="font-size:1.8rem;font-weight:800;">{:.1f}</div><div class="subtle">0–100</div></div>'.format(avg), unsafe_allow_html=True)
    with k2: st.markdown('<div class="kpi-card"><div class="section-title">Desviación Est.</div><div style="font-size:1.8rem;font-weight:800;">{:.2f}</div><div class="subtle">Variabilidad entre rasgos</div></div>'.format(std), unsafe_allow_html=True)
    with k3: st.markdown('<div class="kpi-card"><div class="section-title">Rango</div><div style="font-size:1.8rem;font-weight:800;">{:.2f}</div><div class="subtle">Máx - Mín</div></div>'.format(rng), unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><div class="section-title">Destacado</div><div style="font-size:1.1rem;font-weight:800;">{best}</div><div class="subtle">{res[best]:.1f} pts</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Visualizaciones generales
    t1, t2, t3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])
    with t1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[res[d] for d in DIM_LIST],
            theta=[f"{DIMENSIONES[d]['code']} – {d}" for d in DIM_LIST],
            fill="toself",
            name="Perfil",
            line=dict(width=3, color="#6D597A"),
            fillcolor="rgba(109, 89, 122, .15)",
            marker=dict(size=6)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            showlegend=False,
            height=480,
            template="plotly_white"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with t2:
        df = pd.DataFrame({"Dimensión": DIM_LIST, "Puntuación": [res[d] for d in DIM_LIST]})
        df = df.sort_values("Puntuación", ascending=True)
        bar = go.Figure(go.Bar(
            x=df["Puntuación"], y=df["Dimensión"], orientation="h",
            text=df["Puntuación"].round(1), textposition="outside",
            marker=dict(color="#81B29A")
        ))
        bar.update_layout(height=480, xaxis=dict(range=[0,100]), template="plotly_white")
        st.plotly_chart(bar, use_container_width=True)

    with t3:
        comp = go.Figure()
        comp.add_trace(go.Bar(x=DIM_LIST, y=[res[d] for d in DIM_LIST], name="Perfil", marker=dict(color="#6D597A")))
        comp.add_trace(go.Bar(x=DIM_LIST, y=[50]*len(DIM_LIST), name="Promedio Poblacional", marker=dict(color="#D9D9D9")))
        comp.update_layout(barmode="group", height=480, yaxis=dict(range=[0,100]), template="plotly_white", showlegend=True)
        st.plotly_chart(comp, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Análisis por dimensión (laboral) – con medidor semicircular plotly
    st.markdown('<div class="big-title">🔎 Análisis por dimensión (laboral)</div>', unsafe_allow_html=True)
    st.caption("Fortalezas, riesgos, recomendaciones y ajuste a roles.")
    st.markdown("")

    for d in DIM_LIST:
        score = res[d]
        lvl, tag = level_label(score)
        with st.container():
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            st.markdown(f"### {DIMENSIONES[d]['code']} · {d}")
            st.plotly_chart(semi_gauge_plotly(score, title=f"{lvl} · {tag}"), use_container_width=True)

            fort, risk, recs, roles, notapt, expl = build_dimension_blocks(d, score)

            cA, cB = st.columns([1.1,1])
            with cA:
                st.markdown("**Descripción**")
                st.write(DIMENSIONES[d]["desc"])
                st.markdown("**Explicativo del KPI**")
                st.write(expl)

            with cB:
                st.markdown("**Indicadores**")
                st.write(f"- **Puntuación**: {score:.1f} (0–100)")
                st.write(f"- **Nivel**: {lvl} · **Etiqueta**: {tag}")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### ✅ Fortalezas (laborales)")
                for f in fort: st.markdown(f"- {f}")
                st.markdown("#### 🧭 Recomendaciones")
                for r in recs: st.markdown(f"- {r}")
            with c2:
                st.markdown("#### ⚠️ Riesgos / Cosas a cuidar")
                for r in risk: st.markdown(f"- {r}")
                st.markdown("#### 🎯 Roles sugeridos")
                for r in roles: st.markdown(f"- {r}")

            st.markdown("#### ⛔ No recomendado para")
            if notapt:
                for r in notapt: st.markdown(f"- {r}")
            else:
                st.markdown("- —")

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("")

    # Descarga de PDF
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    cdl, cr = st.columns([1,1])
    with cdl:
        try:
            pdf_bytes = build_pdf(res, st.session_state.fecha)
            st.download_button(
                "⬇️ Descargar informe en PDF",
                data=pdf_bytes,
                file_name="Informe_BigFive_Laboral.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error("No se pudo generar el PDF en este entorno.")
            st.caption(str(e))
    with cr:
        if st.button("🔄 Realizar nueva evaluación", use_container_width=True):
            st.session_state.stage = "inicio"
            st.session_state.q_index = 0
            st.session_state.answers = {p["key"]: None for p in PREGUNTAS}
            st.session_state.result = None

# ========= ROUTER =========
if st.session_state.stage == "inicio":
    view_inicio()
elif st.session_state.stage == "test":
    view_test()
elif st.session_state.stage == "resultados":
    view_resultados()
else:
    st.session_state.stage = "inicio"
    st.rerun()
