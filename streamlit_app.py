# ================================================================
#  Big Five (OCEAN) — Evaluación Laboral PRO (sin doble click)
# ================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import time

# Intento usar matplotlib (para PDF). Si no está, habrá fallback a HTML.
HAS_MPL = False
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.patches import FancyBboxPatch
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# ---------------------------------------------------------------
# Config general
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Big Five PRO | Evaluación Laboral",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------
# Estilos: fondo blanco, tipografías y UI suave
# ---------------------------------------------------------------
st.markdown("""
<style>
/* Ocultar sidebar */
[data-testid="stSidebar"] { display:none !important; }

/* Base */
html, body, [data-testid="stAppViewContainer"]{
  background:#ffffff !important; color:#111 !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
.block-container{ max-width:1200px; padding-top:0.8rem; padding-bottom:2rem; }

/* Títulos grandes y animados para dimensión */
.dim-title{
  font-size:clamp(2.2rem, 5vw, 3.2rem);
  font-weight:900; letter-spacing:.2px; line-height:1.12;
  margin:.2rem 0 .6rem 0;
  animation: slideIn .3s ease-out both;
}
@keyframes slideIn{
  from{ transform: translateY(6px); opacity:0; }
  to{ transform: translateY(0); opacity:1; }
}
.dim-desc{ margin:.1rem 0 1rem 0; opacity:.9; }

/* Tarjeta */
.card{
  border:1px solid #eee; border-radius:14px; background:#fff;
  box-shadow: 0 2px 0 rgba(0,0,0,0.03); padding:18px;
}

/* KPIs "animados" visualmente (CSS) */
.kpi-grid{
  display:grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
  gap:12px; margin:10px 0 6px 0;
}
.kpi{
  border:1px solid #eee; border-radius:14px; background:#fff; padding:16px;
  position:relative; overflow:hidden;
}
.kpi::after{
  content:""; position:absolute; inset:0;
  background: linear-gradient(120deg, rgba(255,255,255,0) 0%,
    rgba(240,240,240,0.7) 45%, rgba(255,255,255,0) 90%);
  transform: translateX(-100%);
  animation: shimmer 2s ease-in-out 1;
}
@keyframes shimmer { to{ transform: translateX(100%);} }
.kpi .label{ font-size:.95rem; opacity:.85; }
.kpi .value{ font-size:2.2rem; font-weight:900; line-height:1; }

/* "count-up" visual (CSS) con data-target (no JS real) — decorativo */
.countup[data-target]::after{ content: attr(data-target); }

/* Expander más limpio */
details, [data-testid="stExpander"]{
  background:#fff; border:1px solid #eee; border-radius:12px;
}

/* Tabla DataFrame más limpia */
[data-testid="stDataFrame"] div[role="grid"]{ font-size:0.95rem; }

/* Botones a ancho completo */
button[kind="primary"], button[kind="secondary"]{ width:100%; }

/* Color suave para elementos gráficos */
.tag{ display:inline-block; padding:.2rem .6rem; border:1px solid #eee; border-radius:999px; font-size:.82rem; }

hr{ border:none; border-top:1px solid #eee; margin:16px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Definiciones Big Five
# ---------------------------------------------------------------
def reverse_score(v:int)->int: return 6 - v

DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code":"O", "desc":"Curiosidad intelectual, creatividad y apertura al cambio.",
        "fort_high":["Ideas originales y mejora continua","Aprendizaje rápido y conexión de conceptos","Flexibilidad ante cambios"],
        "risk_high":["Dispersión o sobre-experimentación"],
        "fort_low":["Enfoque práctico y consistencia"],
        "risk_low":["Resistencia a cambios, menor interés por lo abstracto"],
        "recs_low":["Micro-experimentos semanales","Exposición breve a un tema nuevo"],
        "roles_high":["Innovación","I+D","Diseño","Estrategia","Consultoría"],
        "roles_low":["Operaciones estandarizadas","Control de calidad"]
    },
    "Responsabilidad": {
        "code":"C", "desc":"Orden, planificación, disciplina y cumplimiento de objetivos.",
        "fort_high":["Fiabilidad en plazos","Gestión del tiempo","Calidad consistente"],
        "risk_high":["Perfeccionismo y rigidez"],
        "fort_low":["Flexibilidad y espontaneidad"],
        "risk_low":["Procrastinación y baja finalización"],
        "recs_low":["Checklists diarios","Timeboxing","Revisión semanal de prioridades"],
        "roles_high":["Gestión de Proyectos","Finanzas","Auditoría","Operaciones"],
        "roles_low":["Ideación temprana abierta"]
    },
    "Extraversión": {
        "code":"E", "desc":"Asertividad, sociabilidad y energía en interacción.",
        "fort_high":["Networking y visibilidad","Energía en equipos","Comunicación en público"],
        "risk_high":["Hablar de más / baja escucha"],
        "fort_low":["Profundidad y foco individual","Comunicación escrita clara"],
        "risk_low":["Evita exposición y grandes grupos"],
        "recs_low":["Exposición gradual","Reuniones 1:1","Guiones breves para presentaciones"],
        "roles_high":["Ventas","Relaciones Públicas","Liderazgo Comercial","BD"],
        "roles_low":["Análisis","Investigación","Programación","Datos"]
    },
    "Amabilidad": {
        "code":"A", "desc":"Colaboración, empatía y confianza.",
        "fort_high":["Clima de confianza","Resolución empática de conflictos","Servicio al cliente"],
        "risk_high":["Evitar conversaciones difíciles","Dificultad para poner límites"],
        "fort_low":["Objetividad y firmeza"],
        "risk_low":["Relaciones sensibles desafiantes"],
        "recs_low":["Escucha activa","Feedback con método SBI","Definir límites claros"],
        "roles_high":["RR.HH.","Customer Success","Mediación","Atención de clientes"],
        "roles_low":["Negociación dura","Trading"]
    },
    "Estabilidad Emocional": {
        "code":"N", "desc":"Gestión del estrés, resiliencia y calma bajo presión.",
        "fort_high":["Serenidad en crisis","Recuperación rápida","Decisiones estables"],
        "risk_high":["Subestimar señales de estrés en otros"],
        "fort_low":["Sensibilidad que potencia creatividad y empatía"],
        "risk_low":["Rumiación/estrés, cambios de ánimo"],
        "recs_low":["Respiración 4-7-8","Rutina de pausas/sueño","Journaling breve"],
        "roles_high":["Operaciones críticas","Dirección","Soporte incidentes","Compliance"],
        "roles_low":["Ambientes caóticos sin soporte"]
    },
}
DIM_LIST = list(DIMENSIONES.keys())
LIKERT = {1:"Totalmente en desacuerdo", 2:"En desacuerdo", 3:"Neutral", 4:"De acuerdo", 5:"Totalmente de acuerdo"}
LIK_KEYS = list(LIKERT.keys())

# 50 ítems (10 por dimensión; 5 directos, 5 invertidos)
QUESTIONS = [
    # O
    {"text":"Tengo una imaginación muy activa.","dim":"Apertura a la Experiencia","key":"O1","rev":False},
    {"text":"Me atraen ideas nuevas y complejas.","dim":"Apertura a la Experiencia","key":"O2","rev":False},
    {"text":"Disfruto del arte y la cultura.","dim":"Apertura a la Experiencia","key":"O3","rev":False},
    {"text":"Busco experiencias poco convencionales.","dim":"Apertura a la Experiencia","key":"O4","rev":False},
    {"text":"Valoro la creatividad sobre la rutina.","dim":"Apertura a la Experiencia","key":"O5","rev":False},
    {"text":"Prefiero mantener hábitos que probar cosas nuevas.","dim":"Apertura a la Experiencia","key":"O6","rev":True},
    {"text":"Las discusiones filosóficas me parecen poco útiles.","dim":"Apertura a la Experiencia","key":"O7","rev":True},
    {"text":"Rara vez reflexiono sobre conceptos abstractos.","dim":"Apertura a la Experiencia","key":"O8","rev":True},
    {"text":"Me inclino por lo tradicional más que por lo original.","dim":"Apertura a la Experiencia","key":"O9","rev":True},
    {"text":"Evito cambiar mis hábitos establecidos.","dim":"Apertura a la Experiencia","key":"O10","rev":True},
    # C
    {"text":"Estoy bien preparado/a para mis tareas.","dim":"Responsabilidad","key":"C1","rev":False},
    {"text":"Cuido los detalles al trabajar.","dim":"Responsabilidad","key":"C2","rev":False},
    {"text":"Cumplo mis compromisos y plazos.","dim":"Responsabilidad","key":"C3","rev":False},
    {"text":"Sigo un plan y un horario definidos.","dim":"Responsabilidad","key":"C4","rev":False},
    {"text":"Me exijo altos estándares de calidad.","dim":"Responsabilidad","key":"C5","rev":False},
    {"text":"Dejo mis cosas desordenadas.","dim":"Responsabilidad","key":"C6","rev":True},
    {"text":"Evito responsabilidades cuando puedo.","dim":"Responsabilidad","key":"C7","rev":True},
    {"text":"Me distraigo con facilidad.","dim":"Responsabilidad","key":"C8","rev":True},
    {"text":"Olvido colocar las cosas en su lugar.","dim":"Responsabilidad","key":"C9","rev":True},
    {"text":"Aplazo tareas importantes.","dim":"Responsabilidad","key":"C10","rev":True},
    # E
    {"text":"Disfruto ser visible en reuniones.","dim":"Extraversión","key":"E1","rev":False},
    {"text":"Me siento a gusto con personas nuevas.","dim":"Extraversión","key":"E2","rev":False},
    {"text":"Busco la compañía de otras personas.","dim":"Extraversión","key":"E3","rev":False},
    {"text":"Participo activamente en conversaciones.","dim":"Extraversión","key":"E4","rev":False},
    {"text":"Me energiza compartir con otros.","dim":"Extraversión","key":"E5","rev":False},
    {"text":"Prefiero estar solo/a que rodeado/a de gente.","dim":"Extraversión","key":"E6","rev":True},
    {"text":"Soy más bien reservado/a y callado/a.","dim":"Extraversión","key":"E7","rev":True},
    {"text":"Me cuesta expresarme ante grupos grandes.","dim":"Extraversión","key":"E8","rev":True},
    {"text":"Prefiero actuar en segundo plano.","dim":"Extraversión","key":"E9","rev":True},
    {"text":"Me agotan las interacciones sociales prolongadas.","dim":"Extraversión","key":"E10","rev":True},
    # A
    {"text":"Empatizo con las emociones de los demás.","dim":"Amabilidad","key":"A1","rev":False},
    {"text":"Me preocupo por el bienestar ajeno.","dim":"Amabilidad","key":"A2","rev":False},
    {"text":"Trato a otros con respeto y consideración.","dim":"Amabilidad","key":"A3","rev":False},
    {"text":"Ayudo sin esperar nada a cambio.","dim":"Amabilidad","key":"A4","rev":False},
    {"text":"Confío en las buenas intenciones de la gente.","dim":"Amabilidad","key":"A5","rev":False},
    {"text":"No me interesa demasiado la gente.","dim":"Amabilidad","key":"A6","rev":True},
    {"text":"Sospecho de las intenciones ajenas.","dim":"Amabilidad","key":"A7","rev":True},
    {"text":"A veces soy poco considerado/a.","dim":"Amabilidad","key":"A8","rev":True},
    {"text":"Pienso primero en mí antes que en otros.","dim":"Amabilidad","key":"A9","rev":True},
    {"text":"Los problemas de otros no me afectan mucho.","dim":"Amabilidad","key":"A10","rev":True},
    # N
    {"text":"Me mantengo calmado/a bajo presión.","dim":"Estabilidad Emocional","key":"N1","rev":False},
    {"text":"Rara vez me siento ansioso/a o estresado/a.","dim":"Estabilidad Emocional","key":"N2","rev":False},
    {"text":"Soy emocionalmente estable.","dim":"Estabilidad Emocional","key":"N3","rev":False},
    {"text":"Me recupero rápido de contratiempos.","dim":"Estabilidad Emocional","key":"N4","rev":False},
    {"text":"Me siento seguro/a de mí mismo/a.","dim":"Estabilidad Emocional","key":"N5","rev":False},
    {"text":"Me preocupo demasiado por las cosas.","dim":"Estabilidad Emocional","key":"N6","rev":True},
    {"text":"Me irrito con facilidad.","dim":"Estabilidad Emocional","key":"N7","rev":True},
    {"text":"Con frecuencia me siento triste.","dim":"Estabilidad Emocional","key":"N8","rev":True},
    {"text":"Tengo cambios de ánimo frecuentes.","dim":"Estabilidad Emocional","key":"N9","rev":True},
    {"text":"El estrés me sobrepasa.","dim":"Estabilidad Emocional","key":"N10","rev":True},
]
KEY2IDX = {q["key"]:i for i,q in enumerate(QUESTIONS)}

# ---------------------------------------------------------------
# Estado
# ---------------------------------------------------------------
if "stage" not in st.session_state: st.session_state.stage = "inicio"  # inicio | test | resultados
if "q_idx" not in st.session_state: st.session_state.q_idx = 0
if "answers" not in st.session_state: st.session_state.answers = {q["key"]:None for q in QUESTIONS}
if "fecha" not in st.session_state: st.session_state.fecha = None
if "_needs_rerun" not in st.session_state: st.session_state._needs_rerun = False

# ---------------------------------------------------------------
# Cálculo de resultados
# ---------------------------------------------------------------
def compute_scores(answers:dict)->dict:
    buckets = {d:[] for d in DIM_LIST}
    for q in QUESTIONS:
        raw = answers.get(q["key"])
        v = 3 if raw is None else (reverse_score(raw) if q["rev"] else raw)
        buckets[q["dim"]].append(v)
    out = {}
    for d, vals in buckets.items():
        avg = np.mean(vals)
        perc = ((avg - 1) / 4.0) * 100
        out[d] = round(float(perc), 1)
    return out

def level_label(score:float):
    if score>=75: return "Muy Alto","Dominante"
    if score>=60: return "Alto","Marcado"
    if score>=40: return "Promedio","Moderado"
    if score>=25: return "Bajo","Suave"
    return "Muy Bajo","Mínimo"

def dimension_profile(d:str, score:float):
    ds = DIMENSIONES[d]
    if score>=60:
        f = ds["fort_high"]
        r = ds["risk_high"]
        rec = ["OKRs trimestrales con foco","Revisión quincenal de prioridades","Mentoría puntual por pares"]
        roles = ds["roles_high"]
        expl = "KPI alto: tu conducta típica en esta dimensión favorece el desempeño en contextos que exigen ese rasgo."
    elif score<40:
        f = ds["fort_low"]
        r = ds["risk_low"]
        rec = ds["recs_low"]
        roles = ds["roles_low"]
        expl = "KPI bajo: tu estilo tiende al extremo opuesto; es funcional en ciertos contextos y puede requerir apoyos en otros."
    else:
        f = ["Balance situacional entre ambos extremos"]
        r = ["Variabilidad según contexto; define límites y palancas"]
        rec = ["Micro-hábitos 2–3 veces/sem.","Feedback mensual con pares/líder"]
        roles = ds["roles_high"][:2] + ds["roles_low"][:1]
        expl = "KPI medio: perfil flexible; puede adaptarse con prácticas concretas según el rol."
    return f, r, rec, roles, expl

# ---------------------------------------------------------------
# Auto-avance: callback SIN rerun (marcamos bandera)
# ---------------------------------------------------------------
def on_answer_change(qkey:str):
    st.session_state.answers[qkey] = st.session_state.get(f"resp_{qkey}")
    idx = KEY2IDX[qkey]
    if idx < len(QUESTIONS)-1:
        st.session_state.q_idx = idx + 1
    else:
        st.session_state.stage = "resultados"
        st.session_state.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state._needs_rerun = True  # se ejecuta al final del ciclo

# ---------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------
def plot_radar(res:dict):
    order = list(res.keys())
    vals = [res[d] for d in order]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=[f"{DIMENSIONES[d]['code']} {d}" for d in order],
        fill='toself', name='Perfil',
        line=dict(width=2, color="#6D597A"),
        fillcolor='rgba(109, 89, 122, .12)',
        marker=dict(size=7, color="#6D597A")
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                      showlegend=False, height=520, template="plotly_white")
    return fig

def plot_bar(res:dict):
    palette = ["#81B29A","#F2CC8F","#E07A5F","#9C6644","#6D597A"]
    df = pd.DataFrame({"Dimensión":list(res.keys()),"Puntuación":list(res.values())}).sort_values("Puntuación")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Dimensión"], x=df["Puntuación"], orientation='h',
        marker=dict(color=[palette[i%len(palette)] for i in range(len(df))]),
        text=[f"{v:.1f}" for v in df["Puntuación"]], textposition="outside"
    ))
    fig.update_layout(height=520, template="plotly_white",
                      xaxis=dict(range=[0,105], title="Puntuación (0–100)"),
                      yaxis=dict(title=""))
    return fig, df

# ---------------------------------------------------------------
# Exportar (PDF si hay MPL; HTML si no)
# ---------------------------------------------------------------
def build_pdf(res:dict, fecha:str)->bytes:
    # KPI cards + barras + análisis por dimensión con pros/cons/recs + explicativo KPI.
    order = list(res.keys()); vals=[res[d] for d in order]
    avg = np.mean(vals); std = np.std(vals, ddof=1) if len(vals)>1 else 0.0
    rng = np.max(vals)-np.min(vals); top = max(res, key=res.get)

    buf = BytesIO()
    with PdfPages(buf) as pdf:
        # Portada + KPIs
        fig = plt.figure(figsize=(8.27,11.69))  # A4
        ax = fig.add_axes([0,0,1,1]); ax.axis('off')
        ax.text(.5,.94,"Informe Big Five — Contexto Laboral", ha='center', fontsize=20, fontweight='bold')
        ax.text(.5,.91,f"Fecha: {fecha}", ha='center', fontsize=11)

        # KPI Cards (dibujo con patches)
        def card(x,y,w,h,title,val):
            r = FancyBboxPatch((x,y), w,h, boxstyle="round,pad=0.012,rounding_size=0.018",
                               edgecolor="#dddddd", facecolor="#ffffff")
            ax.add_patch(r)
            ax.text(x+w*0.06, y+h*0.60, title, fontsize=10, color="#333")
            ax.text(x+w*0.06, y+h*0.25, f"{val}", fontsize=20, fontweight='bold')

        Y0 = .80; H = .10; W = .40; GAP = .02
        card(.06, Y0, W, H, "Promedio general (0–100)", f"{avg:.1f}")
        card(.54, Y0, W, H, "Desviación estándar", f"{std:.2f}")
        card(.06, Y0-(H+GAP), W, H, "Rango", f"{rng:.2f}")
        card(.54, Y0-(H+GAP), W, H, "Dimensión destacada", f"{top}")

        ax.text(.5,.58,"Puntuaciones por dimensión", ha='center', fontsize=14, fontweight='bold')
        # Listado
        ylist = .54
        for d in order:
            ax.text(.1, ylist, f"{DIMENSIONES[d]['code']} — {d}: {res[d]:.1f}", fontsize=11)
            ylist -= 0.03

        pdf.savefig(fig, bbox_inches='tight'); plt.close(fig)

        # Barras
        fig2 = plt.figure(figsize=(8.27,11.69))
        a2 = fig2.add_subplot(111)
        y = np.arange(len(order))
        a2.barh(y, [res[d] for d in order], color="#81B29A")
        a2.set_yticks(y); a2.set_yticklabels(order)
        a2.set_xlim(0,100); a2.set_xlabel("Puntuación (0–100)")
        a2.set_title("Puntuaciones por dimensión")
        for i, v in enumerate([res[d] for d in order]):
            a2.text(v+1, i, f"{v:.1f}", va='center', fontsize=9)
        pdf.savefig(fig2, bbox_inches='tight'); plt.close(fig2)

        # Análisis por dimensión (con explicativo KPI, pros, cons, recs, roles)
        for d in order:
            score = res[d]; lvl, tag = level_label(score)
            f, r, recs, roles, expl = dimension_profile(d, score)
            fig3 = plt.figure(figsize=(8.27,11.69)); ax3 = fig3.add_axes([0,0,1,1]); ax3.axis('off')
            ax3.text(.5,.95, f"{DIMENSIONES[d]['code']} — {d}", ha='center', fontsize=16, fontweight='bold')
            ax3.text(.5,.92, f"Puntuación: {score:.1f} · Nivel: {lvl} ({tag})", ha='center', fontsize=11)
            ax3.text(.08,.88,"Descripción", fontsize=13, fontweight='bold'); ax3.text(.08,.85, DIMENSIONES[d]["desc"], fontsize=11)

            ax3.text(.08,.80,"Explicativo del KPI", fontsize=13, fontweight='bold'); ax3.text(.08,.77, expl, fontsize=11)

            def draw_list(y, title, items):
                ax3.text(.08,y,title, fontsize=13, fontweight='bold')
                yy = y - .03
                for it in items:
                    ax3.text(.10, yy, f"• {it}", fontsize=11)
                    yy -= .03
                return yy -.02

            yy = .72
            yy = draw_list(yy, "Fortalezas (laborales)", f)
            yy = draw_list(yy, "Riesgos / Cosas a cuidar", r)
            yy = draw_list(yy, "Recomendaciones", recs)
            draw_list(yy, "Cargos sugeridos", roles)
            pdf.savefig(fig3, bbox_inches='tight'); plt.close(fig3)

    buf.seek(0)
    return buf.read()

def build_html(res:dict, fecha:str)->bytes:
    order = list(res.keys()); vals=[res[d] for d in order]
    avg=np.mean(vals); std=np.std(vals, ddof=1) if len(vals)>1 else 0.0; rng=np.max(vals)-np.min(vals); top=max(res,key=res.get)
    rows = ""
    for d in order:
        lvl,tag = level_label(res[d])
        rows += f"<tr><td>{DIMENSIONES[d]['code']}</td><td>{d}</td><td>{res[d]:.1f}</td><td>{lvl}</td><td>{tag}</td></tr>"
    blocks=""
    for d in order:
        score=res[d]; lvl,tag = level_label(score)
        f,r,recs,roles, expl = dimension_profile(d, score)
        blocks += f"""
<section style="border:1px solid #eee; border-radius:12px; padding:14px; margin:14px 0;">
  <h3 style="margin:.2rem 0;">{DIMENSIONES[d]['code']} — {d} <span class='tag'>{score:.1f} · {lvl} ({tag})</span></h3>
  <p style="margin:.25rem 0; color:#333;">{DIMENSIONES[d]['desc']}</p>
  <h4>Explicativo del KPI</h4>
  <p>{expl}</p>
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap:12px;">
    <div><h4>Fortalezas</h4><ul>{''.join([f'<li>{x}</li>' for x in f])}</ul></div>
    <div><h4>Riesgos</h4><ul>{''.join([f'<li>{x}</li>' for x in r])}</ul></div>
    <div><h4>Recomendaciones</h4><ul>{''.join([f'<li>{x}</li>' for x in recs])}</ul></div>
  </div>
  <h4>Cargos sugeridos</h4>
  <ul>{''.join([f'<li>{x}</li>' for x in roles])}</ul>
</section>
"""
    html=f"""<!doctype html>
<html><head><meta charset="utf-8" />
<title>Informe Big Five Laboral</title>
<style>
body{{font-family:Inter,Arial; margin:24px; color:#111;}}
h1{{font-size:24px; margin:0 0 8px 0;}}
h3{{font-size:18px; margin:.2rem 0;}}
h4{{font-size:15px; margin:.2rem 0;}}
table{{border-collapse:collapse; width:100%; margin-top:8px}}
th,td{{border:1px solid #eee; padding:8px; text-align:left;}}
.tag{{display:inline-block; padding:.2rem .6rem; border:1px solid #eee; border-radius:999px; font-size:.82rem;}}
.kpi-grid{{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:10px 0 6px 0;}}
.kpi{{border:1px solid #eee; border-radius:12px; padding:12px; background:#fff;}}
.kpi .label{{font-size:13px; opacity:.85}}
.kpi .value{{font-size:22px; font-weight:800}}
@media print{{ .no-print{{display:none}} }}
</style>
</head>
<body>
<h1>Informe Big Five — Contexto Laboral</h1>
<p>Fecha: <b>{fecha}</b></p>
<div class="kpi-grid">
  <div class="kpi"><div class="label">Promedio general (0–100)</div><div class="value">{avg:.1f}</div></div>
  <div class="kpi"><div class="label">Desviación estándar</div><div class="value">{std:.2f}</div></div>
  <div class="kpi"><div class="label">Rango</div><div class="value">{rng:.2f}</div></div>
  <div class="kpi"><div class="label">Dimensión destacada</div><div class="value">{top}</div></div>
</div>

<h3>Tabla resumen</h3>
<table>
  <thead><tr><th>Código</th><th>Dimensión</th><th>Puntuación</th><th>Nivel</th><th>Etiqueta</th></tr></thead>
  <tbody>{rows}</tbody>
</table>

<h3>Análisis por dimensión (laboral)</h3>
{blocks}

<div class="no-print" style="margin-top:16px;">
  <button onclick="window.print()" style="padding:10px 14px; border:1px solid #ddd; background:#f9f9f9; border-radius:8px; cursor:pointer;">
    Imprimir / Guardar como PDF
  </button>
</div>
</body></html>"""
    return html.encode("utf-8")

# ---------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------
def view_inicio():
    st.markdown(
        """
        <div class="card">
          <h1 style="margin:0 0 6px 0; font-size:clamp(2.2rem,3.8vw,3rem); font-weight:900;">
            🧠 Test Big Five (OCEAN) — Evaluación Laboral
          </h1>
          <p class="tag" style="margin:0;">Fondo blanco · Texto negro · Diseño profesional y responsivo</p>
        </div>
        """, unsafe_allow_html=True
    )
    c1, c2 = st.columns([1.35,1])
    with c1:
        st.markdown(
            """
            <div class="card">
              <h3 style="margin-top:0">¿Qué mide?</h3>
              <ul style="line-height:1.6">
                <li><b>O</b> Apertura a la Experiencia</li>
                <li><b>C</b> Responsabilidad</li>
                <li><b>E</b> Extraversión</li>
                <li><b>A</b> Amabilidad</li>
                <li><b>N</b> Estabilidad Emocional</li>
              </ul>
              <p class="small">50 ítems Likert (1–5) · Autoavance · Duración estimada: <b>8–12 min</b>.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            """
            <div class="card">
              <h3 style="margin-top:0">Cómo funciona</h3>
              <ol style="line-height:1.6">
                <li>Ves 1 pregunta por pantalla y eliges una opción.</li>
                <li>Al elegir, avanzas automáticamente a la siguiente.</li>
                <li>Resultados con KPIs “animados”, gráficos y análisis laboral (pros, riesgos, recomendaciones y cargos).</li>
              </ol>
            </div>
            """, unsafe_allow_html=True
        )
        # Botón sin doble click: cambiamos estado y rerun aquí mismo.
        if st.button("🚀 Iniciar evaluación", type="primary", use_container_width=True):
            st.session_state.stage = "test"
            st.session_state.q_idx = 0
            st.session_state.answers = {q["key"]:None for q in QUESTIONS}
            st.session_state.fecha = None
            st.rerun()

def view_test():
    i = st.session_state.q_idx
    q = QUESTIONS[i]
    dim = q["dim"]; code = DIMENSIONES[dim]["code"]
    # Progreso
    p = (i+1)/len(QUESTIONS)
    st.progress(p, text=f"Progreso: {i+1}/{len(QUESTIONS)}")

    # Dimensión grande y animada
    st.markdown(f"<div class='dim-title'>{code} — {dim}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='dim-desc'>{DIMENSIONES[dim]['desc']}</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {i+1}. {q['text']}")
    prev = st.session_state.answers.get(q["key"])
    prev_idx = None if prev is None else LIK_KEYS.index(prev)
    st.radio(
        "Selecciona una opción",
        options=LIK_KEYS,
        index=prev_idx,
        format_func=lambda x: LIKERT[x],
        key=f"resp_{q['key']}",
        horizontal=True,
        label_visibility="collapsed",
        on_change=on_answer_change,
        args=(q["key"],),
    )
    st.markdown("</div>", unsafe_allow_html=True)

def view_resultados():
    res = compute_scores(st.session_state.answers)
    order = list(res.keys()); vals=[res[d] for d in order]
    avg = round(float(np.mean(vals)),1)
    std = round(float(np.std(vals, ddof=1)),2) if len(vals)>1 else 0.0
    rng = round(float(np.max(vals)-np.min(vals)),2)
    top = max(res, key=res.get)

    # Encabezado
    st.markdown(
        f"""
        <div class="card">
          <h1 style="margin:0 0 6px 0; font-size:clamp(2.2rem,3.8vw,3rem); font-weight:900;">📊 Informe Big Five — Resultados Laborales</h1>
          <p class="small" style="margin:0;">Fecha: <b>{st.session_state.fecha}</b></p>
        </div>
        """, unsafe_allow_html=True
    )

    # KPIs con “micro animación” visual (CSS)
    st.markdown("<div class='kpi-grid'>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi'><div class='label'>Promedio general (0–100)</div><div class='value countup' data-target='{avg:.1f}'>{avg:.1f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi'><div class='label'>Desviación estándar</div><div class='value countup' data-target='{std:.2f}'>{std:.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi'><div class='label'>Rango</div><div class='value countup' data-target='{rng:.2f}'>{rng:.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi'><div class='label'>Dimensión destacada</div><div class='value'>{top}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Radar del perfil")
        st.plotly_chart(plot_radar(res), use_container_width=True)
    with c2:
        st.subheader("📊 Puntuaciones por dimensión")
        fig_bar, df_sorted = plot_bar(res)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Resumen de resultados")
    tabla = pd.DataFrame({
        "Código":[DIMENSIONES[d]["code"] for d in order],
        "Dimensión":order,
        "Puntuación":[f"{res[d]:.1f}" for d in order],
        "Nivel":[level_label(res[d])[0] for d in order],
        "Etiqueta":[level_label(res[d])[1] for d in order],
    })
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔍 Análisis por dimensión (laboral)")
    for d in DIM_LIST:
        score = res[d]; lvl, tag = level_label(score)
        fort, risk, recs, roles, expl = dimension_profile(d, score)
        with st.expander(f"{DIMENSIONES[d]['code']} — {d}: {score:.1f} ({lvl})", expanded=True):
            cc1, cc2 = st.columns([1,2])
            with cc1:
                st.markdown("**Indicador (0–100)**")
                st.markdown(f"<div class='card'><div class='value'>{score:.1f}</div><div class='label'>{lvl} · {tag}</div></div>", unsafe_allow_html=True)
                st.markdown("**Cargos sugeridos**")
                st.markdown("<ul>"+ "".join([f"<li>{x}</li>" for x in roles]) +"</ul>", unsafe_allow_html=True)
            with cc2:
                st.markdown("**Descripción**")
                st.markdown(DIMENSIONES[d]["desc"])
                st.markdown("**Explicativo del KPI**")
                st.markdown(expl)
                cL, cR = st.columns(2)
                with cL:
                    st.markdown("**Fortalezas (laborales)**")
                    st.markdown("<ul>"+ "".join([f"<li>{x}</li>" for x in fort]) +"</ul>", unsafe_allow_html=True)
                with cR:
                    st.markdown("**Riesgos / Cosas a cuidar**")
                    st.markdown("<ul>"+ "".join([f"<li>{x}</li>" for x in risk]) +"</ul>", unsafe_allow_html=True)
                st.markdown("**Recomendaciones**")
                st.markdown("<ul>"+ "".join([f"<li>{x}</li>" for x in recs]) +"</ul>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📥 Exportar informe")

    # Generamos bytes inmediatamente (sin “preparar”), así el botón funciona 1 click
    if HAS_MPL:
        pdf_bytes = build_pdf(res, st.session_state.fecha)
        st.download_button(
            "⬇️ Descargar PDF (servidor)",
            data=pdf_bytes,
            file_name="Informe_BigFive_Laboral.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        html_bytes = build_html(res, st.session_state.fecha)
        st.download_button(
            "⬇️ Descargar Reporte (HTML) — Imprime como PDF",
            data=html_bytes,
            file_name="Informe_BigFive_Laboral.html",
            mime="text/html",
            use_container_width=True
        )
        st.caption("Abre el HTML y usa “Imprimir → Guardar como PDF”. (Si instalas matplotlib obtendrás PDF directo.)")

    st.markdown("---")
    if st.button("🔄 Nueva evaluación", type="primary", use_container_width=True):
        st.session_state.stage = "inicio"
        st.session_state.q_idx = 0
        st.session_state.answers = {q["key"]:None for q in QUESTIONS}
        st.session_state.fecha = None
        st.rerun()

# ---------------------------------------------------------------
# FLUJO PRINCIPAL
# ---------------------------------------------------------------
if st.session_state.stage == "inicio":
    view_inicio()
elif st.session_state.stage == "test":
    view_test()
else:
    view_resultados()

# Si el callback de la radio marcó bandera de rerun, lo hacemos aquí (1 sola vez)
if st.session_state._needs_rerun:
    st.session_state._needs_rerun = False
    st.rerun()
