import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
import random
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(
    layout="wide", 
    page_title="Test Big Five (OCEAN) | Evaluación Profesional",
    page_icon="🧠"
)

# Ancla para scroll
st.html('<a id="top-anchor"></a>')

# Definición de las dimensiones del Big Five
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O", 
        "color": "#0077b6", 
        "icon": "💡", 
        "desc": "Imaginación, curiosidad intelectual, creatividad y aprecio por el arte y las nuevas experiencias.",
        "caracteristicas_altas": "Creativo, curioso, aventurero, con mente abierta",
        "caracteristicas_bajas": "Práctico, convencional, prefiere lo familiar"
    },
    "Responsabilidad": {
        "code": "C", 
        "color": "#00b4d8", 
        "icon": "🎯", 
        "desc": "Autodisciplina, organización, cumplimiento de objetivos y sentido del deber.",
        "caracteristicas_altas": "Organizado, confiable, disciplinado, planificado",
        "caracteristicas_bajas": "Flexible, espontáneo, despreocupado"
    },
    "Extraversión": {
        "code": "E", 
        "color": "#48cae4", 
        "icon": "🗣️", 
        "desc": "Sociabilidad, asertividad, energía y búsqueda de estimulación en compañía de otros.",
        "caracteristicas_altas": "Sociable, hablador, asertivo, enérgico",
        "caracteristicas_bajas": "Reservado, tranquilo, independiente, reflexivo"
    },
    "Amabilidad": {
        "code": "A", 
        "color": "#90e0ef", 
        "icon": "🤝", 
        "desc": "Cooperación, empatía, compasión, confianza y respeto por los demás.",
        "caracteristicas_altas": "Compasivo, cooperativo, confiado, altruista",
        "caracteristicas_bajas": "Competitivo, escéptico, directo, objetivo"
    },
    "Estabilidad Emocional": { 
        "code": "N", 
        "color": "#0096c7", 
        "icon": "🧘", 
        "desc": "Capacidad para mantener la calma y gestionar el estrés. (Opuesto a Neuroticismo)",
        "caracteristicas_altas": "Estable, calmado, resiliente, seguro",
        "caracteristicas_bajas": "Sensible, ansioso, reactivo emocionalmente"
    },
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

# Escala Likert
ESCALA_LIKERT = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}
LIKERT_OPTIONS = list(ESCALA_LIKERT.keys())

def reverse_score(score):
    """Invierte el puntaje para preguntas inversas."""
    if isinstance(score, (int, float)):
        return 6 - score
    return 3 # Fallback

# 50 Preguntas del Big Five (10 por dimensión)
PREGUNTAS = [
    # Apertura a la Experiencia (O)
    {"text": "Tengo una imaginación muy activa", "dim": "Apertura a la Experiencia", "key": "O1", "reverse": False},
    {"text": "Me gustan los retos intelectuales complejos", "dim": "Apertura a la Experiencia", "key": "O2", "reverse": False},
    {"text": "Disfruto visitando museos y galerías de arte", "dim": "Apertura a la Experiencia", "key": "O3", "reverse": False},
    {"text": "Me gusta experimentar con nuevas ideas", "dim": "Apertura a la Experiencia", "key": "O4", "reverse": False},
    {"text": "Valoro la creatividad y la originalidad", "dim": "Apertura a la Experiencia", "key": "O5", "reverse": False},
    {"text": "Prefiero la rutina a probar cosas nuevas", "dim": "Apertura a la Experiencia", "key": "O6", "reverse": True},
    {"text": "No me interesan las discusiones filosóficas", "dim": "Apertura a la Experiencia", "key": "O7", "reverse": True},
    {"text": "Rara vez reflexiono sobre temas abstractos", "dim": "Apertura a la Experiencia", "key": "O8", "reverse": True},
    {"text": "Prefiero lo convencional a lo original", "dim": "Apertura a la Experiencia", "key": "O9", "reverse": True},
    {"text": "No me gusta cambiar mis hábitos establecidos", "dim": "Apertura a la Experiencia", "key": "O10", "reverse": True},

    # Responsabilidad (C)
    {"text": "Siempre estoy bien preparado", "dim": "Responsabilidad", "key": "C1", "reverse": False},
    {"text": "Presto atención a los detalles", "dim": "Responsabilidad", "key": "C2", "reverse": False},
    {"text": "Cumplo con mis compromisos y plazos", "dim": "Responsabilidad", "key": "C3", "reverse": False},
    {"text": "Sigo un horario y una planificación", "dim": "Responsabilidad", "key": "C4", "reverse": False},
    {"text": "Me esfuerzo por la excelencia en mi trabajo", "dim": "Responsabilidad", "key": "C5", "reverse": False},
    {"text": "Dejo las cosas desordenadas", "dim": "Responsabilidad", "key": "C6", "reverse": True},
    {"text": "Evito mis responsabilidades", "dim": "Responsabilidad", "key": "C7", "reverse": True},
    {"text": "Me distraigo fácilmente", "dim": "Responsabilidad", "key": "C8", "reverse": True},
    {"text": "A menudo olvido poner las cosas en su lugar", "dim": "Responsabilidad", "key": "C9", "reverse": True},
    {"text": "Tiendo a procrastinar tareas importantes", "dim": "Responsabilidad", "key": "C10", "reverse": True},

    # Extraversión (E)
    {"text": "Soy el alma de la fiesta", "dim": "Extraversión", "key": "E1", "reverse": False},
    {"text": "Me siento cómodo con desconocidos", "dim": "Extraversión", "key": "E2", "reverse": False},
    {"text": "Busco activamente la compañía de otros", "dim": "Extraversión", "key": "E3", "reverse": False},
    {"text": "Hablo mucho en reuniones sociales", "dim": "Extraversión", "key": "E4", "reverse": False},
    {"text": "Me gusta llamar la atención", "dim": "Extraversión", "key": "E5", "reverse": False},
    {"text": "Prefiero estar solo que rodeado de gente", "dim": "Extraversión", "key": "E6", "reverse": True},
    {"text": "Soy una persona reservada y callada", "dim": "Extraversión", "key": "E7", "reverse": True},
    {"text": "Me cuesta expresarme en grupos grandes", "dim": "Extraversión", "key": "E8", "reverse": True},
    {"text": "Prefiero trabajar en segundo plano", "dim": "Extraversión", "key": "E9", "reverse": True},
    {"text": "Me agotan las interacciones sociales prolongadas", "dim": "Extraversión", "key": "E10", "reverse": True},

    # Amabilidad (A)
    {"text": "Simpatizo fácilmente con otros", "dim": "Amabilidad", "key": "A1", "reverse": False},
    {"text": "Me preocupo por el bienestar de los demás", "dim": "Amabilidad", "key": "A2", "reverse": False},
    {"text": "Trato a todos con respeto", "dim": "Amabilidad", "key": "A3", "reverse": False},
    {"text": "Ayudo a otros sin esperar nada a cambio", "dim": "Amabilidad", "key": "A4", "reverse": False},
    {"text": "Confío en las buenas intenciones de la gente", "dim": "Amabilidad", "key": "A5", "reverse": False},
    {"text": "No me interesa realmente la gente", "dim": "Amabilidad", "key": "A6", "reverse": True},
    {"text": "Soy cínico sobre las intenciones ajenas", "dim": "Amabilidad", "key": "A7", "reverse": True},
    {"text": "Puedo ser bastante insensible", "dim": "Amabilidad", "key": "A8", "reverse": True},
    {"text": "Pienso primero en mí mismo", "dim": "Amabilidad", "key": "A9", "reverse": True},
    {"text": "No me conmueven los problemas de otros", "dim": "Amabilidad", "key": "A10", "reverse": True},

    # Estabilidad Emocional (N invertido)
    {"text": "Mantengo la calma bajo presión", "dim": "Estabilidad Emocional", "key": "N1", "reverse": False},
    {"text": "Rara vez me siento ansioso o estresado", "dim": "Estabilidad Emocional", "key": "N2", "reverse": False},
    {"text": "Soy emocionalmente estable", "dim": "Estabilidad Emocional", "key": "N3", "reverse": False},
    {"text": "Me recupero rápidamente de contratiempos", "dim": "Estabilidad Emocional", "key": "N4", "reverse": False},
    {"text": "Me siento seguro de mí mismo", "dim": "Estabilidad Emocional", "key": "N5", "reverse": False},
    {"text": "Me preocupo mucho por las cosas", "dim": "Estabilidad Emocional", "key": "N6", "reverse": True},
    {"text": "Me irrito fácilmente", "dim": "Estabilidad Emocional", "key": "N7", "reverse": True},
    {"text": "A menudo me siento triste o deprimido", "dim": "Estabilidad Emocional", "key": "N8", "reverse": True},
    {"text": "Tengo cambios de humor frecuentes", "dim": "Estabilidad Emocional", "key": "N9", "reverse": True},
    {"text": "Me siento abrumado por el estrés", "dim": "Estabilidad Emocional", "key": "N10", "reverse": True},
]

# Inicialización de Session State
if 'stage' not in st.session_state:
    st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'current_dimension_index' not in st.session_state:
    st.session_state.current_dimension_index = 0
if 'should_scroll' not in st.session_state:
    st.session_state.should_scroll = False 
if 'fecha_evaluacion' not in st.session_state:
    st.session_state.fecha_evaluacion = None

# --- 2. FUNCIONES DE SCROLL ---
def forzar_scroll_al_top():
    """Fuerza el scroll al inicio usando JS y el ancla 'top-anchor'."""
    js_code = """
        <script>
            setTimeout(function() {
                var topAnchor = window.parent.document.getElementById('top-anchor');
                if (topAnchor) {
                    topAnchor.scrollIntoView({ behavior: 'auto', block: 'start' });
                } else {
                    window.parent.scrollTo({ top: 0, behavior: 'auto' });
                    var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                    if (mainContent) {
                        mainContent.scrollTo({ top: 0, behavior: 'auto' });
                    }
                }
            }, 150); 
        </script>
    """
    components.html(js_code, height=0, scrolling=False, key="scroll_component_static")

# --- 3. FUNCIONES DE CÁLCULO Y LÓGICA ---
def calcular_resultados(respuestas):
    """Calcula las puntuaciones de las 5 dimensiones (0-100)."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}

    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'])

        if isinstance(respuesta, (int, float)):
             if p['reverse']:
                 score = reverse_score(respuesta)
             else:
                 score = respuesta
        else:
            score = 3 

        scores[p['dim']].append(score)

    resultados = {}
    for dim, score_list in scores.items():
        if score_list: 
             avg_score = np.mean(score_list)
             percent_score = ((avg_score - 1) / 4) * 100
             resultados[dim] = round(percent_score, 1) 
        else:
             resultados[dim] = 50.0 

    return resultados

def get_nivel_interpretacion(score):
    """Clasifica el puntaje y retorna nivel, color y etiqueta."""
    if score is None: return "N/A", "#808080", "Indeterminado"
    if score >= 75: return "Muy Alto", "#2a9d8f", "Dominante"
    elif score >= 60: return "Alto", "#264653", "Marcado"
    elif score >= 40: return "Promedio", "#e9c46a", "Moderado"
    elif score >= 25: return "Bajo", "#f4a261", "Suave"
    else: return "Muy Bajo", "#e76f51", "Mínimo" 

def get_recomendaciones_detalladas(dim, score):
    """Genera recomendaciones profesionales detalladas, indicando aptitud."""
    nivel_map, _, _ = get_nivel_interpretacion(score)

    rec_db = {
        "Apertura a la Experiencia": {
            "Muy Alto": "**Roles Idóneos:** Innovación, I+D, Diseño Estratégico, Artista, Investigador. **Fortalezas:** Curiosidad, creatividad, adaptabilidad.",
            "Alto": "**Roles Idóneos:** Marketing Creativo, Consultoría, Desarrollo de Nuevos Productos. **Fortalezas:** Abierto a nuevas ideas, pensamiento flexible.",
            "Promedio": "**Aptitud General:** Bueno para roles que equilibran rutina y novedad. Puede participar en mejora continua.",
            "Bajo": "**Roles Idóneos:** Tareas Rutinarias, Control de Calidad, Administración. **Precaución:** Requiere apoyo para manejar cambios.",
            "Muy Bajo": "**Roles No Idóneos:** Innovación Disruptiva, Estratega. **Aptitud:** Prefiere entornos predecibles."
        },
        "Responsabilidad": {
            "Muy Alto": "**Roles Idóneos:** Gerencia de Proyectos, Auditoría, Contraloría, Finanzas. **Fortalezas:** Organización, disciplina, fiabilidad.",
            "Alto": "**Roles Idóneos:** Planificación Financiera, Logística, Ingeniería de Procesos. **Fortalezas:** Cumplimiento de plazos, detalle.",
            "Promedio": "**Aptitud General:** Mantiene disciplina en roles definidos. Mejorar con herramientas de gestión.",
            "Bajo": "**Roles Idóneos:** Roles Flexibles, Ventas Creativas (con supervisión). **Precaución:** Necesita seguimiento estructurado.",
            "Muy Bajo": "**Roles No Idóneos:** Auditoría, Gestión Crítica. **Aptitud:** Funciona mejor en entornos menos estructurados."
        },
        "Extraversión": {
            "Muy Alto": "**Roles Idóneos:** Dirección Comercial, Liderazgo, Relaciones Públicas, Ventas. **Fortalezas:** Sociabilidad, asertividad, energía.",
            "Alto": "**Roles Idóneos:** Jefe de Equipo, Capacitador, Eventos. **Fortalezas:** Buena comunicación, disfruta interacción.",
            "Promedio": "**Aptitud General:** Adaptable. Funciona bien en equipo y solo.",
            "Bajo": "**Roles Idóneos:** Analista, Programador, Escritor Técnico, Investigador. **Precaución:** Puede agotarse en roles de alta interacción.",
            "Muy Bajo": "**Roles No Idóneos:** Ventas de Campo, PR. **Aptitud:** Prefiere trabajo individual y entornos tranquilos."
        },
        "Amabilidad": {
            "Muy Alto": "**Roles Idóneos:** Gerencia de RR.HH., Servicio al Cliente, Mediador, Terapeuta. **Fortalezas:** Empatía, cooperación.",
            "Alto": "**Roles Idóneos:** Trabajo Social, Enfermería, Consultor Interno. **Fortalezas:** Colaborador, considerado.",
            "Promedio": "**Aptitud General:** Buen colaborador. Fomentar liderazgo servicial.",
            "Bajo": "**Roles Idóneos:** Negociador, Analista Crítico, Abogado Litigante. **Precaución:** Puede generar conflictos.",
            "Muy Bajo": "**Roles No Idóneos:** Soporte al Cliente, RR.HH. **Aptitud:** Toma de decisiones objetiva, competitivo."
        },
        "Estabilidad Emocional": {
            "Muy Alto": "**Roles Idóneos:** Gestión de Crisis, Operaciones de Alto Estrés, Liderazgo Ejecutivo. **Fortalezas:** Resiliencia, calma bajo presión.",
            "Alto": "**Roles Idóneos:** Cirujano, Piloto, Bombero. **Fortalezas:** Manejo efectivo del estrés.",
            "Promedio": "**Aptitud General:** Gestión emocional adecuada. Ofrecer talleres de estrés.",
            "Bajo": "**Roles Idóneos (con apoyo):** Roles Creativos, Terapeuta. **Precaución:** Sensible al estrés.",
            "Muy Bajo": "**Roles No Idóneos:** Operaciones de Crisis. **Precaución:** Requiere ambiente de baja presión y soporte."
        },
    }

    return rec_db.get(dim, {}).get(nivel_map, "Analizar fortalezas y debilidades para la ruta profesional.")

def get_roles_no_recomendados(resultados):
    """Determina roles no recomendados basándose en puntajes extremos (resumen)."""
    no_aptos = set()
    UMBRAL_BAJO = 25
    UMBRAL_ALTO = 75

    if resultados.get("Estabilidad Emocional", 50) < UMBRAL_BAJO: 
        no_aptos.add("Operaciones de Crisis/Alto Estrés (Baja Estabilidad Emocional <25)")
    if resultados.get("Responsabilidad", 50) < UMBRAL_BAJO:
        no_aptos.add("Auditoría/Gestión Crítica (Responsabilidad <25)")
    if resultados.get("Amabilidad", 50) < UMBRAL_BAJO:
        no_aptos.add("RR.HH./Soporte al Cliente (Amabilidad <25)")
    if resultados.get("Apertura a la Experiencia", 50) < UMBRAL_BAJO:
        no_aptos.add("I+D/Innovación Disruptiva (Apertura <25)")
    if resultados.get("Extraversión", 50) < UMBRAL_BAJO:
        no_aptos.add("Ventas Campo/Relaciones Públicas (Extraversión <25)")

    if not no_aptos:
        return None
    return " | ".join(sorted(list(no_aptos)))

# --- 4. FUNCIONES DE GRÁFICOS ---
def crear_grafico_radar(resultados):
    """Crea gráfico de radar del perfil."""
    if resultados is None: return go.Figure()

    categories = [DIMENSIONES[dim]['code'] + ' - ' + dim.split(' ')[0] for dim in resultados.keys()] 
    values = list(resultados.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Tu Perfil',
        line=dict(color='#0077b6', width=3),
        fillcolor='rgba(0, 119, 182, 0.25)',
        marker=dict(size=10, color='#00b4d8')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
                linecolor="#cccccc"
            ),
            angularaxis=dict(
                linecolor="#cccccc"
            ),
        ),
        showlegend=False,
        height=600,
        title=dict(
            text="Perfil de Personalidad Big Five (OCEAN)",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#333')
        ),
        template="plotly_white"
    )
    fig.update_traces(hovertemplate='<b>%{theta}</b><br>Puntuación: %{r:.1f}<extra></extra>')

    return fig

def crear_grafico_barras(resultados):
    """Crea gráfico de barras horizontales."""
    if resultados is None: return go.Figure()

    df = pd.DataFrame({
        'Dimensión': list(resultados.keys()),
        'Puntuación': list(resultados.values())
    })
    df = df.sort_values('Puntuación', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['Dimensión'],
        x=df['Puntuación'],
        orientation='h',
        marker=dict(
            color=df['Puntuación'],
            colorscale='RdYlGn', 
            cmin=0, cmax=100, 
            colorbar=dict(title="Puntuación", x=1.05) 
        ),
        text=df['Puntuación'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Puntuación: %{x:.1f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Puntuaciones por Dimensión", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Puntuación (0-100)", range=[0, 110]), 
        yaxis=dict(title="", tickfont=dict(size=10)), 
        height=400, 
        margin=dict(l=200, r=50, t=50, b=50), 
        template="plotly_white"
    )

    return fig

def crear_grafico_comparativo(resultados):
    """Crea gráfico comparativo con la población promedio."""
    if resultados is None: return go.Figure()

    dimensiones = list(resultados.keys())
    tu_perfil = list(resultados.values())
    promedio = [50] * len(dimensiones)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Tu Perfil',
        x=dimensiones,
        y=tu_perfil,
        marker=dict(color='#0077b6'),
        text=[f"{v:.1f}" for v in tu_perfil],
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        name='Promedio Poblacional',
        x=dimensiones,
        y=promedio,
        marker=dict(color='#95a5a6'),
        text=['50.0'] * len(dimensiones),
        textposition='outside'
    ))

    fig.update_layout(
        title=dict(text="Tu Perfil vs Promedio Poblacional", x=0.5, xanchor='center', font=dict(size=18)),
        yaxis=dict(title="Puntuación (0-100)", range=[0, 115]), 
        xaxis=dict(title="", tickangle=-45), 
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white"
    )

    return fig


# --- 5. FUNCIONES DE NAVEGACIÓN Y FLUJO ---
def iniciar_test():
    """Inicia el test."""
    st.session_state.stage = 'test_activo'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None
    st.session_state.should_scroll = True 
    st.rerun()

def completar_al_azar():
    """Genera respuestas aleatorias y va a resultados."""
    st.session_state.respuestas = {p['key']: random.choice(LIKERT_OPTIONS) for p in PREGUNTAS}
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.stage = 'resultados'
    st.session_state.should_scroll = True 
    st.rerun()

def reiniciar_test():
    """Reinicia el test."""
    st.session_state.stage = 'inicio'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None
    st.session_state.should_scroll = True 
    st.rerun()

def avanzar_dimension():
    """Avanza al siguiente índice de dimensión."""
    if st.session_state.current_dimension_index < len(DIMENSIONES_LIST) - 1:
        st.session_state.current_dimension_index += 1
        st.session_state.should_scroll = True 
        st.rerun()
    else:
        procesar_y_mostrar_resultados()

def procesar_y_mostrar_resultados():
    """Calcula resultados, guarda fecha y cambia a stage 'resultados'."""
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.stage = 'resultados'
    st.session_state.should_scroll = True 
    st.rerun()

# --- 6. VISTAS ---
def vista_inicio():
    """Vista de inicio."""
    st.title("🧠 Test de Personalidad Big Five (OCEAN)")
    st.markdown("### Evaluación Profesional de los Cinco Grandes Factores de Personalidad")

    st.info("""
    El modelo Big Five (también conocido como OCEAN) es el marco más respaldado científicamente para
    comprender la personalidad humana. Mide cinco dimensiones fundamentales que predicen
    comportamientos en múltiples contextos.
    """)

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Información del Test")
        st.markdown("""
        - **Duración:** 10-15 minutos
        - **Preguntas:** 50 ítems (10 por dimensión)
        - **Escala:** Likert de 5 puntos
        - **Dimensiones evaluadas:**
          - 💡 **O**penness (Apertura a la Experiencia)
          - 🎯 **C**onscientiousness (Responsabilidad)
          - 🗣️ **E**xtraversion (Extraversión)
          - 🤝 **A**greeableness (Amabilidad)
          - 🧘 **N**euroticism (Estabilidad Emocional*)

        _*En este test medimos Estabilidad Emocional (opuesto a Neuroticismo)_
        """)

    with col2:
        st.subheader("🚀 Comenzar")

        if st.button("📝 Iniciar Test", type="primary", use_container_width=True):
            iniciar_test() 

        st.markdown("---")

        st.caption("**Modo Demo:**")
        if st.button("🎲 Completar Aleatoriamente", type="secondary", use_container_width=True):
            completar_al_azar() 

def vista_test_activo():
    """Vista del test activo."""
    current_index = st.session_state.current_dimension_index
    current_dim_name = DIMENSIONES_LIST[current_index]
    dim_info = DIMENSIONES[current_dim_name]

    st.title(f"{dim_info['icon']} Dimensión {current_index + 1} de {len(DIMENSIONES_LIST)}: {current_dim_name}")
    st.markdown(f"**{dim_info['desc']}**")

    # Progreso general
    total_respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None)
    total_preguntas = len(PREGUNTAS)
    progreso = total_respondidas / total_preguntas

    st.progress(progreso, text=f"Progreso: {total_respondidas}/{total_preguntas} preguntas ({progreso*100:.0f}%)")
    st.markdown("---")

    preguntas_dimension = [p for p in PREGUNTAS if p['dim'] == current_dim_name]

    with st.form(f"form_dim_{current_index}"):
        st.subheader(f"Responde a las siguientes 10 afirmaciones:")

        respuestas_form_actual = {}
        all_questions_in_form_answered = True 

        for i, p in enumerate(preguntas_dimension, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {p['text']}**")

                initial_value = st.session_state.respuestas.get(p['key'])
                initial_index = LIKERT_OPTIONS.index(initial_value) if initial_value is not None else None

                widget_key = f"radio_{p['key']}" 
                respuestas_form_actual[p['key']] = st.radio(
                    label=f"Selecciona tu respuesta para: {p['text'][:30]}...",
                    options=LIKERT_OPTIONS,
                    format_func=lambda x: ESCALA_LIKERT[x],
                    index=initial_index,
                    key=widget_key,
                    horizontal=True,
                    label_visibility="collapsed"
                )
                if respuestas_form_actual[p['key']] is None:
                    all_questions_in_form_answered = False


        st.markdown("---")

        if current_index == len(DIMENSIONES_LIST) - 1:
            button_label = "✅ Finalizar y Ver Resultados"
        else:
            next_dim = DIMENSIONES_LIST[current_index + 1]
            button_label = f"➡️ Continuar a: {next_dim}"

        submitted = st.form_submit_button(button_label, type="primary", use_container_width=True)

        if submitted:
            validation_passed = True
            for q_key in [q['key'] for q in preguntas_dimension]:
                if respuestas_form_actual.get(q_key) is None:
                     validation_passed = False
                     break

            if not validation_passed:
                st.error(f"⚠️ Por favor, responde todas las preguntas de esta dimensión ({current_dim_name}) antes de continuar.")
            else:
                st.session_state.respuestas.update(respuestas_form_actual)
                avanzar_dimension()


def vista_resultados():
    """Vista de resultados profesional."""
    resultados = st.session_state.resultados

    if resultados is None:
        st.warning("No hay resultados disponibles. Por favor, completa el test.")
        if st.button("Volver al Inicio"):
            reiniciar_test()
        return

    st.title("📊 Tu Informe de Personalidad Big Five")
    fecha_eval = st.session_state.get('fecha_evaluacion', "Fecha no registrada")
    st.markdown(f"**Fecha de Evaluación:** {fecha_eval}")
    st.markdown("---")

    # --- 1. RESUMEN EJECUTIVO ---
    st.header("1. 📈 Resumen Ejecutivo")

    promedio_total = np.mean(list(resultados.values()))

    st.metric(label="Puntuación Promedio General", value=f"{promedio_total:.1f}/100", delta="Perfil Equilibrado")

    st.markdown("---")

    # --- 2. VISUALIZACIONES ---
    st.header("2. 📊 Visualización de tu Perfil")

    tab1, tab2, tab3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])

    with tab1:
        fig_radar = crear_grafico_radar(resultados)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("Gráfico de radar mostrando tu perfil en las 5 dimensiones.")

    with tab2:
        fig_barras = crear_grafico_barras(resultados)
        st.plotly_chart(fig_barras, use_container_width=True)
        st.caption("Puntuaciones ordenadas de menor a mayor.")

    with tab3:
        fig_comp = crear_grafico_comparativo(resultados)
        st.plotly_chart(fig_comp, use_container_width=True)
        st.caption("Comparación de tu perfil con el promedio poblacional (50 puntos).")

    st.markdown("---")

    # --- 3. ANÁLISIS DETALLADO ---
    st.header("3. 🔍 Análisis Detallado por Dimensión")

    for dim_name in DIMENSIONES_LIST:
        score = resultados.get(dim_name, 50) 
        dim_info = DIMENSIONES[dim_name]
        nivel, color, etiqueta = get_nivel_interpretacion(score)

        with st.expander(f"{dim_info['icon']} **{dim_name}**: {score:.1f} puntos ({nivel})", expanded=True):
            col1, col2 = st.columns([1, 2])

            with col1:
                # Medidor circular
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"{dim_info['code']}", 'font': {'size': 20}}, 
                    number={'font': {'size': 36}}, 
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1},
                        'bar': {'color': dim_info['color']},
                        'steps': [
                            {'range': [0, 25], 'color': '#f8d7da'},
                            {'range': [25, 40], 'color': '#fff3cd'},
                            {'range': [40, 60], 'color': '#d1ecf1'},
                            {'range': [60, 75], 'color': '#d4edda'},
                            {'range': [75, 100], 'color': '#c3e6cb'}
                        ],
                        'threshold': {
                             'line': {'color': "black", 'width': 3}, 
                             'thickness': 0.9, 
                             'value': score
                        } 
                    }
                ))
                fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10)) 
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col2:
                st.markdown(f"**Descripción:**")
                st.markdown(dim_info['desc'])

                st.markdown(f"**Nivel:** <span style='color:{color}; font-weight: bold; font-size: 1.1em;'>{nivel} ({etiqueta})</span>", unsafe_allow_html=True)

                if score >= 60:
                    st.success(f"✅ **Puntuación Alta/Muy Alta**")
                    st.markdown(f"**Características Típicas:** {dim_info['caracteristicas_altas']}")
                elif score <= 40:
                    st.warning(f"⚠️ **Puntuación Baja/Muy Baja**")
                    st.markdown(f"**Características Típicas:** {dim_info['caracteristicas_bajas']}")
                else: 
                    st.info(f"ℹ️ **Puntuación Media**")
                    st.markdown("Equilibrio entre las características altas y bajas.")

            st.markdown("---", help="Separador visual") 

            st.markdown("**💼 Implicaciones y Aptitud Profesional:**")
            recomendacion_profesional = get_recomendaciones_detalladas(dim_name, score)
            st.markdown(f" {recomendacion_profesional}") 

    st.markdown("---")

    # --- 4. FORTALEZAS Y ÁREAS DE DESARROLLO ---
    st.header("4. 💪 Fortalezas y Áreas de Desarrollo")

    col_fort, col_des = st.columns(2)

    sorted_dims = sorted(resultados.items(), key=lambda item: item[1], reverse=True)
    top_3 = sorted_dims[:3]
    bottom_scores = sorted(resultados.items(), key=lambda item: item[1])
    areas_desarrollo = [item for item in bottom_scores if item[1] < 40]
    if len(areas_desarrollo) < 3:
         needed = 3 - len(areas_desarrollo)
         additional = [item for item in bottom_scores if item[1] >= 40][:needed]
         areas_desarrollo.extend(additional)

    with col_fort:
        st.subheader("🌟 Tus 3 Principales Fortalezas")
        if not top_3:
             st.write("No se pudieron determinar las fortalezas.")
        else:
             for i, (dim, score) in enumerate(top_3, 1):
                 icon = DIMENSIONES[dim]['icon']
                 st.markdown(f"""
                 **{i}. {icon} {dim}**
                 - Puntuación: **{score:.1f}**/100
                 - {DIMENSIONES[dim]['caracteristicas_altas']}
                 """)
                 st.progress(score / 100) 
                 st.markdown("") 

    with col_des:
        st.subheader("📈 Áreas Potenciales de Desarrollo")
        if not areas_desarrollo:
             st.write("No se identificaron áreas críticas de desarrollo (puntuaciones >= 40).")
        else:
             for i, (dim, score) in enumerate(areas_desarrollo, 1):
                 icon = DIMENSIONES[dim]['icon']
                 nivel, _, _ = get_nivel_interpretacion(score)
                 if score < 40:
                     st.markdown(f"""
                     **{i}. {icon} {dim}**
                     - Puntuación: **{score:.1f}**/100 (<span style='color:#e76f51;'>{nivel}</span>)
                     - **Foco Sugerido:** Considerar desarrollo si es relevante para objetivos.
                     """, unsafe_allow_html=True)
                 else:
                     st.markdown(f"""
                     **{i}. {icon} {dim}**
                     - Puntuación: **{score:.1f}**/100 ({nivel})
                     - Nivel Adecuado.
                     """, unsafe_allow_html=True)
                 st.progress(score / 100)
                 st.markdown("")

    st.markdown("---")

    # --- 5. Roles No Recomendados ---
    st.header("5. 🛑 Alerta de Incompatibilidad con Roles Clave")

    roles_no_aptos = get_roles_no_recomendados(resultados)

    if roles_no_aptos is None:
        st.success("✅ **Perfil Versátil:** No se identificaron incompatibilidades significativas para roles críticos basadas en puntuaciones extremas.")
    else:
        st.error(f"**Cargos NO Recomendados o de Alto Riesgo (Puntuación Extrema):** {roles_no_aptos}")
        st.caption("Esta lista se basa en puntuaciones extremas (<25 o >75). Considere esto al evaluar el ajuste para estos roles específicos.")

    st.markdown("---")


    # --- 6. TABLA DE RESULTADOS ---
    st.header("6. 📋 Tabla Resumen de Resultados")

    df_resultados = pd.DataFrame({
        'Dimensión': [dim for dim in resultados.keys()],
        'Código': [DIMENSIONES[dim]['code'] for dim in resultados.keys()],
        'Puntuación': [f"{score:.1f}" for score in resultados.values()],
        'Nivel': [get_nivel_interpretacion(score)[0] for score in resultados.values()],
        'Etiqueta': [get_nivel_interpretacion(score)[2] for score in resultados.values()]
    })

    def color_nivel_tabla(val):
        try:
            score = float(val)
            if score >= 75: return 'background-color: #c3e6cb; color: #155724; font-weight: bold;'
            elif score >= 60: return 'background-color: #d4edda; color: #155724;'
            elif score >= 40: return 'background-color: #d1ecf1; color: #0c5460;'
            elif score >= 25: return 'background-color: #fff3cd; color: #856404;'
            else: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        except: return ''

    styled_df = df_resultados.style.applymap(color_nivel_tabla, subset=['Puntuación'])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- 7. EXPORTAR Y ACCIONES ---
    st.header("7. 📥 Exportar y Acciones")

    col_download, col_reiniciar = st.columns(2)

    with col_download:
        try:
             csv_data = df_resultados.to_csv(index=False).encode('utf-8')
             fecha_file = st.session_state.get('fecha_evaluacion', 'fecha').replace('/', '-').replace(' ', '_').replace(':', '-')
             st.download_button(
                 label="📊 Descargar Resultados (CSV)",
                 data=csv_data,
                 file_name=f"BigFive_Resultados_{fecha_file}.csv",
                 mime="text/csv",
                 use_container_width=True
             )
        except Exception as e:
             st.error(f"Error al generar CSV: {e}")

    with col_reiniciar:
        if st.button("🔄 Realizar Nueva Evaluación", type="primary", use_container_width=True):
            reiniciar_test() 

    st.markdown("---")

    # Disclaimer
    st.info("""
    **Disclaimer:** Los resultados de este test son orientativos y están basados en tus respuestas 
    autorreportadas. La personalidad es compleja y multidimensional. Este test proporciona una 
    aproximación general a tu perfil, pero no reemplaza una evaluación profesional completa.
    """)

# --- 8. FLUJO PRINCIPAL Y SCROLL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()
else:
    st.error("Estado inválido de la aplicación. Reiniciando...")
    reiniciar_test()

# Ejecución Condicional del Scroll (FIX FINAL ROBUSTO)
if st.session_state.get('should_scroll', False):
    forzar_scroll_al_top() 
    st.session_state.should_scroll = False
