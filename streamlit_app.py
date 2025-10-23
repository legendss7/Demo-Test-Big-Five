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

# Ancla para scroll al inicio de la página
st.html('<a id="top-anchor"></a>')

# Definición de las dimensiones del Big Five
# Se utiliza Estabilidad Emocional como opuesto a Neuroticismo (N) para puntajes positivos
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
    """Invierte el puntaje para preguntas inversas (1->5, 2->4, 3->3, 4->2, 5->1)."""
    if isinstance(score, (int, float)):
        return 6 - score
    return 3 # Fallback para asegurar que el cálculo no falle

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
    # Se usa un key dinámico para forzar el re-render de este componente JS
    components.html(js_code, height=0, scrolling=False, key=f"scroll_component_{datetime.now().timestamp()}")

# --- 3. FUNCIONES DE CÁLCULO Y LÓGICA ---
def calcular_resultados(respuestas):
    """Calcula las puntuaciones de las 5 dimensiones (0-100)."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}

    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'])

        if isinstance(respuesta, (int, float)):
             # Aplicar la inversión de puntaje si es necesario
             if p['reverse']:
                 score = reverse_score(respuesta)
             else:
                 score = respuesta
        else:
            # Si no hay respuesta, se asume un puntaje neutral (3)
            score = 3 

        scores[p['dim']].append(score)

    resultados = {}
    for dim, score_list in scores.items():
        if score_list: 
             # Cálculo del promedio de las 10 preguntas (escala 1-5)
             avg_score = np.mean(score_list)
             # Conversión a escala porcentual (0-100)
             # (avg_score - min_score) / (max_score - min_score) * 100
             # (avg_score - 1) / (5 - 1) * 100
             percent_score = ((avg_score - 1) / 4) * 100
             resultados[dim] = round(percent_score, 1) 
        else:
             # Fallback si no hay datos
             resultados[dim] = 50.0 

    return resultados

def get_nivel_interpretacion(score):
    """Clasifica el puntaje y retorna nivel, color y etiqueta."""
    if score is None: return "N/A", "#808080", "Indeterminado"
    # Se definen umbrales de interpretación (percentiles aproximados)
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
            "Muy Alto": "**Roles Idóneos:** Innovación, I+D, Diseño Estratégico, Artista, Investigador. **Fortalezas:** Curiosidad, creatividad, adaptabilidad. **Desafío:** Mantener el foco y la ejecución.",
            "Alto": "**Roles Idóneos:** Marketing Creativo, Consultoría, Desarrollo de Nuevos Productos. **Fortalezas:** Abierto a nuevas ideas, pensamiento flexible. **Desafío:** Evitar la fatiga por el cambio constante.",
            "Promedio": "**Aptitud General:** Bueno para roles que equilibran rutina y novedad. Puede participar en mejora continua. **Foco:** Ser proactivo en proponer soluciones.",
            "Bajo": "**Roles Idóneos:** Tareas Rutinarias, Control de Calidad, Administración. **Precaución:** Requiere apoyo para manejar cambios. **Foco:** Entender el 'por qué' del cambio.",
            "Muy Bajo": "**Roles No Idóneos:** Innovación Disruptiva, Estratega. **Aptitud:** Prefiere entornos predecibles. **Foco:** Priorizar la eficiencia y la estabilidad."
        },
        "Responsabilidad": {
            "Muy Alto": "**Roles Idóneos:** Gerencia de Proyectos, Auditoría, Contraloría, Finanzas. **Fortalezas:** Organización, disciplina, fiabilidad. **Desafío:** Delegar y evitar el perfeccionismo paralizante.",
            "Alto": "**Roles Idóneos:** Planificación Financiera, Logística, Ingeniería de Procesos. **Fortalezas:** Cumplimiento de plazos, detalle. **Desafío:** Aceptar que no todo es controlable.",
            "Promedio": "**Aptitud General:** Mantiene disciplina en roles definidos. Mejorar con herramientas de gestión. **Foco:** Establecer metas claras y un sistema de seguimiento.",
            "Bajo": "**Roles Idóneos:** Roles Flexibles, Ventas Creativas (con supervisión). **Precaución:** Necesita seguimiento estructurado. **Foco:** Uso de listas de tareas y priorización (ej. Método GTD).",
            "Muy Bajo": "**Roles No Idóneos:** Auditoría, Gestión Crítica. **Aptitud:** Funciona mejor en entornos menos estructurados. **Foco:** Concentrarse en una tarea a la vez para mejorar la finalización."
        },
        "Extraversión": {
            "Muy Alto": "**Roles Idóneos:** Dirección Comercial, Liderazgo, Relaciones Públicas, Ventas. **Fortalezas:** Sociabilidad, asertividad, energía. **Desafío:** Escuchar activamente y dar espacio a otros.",
            "Alto": "**Roles Idóneos:** Jefe de Equipo, Capacitador, Eventos. **Fortalezas:** Buena comunicación, disfruta interacción. **Desafío:** Manejar el tiempo de forma efectiva en la interacción.",
            "Promedio": "**Aptitud General:** Adaptable. Funciona bien en equipo y solo. **Foco:** Desarrollar habilidades de presentación y networking.",
            "Bajo": "**Roles Idóneos:** Analista, Programador, Escritor Técnico, Investigador. **Precaución:** Puede agotarse en roles de alta interacción. **Foco:** Establecer límites y proteger el tiempo de concentración.",
            "Muy Bajo": "**Roles No Idóneos:** Ventas de Campo, PR. **Aptitud:** Prefiere trabajo individual y entornos tranquilos. **Foco:** Usar comunicación escrita o reuniones 1:1 para expresar ideas."
        },
        "Amabilidad": {
            "Muy Alto": "**Roles Idóneos:** Gerencia de RR.HH., Servicio al Cliente, Mediador, Terapeuta. **Fortalezas:** Empatía, cooperación. **Desafío:** Decir 'no' cuando sea necesario y defender sus propias posiciones.",
            "Alto": "**Roles Idóneos:** Trabajo Social, Enfermería, Consultor Interno. **Fortalezas:** Colaborador, considerado. **Desafío:** Evitar el exceso de complacencia.",
            "Promedio": "**Aptitud General:** Buen colaborador. Fomentar liderazgo servicial. **Foco:** Buscar activamente la retroalimentación honesta.",
            "Bajo": "**Roles Idóneos:** Negociador, Analista Crítico, Abogado Litigante. **Precaución:** Puede generar conflictos. **Foco:** Practicar la escucha empática antes de responder.",
            "Muy Bajo": "**Roles No Idóneos:** Soporte al Cliente, RR.HH. **Aptitud:** Toma de decisiones objetiva, competitivo. **Foco:** Entender el impacto de la rudeza y buscar un lenguaje constructivo."
        },
        "Estabilidad Emocional": {
            "Muy Alto": "**Roles Idóneos:** Gestión de Crisis, Operaciones de Alto Estrés, Liderazgo Ejecutivo. **Fortalezas:** Resiliencia, calma bajo presión. **Desafío:** Evitar parecer frío o distante; mostrar empatía.",
            "Alto": "**Roles Idóneos:** Cirujano, Piloto, Bombero. **Fortalezas:** Manejo efectivo del estrés. **Desafío:** Prestar atención a las señales sutiles de estrés en uno mismo.",
            "Promedio": "**Aptitud General:** Gestión emocional adecuada. Ofrecer talleres de estrés. **Foco:** Implementar técnicas de *mindfulness*.",
            "Bajo": "**Roles Idóneos (con apoyo):** Roles Creativos, Terapeuta. **Precaución:** Sensible al estrés. **Foco:** Desarrollar estrategias de afrontamiento y auto-regulación.",
            "Muy Bajo": "**Roles No Idóneos:** Operaciones de Crisis. **Precaución:** Requiere ambiente de baja presión y soporte. **Foco:** Evitar la rumia mental y buscar apoyo profesional si es necesario."
        },
    }

    return rec_db.get(dim, {}).get(nivel_map, "Analizar fortalezas y debilidades para la ruta profesional.")

def get_roles_no_recomendados(resultados):
    """Determina roles no recomendados basándose en puntajes extremos (resumen)."""
    no_aptos = set()
    UMBRAL_BAJO = 25 # Puntaje bajo es un indicador de posible incompatibilidad crítica
    UMBRAL_ALTO = 75 # Puntaje alto es un indicador de posible desafío social

    if resultados.get("Estabilidad Emocional", 50) < UMBRAL_BAJO: 
        no_aptos.add("Operaciones de Crisis/Alto Estrés (Baja Estabilidad <25)")
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

    # Prepara los datos para el radar
    categories = [DIMENSIONES[dim]['code'] + ' - ' + dim.split(' ')[0] for dim in resultados.keys()] 
    values = list(resultados.values())
    
    # Repite el primer valor al final para cerrar el círculo en el gráfico
    values.append(values[0])
    categories.append(categories[0]) 

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
                linecolor="#cccccc",
                gridcolor="#e0e0e0"
            ),
            angularaxis=dict(
                linecolor="#cccccc",
                gridcolor="#e0e0e0"
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
    # Ordena para visualizar mejor las fortalezas y debilidades
    df = df.sort_values('Puntuación', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['Dimensión'],
        x=df['Puntuación'],
        orientation='h',
        marker=dict(
            # Escala de color que va de rojo (bajo) a verde (alto)
            color=df['Puntuación'],
            colorscale='RdYlGn', 
            cmin=0, cmax=100, 
            colorbar=dict(title="Puntuación", x=1.05) 
        ),
        text=df['Puntuación'].round(1).astype(str) + '%', # Mostrar porcentaje en la barra
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Puntuación: %{x:.1f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Puntuaciones por Dimensión", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Puntuación (0-100)", range=[0, 110], showgrid=True, gridcolor='#e0e0e0'), 
        yaxis=dict(title="", tickfont=dict(size=10)), 
        height=400, 
        margin=dict(l=200, r=50, t=50, b=50), 
        template="plotly_white"
    )

    return fig

def crear_grafico_comparativo(resultados):
    """Crea gráfico comparativo con la población promedio (asumido en 50)."""
    if resultados is None: return go.Figure()

    dimensiones = list(resultados.keys())
    tu_perfil = list(resultados.values())
    promedio = [50] * len(dimensiones) # El promedio poblacional se establece en 50 (percentil 50)

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
        textposition='inside'
    ))

    fig.update_layout(
        title=dict(text="Tu Perfil vs Promedio Poblacional", x=0.5, xanchor='center', font=dict(size=18)),
        yaxis=dict(title="Puntuación (0-100)", range=[0, 115], showgrid=True, gridcolor='#e0e0e0'), 
        xaxis=dict(title="", tickangle=-45), 
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white"
    )

    return fig


# --- 5. FUNCIONES DE NAVEGACIÓN Y FLUJO ---
def iniciar_test():
    """Inicializa el estado para comenzar el test."""
    st.session_state.stage = 'test_activo'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None
    st.session_state.should_scroll = True 
    st.rerun()

def completar_al_azar():
    """Genera respuestas aleatorias y va directamente a resultados (Demo)."""
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
    # st.rerun() se llama al final del flujo principal

def avanzar_dimension():
    """Avanza al siguiente índice de dimensión o finaliza."""
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
    """Vista de inicio y explicación del test."""
    st.title("🧠 Test de Personalidad Big Five (OCEAN)")
    st.markdown("### Evaluación Profesional de los Cinco Grandes Factores de Personalidad")

    st.info("""
    El modelo Big Five es el marco más respaldado científicamente para comprender la personalidad humana. 
    Mide cinco dimensiones fundamentales que influyen en el comportamiento laboral y personal.
    """)

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Información del Test")
        st.markdown("""
        - **Duración estimada:** 10-15 minutos
        - **Preguntas:** 50 ítems (10 por dimensión)
        - **Escala de Respuesta:** Likert de 5 puntos (Totalmente en Desacuerdo a Totalmente de Acuerdo).
        - **Dimensiones evaluadas:**
          - 💡 **O**penness (Apertura a la Experiencia)
          - 🎯 **C**onscientiousness (Responsabilidad)
          - 🗣️ **E**xtraversion (Extraversión)
          - 🤝 **A**greeableness (Amabilidad)
          - 🧘 **N**euroticism (Estabilidad Emocional - Opuesto a Neuroticismo)
        """)

    with col2:
        st.subheader("🚀 Comenzar Evaluación")

        if st.button("📝 Iniciar Test Profesional", type="primary", use_container_width=True):
            iniciar_test() 

        st.markdown("---")

        st.caption("**Opciones de Demostración:**")
        if st.button("🎲 Completar Aleatoriamente (DEMO)", type="secondary", use_container_width=True):
            completar_al_azar() 
    
    st.markdown("---")
    st.subheader("Entendiendo las Dimensiones")
    
    # Mostrar una tabla resumen de las dimensiones
    dim_data = []
    for name, info in DIMENSIONES.items():
        dim_data.append({
            "Factor": f"{info['icon']} **{name}** ({info['code']})",
            "Descripción Clave": info['desc'],
            "Puntaje Alto": info['caracteristicas_altas'].split(',')[0] + "...",
            "Puntaje Bajo": info['caracteristicas_bajas'].split(',')[0] + "..."
        })
        
    df_dims = pd.DataFrame(dim_data)
    st.markdown(df_dims.to_markdown(index=False), unsafe_allow_html=True)


def vista_test_activo():
    """Vista del test activo, con navegación por dimensiones."""
    current_index = st.session_state.current_dimension_index
    current_dim_name = DIMENSIONES_LIST[current_index]
    dim_info = DIMENSIONES[current_dim_name]

    st.title(f"{dim_info['icon']} Sección {current_index + 1} de {len(DIMENSIONES_LIST)}")
    st.subheader(f"Dimensión: {current_dim_name}")
    st.markdown(f"*{dim_info['desc']}*")

    # Calculo y visualización de progreso general
    total_respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None)
    total_preguntas = len(PREGUNTAS)
    progreso = total_respondidas / total_preguntas

    st.progress(progreso, text=f"Progreso General: {total_respondidas}/{total_preguntas} preguntas ({progreso*100:.0f}%)")
    st.markdown("---")

    preguntas_dimension = [p for p in PREGUNTAS if p['dim'] == current_dim_name]

    # Usar un formulario para capturar todas las respuestas de la dimensión a la vez
    with st.form(f"form_dim_{current_index}", clear_on_submit=False):
        st.caption("Usa la escala: 1 (Totalmente en desacuerdo) a 5 (Totalmente de acuerdo).")

        respuestas_form_actual = {}
        # Muestra 10 preguntas por dimensión
        for i, p in enumerate(preguntas_dimension, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {p['text']}**")

                initial_value = st.session_state.respuestas.get(p['key'])
                # Necesita el índice (0-4) para el valor inicial, no el valor (1-5)
                initial_index = LIKERT_OPTIONS.index(initial_value) if initial_value is not None else None

                widget_key = f"radio_{p['key']}_{st.session_state.current_dimension_index}" 
                respuestas_form_actual[p['key']] = st.radio(
                    label=f"Respuesta para {p['key']}",
                    options=LIKERT_OPTIONS,
                    format_func=lambda x: ESCALA_LIKERT[x],
                    index=initial_index,
                    key=widget_key,
                    horizontal=True,
                    label_visibility="collapsed"
                )


        st.markdown("---")
        
        # Botones de navegación
        col_prev, col_next = st.columns(2)

        # Botón para ir atrás
        with col_prev:
            if current_index > 0:
                prev_dim_name = DIMENSIONES_LIST[current_index - 1]
                if st.form_submit_button(f"⏪ Atrás a: {prev_dim_name}", type="secondary", use_container_width=True):
                    # No es necesario validar, solo retroceder
                    st.session_state.current_dimension_index -= 1
                    st.session_state.should_scroll = True
                    st.rerun()

        # Botón para ir adelante/finalizar
        with col_next:
            if current_index == len(DIMENSIONES_LIST) - 1:
                button_label = "✅ Finalizar y Ver Resultados"
                button_type = "primary"
            else:
                next_dim = DIMENSIONES_LIST[current_index + 1]
                button_label = f"➡️ Continuar a: {next_dim}"
                button_type = "primary"

            submitted = st.form_submit_button(button_label, type=button_type, use_container_width=True)

            if submitted:
                # 1. Validar que todas las preguntas del formulario actual estén respondidas
                validation_passed = True
                for q_key, answer in respuestas_form_actual.items():
                    if answer is None:
                         validation_passed = False
                         break

                if not validation_passed:
                    st.error(f"⚠️ Por favor, responde todas las 10 afirmaciones de esta sección ({current_dim_name}) antes de continuar.")
                    st.session_state.should_scroll = True # Scroll para ver el error
                    st.rerun()
                else:
                    # 2. Guardar las respuestas en el estado
                    st.session_state.respuestas.update(respuestas_form_actual)
                    # 3. Avanzar o finalizar
                    avanzar_dimension()

def vista_resultados():
    """Vista de resultados profesional."""
    resultados = st.session_state.resultados

    if resultados is None:
        st.warning("No hay resultados disponibles. Por favor, completa el test.")
        if st.button("Volver al Inicio"):
            reiniciar_test()
            st.rerun()
        return

    st.title("📊 Tu Informe de Personalidad Big Five")
    fecha_eval = st.session_state.get('fecha_evaluacion', "Fecha no registrada")
    st.markdown(f"**Fecha de Evaluación:** {fecha_eval}")
    st.markdown("---")

    # --- 1. RESUMEN EJECUTIVO ---
    st.header("1. 📈 Resumen Ejecutivo y Visualización Global")

    col_metric, col_chart = st.columns([1, 2])
    
    with col_metric:
        promedio_total = np.mean(list(resultados.values()))
        st.metric(label="Puntuación Promedio General", value=f"{promedio_total:.1f}/100", delta="Perfil Equilibrado" if 45 <= promedio_total <= 55 else "Perfil Destacado")
        
        # Identificar la dimensión más alta y más baja
        dim_max = max(resultados, key=resultados.get)
        dim_min = min(resultados, key=resultados.get)
        
        st.success(f"**Fortaleza Clave:** {DIMENSIONES[dim_max]['icon']} {dim_max} ({resultados[dim_max]:.1f})")
        st.warning(f"**Área de Foco:** {DIMENSIONES[dim_min]['icon']} {dim_min} ({resultados[dim_min]:.1f})")

    with col_chart:
        fig_radar = crear_grafico_radar(resultados)
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # --- 2. ANÁLISIS GRÁFICO DETALLADO ---
    st.header("2. 📉 Análisis de Perfil")

    tab1, tab2 = st.tabs(["📊 Puntuación por Factor", "⚖️ Comparación Poblacional"])

    with tab1:
        fig_barras = crear_grafico_barras(resultados)
        st.plotly_chart(fig_barras, use_container_width=True, config={'displayModeBar': False})
        st.caption("Gráfico de barras horizontal mostrando tus puntuaciones. Mayor puntuación = mayor presencia del rasgo.")

    with tab2:
        fig_comp = crear_grafico_comparativo(resultados)
        st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
        st.caption("El promedio poblacional se establece en 50/100. Las barras por encima indican un rasgo más marcado que el promedio.")

    st.markdown("---")

    # --- 3. INTERPRETACIÓN Y RECOMENDACIONES ---
    st.header("3. 💡 Interpretación por Dimensión")

    for dim_name in DIMENSIONES_LIST:
        score = resultados.get(dim_name, 50) 
        dim_info = DIMENSIONES[dim_name]
        nivel, color, etiqueta = get_nivel_interpretacion(score)

        with st.expander(f"{dim_info['icon']} **{dim_name}** ({dim_info['code']}) - **{score:.1f}** puntos ({nivel})", expanded=True):
            
            st.markdown(f"**Nivel:** <span style='color:{color}; font-weight: bold; font-size: 1.1em;'>{nivel} ({etiqueta})</span>", unsafe_allow_html=True)
            st.markdown(f"**Descripción:** {dim_info['desc']}")

            col_tipos, col_rec = st.columns([1, 2])

            with col_tipos:
                 if score >= 60:
                    st.success(f"**Orientación:** Alto nivel de las siguientes características:")
                    st.markdown(f"• {dim_info['caracteristicas_altas'].replace(',', '\n• ')}")
                 elif score <= 40:
                    st.warning(f"**Orientación:** Bajo nivel de las siguientes características:")
                    st.markdown(f"• {dim_info['caracteristicas_bajas'].replace(',', '\n• ')}")
                 else: 
                    st.info(f"**Orientación:** Perfil balanceado. Características moderadas.")
                    st.markdown(f"• {dim_info['caracteristicas_altas'].split(',')[0]} (Alta) / {dim_info['caracteristicas_bajas'].split(',')[0]} (Baja)")
            
            with col_rec:
                st.markdown("**💼 Implicaciones Profesionales y Desarrollo:**")
                recomendacion_profesional = get_recomendaciones_detalladas(dim_name, score)
                st.markdown(recomendacion_profesional) 

            st.markdown("---")
            
    # --- 4. ALERTA DE INCOMPATIBILIDAD ---
    st.header("4. 🛑 Alertas y Foco de Desarrollo")
    
    roles_no_aptos = get_roles_no_recomendados(resultados)

    if roles_no_aptos is None:
        st.success("✅ **Perfil Versátil:** No se identificaron incompatibilidades significativas para roles críticos basadas en puntuaciones extremas (por debajo de 25).")
    else:
        st.error(f"**Cargos NO Recomendados o de Alto Riesgo:** {roles_no_aptos}")
        st.caption("Esta lista se basa en puntuaciones extremas (por debajo de 25/100) en el factor clave para dicho rol. Sugiere precaución y un alto esfuerzo de adaptación.")

    st.markdown("---")


    # --- 5. EXPORTAR Y ACCIONES FINALES ---
    st.header("5. 📥 Acciones de Informe")

    col_download, col_reiniciar = st.columns(2)

    with col_download:
        try:
             # Generar la tabla de resultados para exportar
             df_resultados = pd.DataFrame({
                'Dimensión': [dim for dim in resultados.keys()],
                'Código': [DIMENSIONES[dim]['code'] for dim in resultados.keys()],
                'Puntuación_0-100': [f"{score:.1f}" for score in resultados.values()],
                'Nivel_Interpretacion': [get_nivel_interpretacion(score)[0] for score in resultados.values()],
            })
             csv_data = df_resultados.to_csv(index=False).encode('utf-8')
             fecha_file = st.session_state.get('fecha_evaluacion', 'fecha').replace('/', '-').replace(' ', '_').replace(':', '-')
             st.download_button(
                 label="📊 Descargar Informe Completo (CSV)",
                 data=csv_data,
                 file_name=f"BigFive_Resultados_{fecha_file}.csv",
                 mime="text/csv",
                 use_container_width=True
             )
        except Exception as e:
             st.error(f"Error al generar CSV: {e}")

    with col_reiniciar:
        if st.button("🔄 Realizar Nueva Evaluación", type="secondary", use_container_width=True, on_click=reiniciar_test):
            pass # La función on_click ya maneja el reinicio y rerender


    # Disclaimer al final
    st.markdown("---")
    st.info("""
    **Nota Importante:** Este informe es una herramienta de autoconocimiento. Las puntuaciones 
    son relativas a la población general y solo representan tendencias de comportamiento. 
    Se recomienda complementar con experiencia práctica y retroalimentación externa.
    """)


# --- 7. FLUJO PRINCIPAL Y SCROLL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()
else:
    st.error("Estado de la aplicación inválido. Volviendo al inicio.")
    reiniciar_test()

# 8. Ejecución Condicional del Scroll al final del script
if st.session_state.get('should_scroll', False):
    forzar_scroll_al_top() 
    st.session_state.should_scroll = False 
