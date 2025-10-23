import streamlit as st
import pandas as pd
import numpy as np
import time # Added time for potential delays if needed
import plotly.graph_objects as go
import plotly.express as px # Added for potential future use
import streamlit.components.v1 as components
import random
from datetime import datetime

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(
    layout="wide",
    page_title="Test Big Five (OCEAN) | Evaluación Profesional",
    page_icon="🧠"
)

# Ancla para scroll (como solicitaste)
st.markdown('<div id="top-anchor" style="position: absolute; top: 0; left: 0; height: 1px;"></div>', unsafe_allow_html=True)


# Definición de las dimensiones del Big Five
DIMENSIONES = {
    "Apertura a la Experiencia": {
        "code": "O",
        "color": "#0077b6", # Azul principal
        "icon": "💡",
        [cite_start]"desc": "Imaginación, curiosidad intelectual, creatividad y aprecio por el arte y las nuevas experiencias."[cite: 207],
        "caracteristicas_altas": "Creativo, curioso, aventurero, con mente abierta",
        "caracteristicas_bajas": "Práctico, convencional, prefiere lo familiar"
    },
    "Responsabilidad": {
        "code": "C",
        "color": "#00b4d8", # Azul claro
        "icon": "🎯",
        [cite_start]"desc": "Autodisciplina, organización, cumplimiento de objetivos y sentido del deber."[cite: 208],
        "caracteristicas_altas": "Organizado, confiable, disciplinado, planificado",
        "caracteristicas_bajas": "Flexible, espontáneo, despreocupado"
    },
    "Extraversión": {
        "code": "E",
        "color": "#48cae4", # Turquesa
        "icon": "🗣️",
        "desc": "Sociabilidad, asertividad, energía y búsqueda de estimulación en compañía de otros.",
        "caracteristicas_altas": "Sociable, hablador, asertivo, enérgico",
        [cite_start]"caracteristicas_bajas": "Reservado, tranquilo, independiente, reflexivo" [cite: 209]
    },
    "Amabilidad": {
        "code": "A",
        "color": "#90e0ef", # Azul muy claro
        "icon": "🤝",
        "desc": "Cooperación, empatía, compasión, confianza y respeto por los demás.",
        "caracteristicas_altas": "Compasivo, cooperativo, confiado, altruista",
        "caracteristicas_bajas": "Competitivo, escéptico, directo, objetivo"
    },
    "Estabilidad Emocional": { # Renombrado desde Neuroticismo para claridad
        "code": "N", # Código original mantenido
        "color": "#0096c7", # Azul medio
        "icon": "🧘", # Icono cambiado
        [cite_start]"desc": "Capacidad para mantener la calma y gestionar el estrés. (Opuesto a Neuroticismo)"[cite: 210, 211],
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

# [cite_start]50 Preguntas del Big Five (10 por dimensión) [cite: 212]
PREGUNTAS = [
    # [cite_start]Apertura a la Experiencia (O) [cite: 212, 213, 214]
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

    # [cite_start]Responsabilidad (C) [cite: 214, 215]
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

    # [cite_start]Extraversión (E) [cite: 215, 216, 217]
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

    # [cite_start]Amabilidad (A) [cite: 217, 218, 219]
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

    # [cite_start]Estabilidad Emocional (N invertido) [cite: 219, 220]
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
    [cite_start]st.session_state.respuestas = {p['key']: None for p in PREGUNTAS} [cite: 221]
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'current_dimension_index' not in st.session_state:
    st.session_state.current_dimension_index = 0
if 'should_scroll' not in st.session_state:
    st.session_state.should_scroll = False # Bandera para controlar el scroll
if 'fecha_evaluacion' not in st.session_state:
    st.session_state.fecha_evaluacion = None

# --- 2. FUNCIONES DE SCROLL ---
def forzar_scroll_al_top():
    """Fuerza el scroll al inicio usando JS y el ancla 'top-anchor'."""
    # El idx no es necesario con el ancla
    js_code = """
        <script>
            // Usamos un pequeño delay para asegurar que el DOM se haya actualizado
            setTimeout(function() {
                var topAnchor = window.parent.document.getElementById('top-anchor');
                if (topAnchor) {
                    topAnchor.scrollIntoView({ behavior: 'auto', block: 'start' });
                } else {
                    // Fallbacks si el ancla falla
                    [cite_start]window.parent.scrollTo({ top: 0, behavior: 'auto' }); [cite: 222]
                    var mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                    if (mainContent) {
                        mainContent.scrollTo({ top: 0, behavior: 'auto' });
                    }
                }
            }, 150); // Delay corto
        </script>
    [cite_start]""" [cite: 223]
    # Usamos clave estática para evitar TypeError
    components.html(js_code, height=0, scrolling=False, key="scroll_component_static")

# --- 3. FUNCIONES DE CÁLCULO Y LÓGICA ---
def calcular_resultados(respuestas):
    """Calcula las puntuaciones de las 5 dimensiones (0-100)."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}

    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'])

        # Validar y asignar score
        if isinstance(respuesta, (int, float)):
             [cite_start]if p['reverse']: [cite: 224]
                 score = reverse_score(respuesta)
             else:
                 score = respuesta
        else:
            score = 3 # Neutral como fallback

        scores[p['dim']].append(score)

    resultados = {}
    for dim, score_list in scores.items():
        if score_list: # Evitar división por cero si la lista está vacía
             avg_score = np.mean(score_list)
             # [cite_start]Convertir de escala 1-5 a 0-100 [cite: 225]
             percent_score = ((avg_score - 1) / 4) * 100
             resultados[dim] = round(percent_score, 1) # Redondeo a 1 decimal
        else:
             resultados[dim] = 50.0 # Fallback si no hay scores

    return resultados

def get_nivel_interpretacion(score):
    """Clasifica el puntaje y retorna nivel, color y etiqueta."""
    if score is None: return "N/A", "#808080", "Indeterminado"
    if score >= 75: return "Muy Alto", "#2a9d8f", "Dominante"
    elif score >= 60: return "Alto", "#264653", "Marcado"
    [cite_start]elif score >= 40: return "Promedio", "#e9c46a", "Moderado" [cite: 226]
    elif score >= 25: return "Bajo", "#f4a261", "Suave"
    else: return "Muy Bajo", "#e76f51", "Mínimo" # Cambiado de Recesivo

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

    # Usa fallback de 50 si falta el resultado para evitar errores
    if resultados.get("Estabilidad Emocional", 50) < UMBRAL_BAJO: # Opuesto a Neuroticismo ALTO
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

    # Usar códigos cortos para las etiquetas del radar
    categories = [DIMENSIONES[dim]['code'] + ' - ' + dim.split(' ')[0] for dim in resultados.keys()] # Ej: O - Apertura
    values = list(resultados.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Tu Perfil',
        [cite_start]line=dict(color='#0077b6', width=3), [cite: 227]
        [cite_start]fillcolor='rgba(0, 119, 182, 0.25)', [cite: 227]
        [cite_start]marker=dict(size=10, color='#00b4d8') [cite: 227]
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                [cite_start]visible=True, [cite: 228]
                [cite_start]range=[0, 100], [cite: 228]
                [cite_start]tickvals=[0, 25, 50, 75, 100], [cite: 228]
                [cite_start]ticktext=["0", "25", "50", "75", "100"], [cite: 228]
                [cite_start]linecolor="#cccccc" [cite: 228]
            ),
            angularaxis=dict(
                [cite_start]linecolor="#cccccc" [cite: 229]
            ),
        ),
        showlegend=False,
        height=600,
        title=dict(
            text="Perfil de Personalidad Big Five (OCEAN)",
            [cite_start]x=0.5, [cite: 230]
            [cite_start]xanchor='center', [cite: 230]
            [cite_start]font=dict(size=20, color='#333') [cite: 230]
        ),
        [cite_start]template="plotly_white" [cite: 230]
    )
    fig.update_traces(hovertemplate='<b>%{theta}</b><br>Puntuación: %{r:.1f}<extra></extra>')

    return fig

def crear_grafico_barras(resultados):
    """Crea gráfico de barras horizontales."""
    [cite_start]if resultados is None: return go.Figure() [cite: 231]

    df = pd.DataFrame({
        'Dimensión': list(resultados.keys()),
        'Puntuación': list(resultados.values())
    })
    df = df.sort_values('Puntuación', ascending=True)

    [cite_start]fig = go.Figure() [cite: 231]

    fig.add_trace(go.Bar(
        y=df['Dimensión'],
        x=df['Puntuación'],
        orientation='h',
        marker=dict(
            color=df['Puntuación'],
            colorscale='RdYlGn', # Rojo-Amarillo-Verde
            cmin=0, cmax=100, # Rango de color
            colorbar=dict(title="Puntuación", x=1.05) # Mover colorbar un poco
        ),
        [cite_start]text=df['Puntuación'].round(1), [cite: 232]
        [cite_start]textposition='outside', [cite: 232]
        [cite_start]hovertemplate='<b>%{y}</b><br>Puntuación: %{x:.1f}<extra></extra>' [cite: 232]
    ))

    fig.update_layout(
        title=dict(text="Puntuaciones por Dimensión", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Puntuación (0-100)", range=[0, 110]), # Ampliar rango para texto
        yaxis=dict(title="", tickfont=dict(size=10)), # Ajustar tamaño fuente eje Y
        height=400, # Reducir altura
        margin=dict(l=200, r=50, t=50, b=50), # Ajustar márgenes
        template="plotly_white"
    [cite_start]) [cite: 233]

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
        [cite_start]text=[f"{v:.1f}" for v in tu_perfil], [cite: 234]
        [cite_start]textposition='outside' [cite: 234]
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
        [cite_start]title=dict(text="Tu Perfil vs Promedio Poblacional", x=0.5, xanchor='center', font=dict(size=18)), [cite: 235]
        yaxis=dict(title="Puntuación (0-100)", range=[0, 115]), # Ampliar rango
        xaxis=dict(title="", tickangle=-45), # Rotar etiquetas eje X
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
    [cite_start]st.session_state.respuestas = {p['key']: None for p in PREGUNTAS} [cite: 236]
    st.session_state.resultados = None
    st.session_state.should_scroll = True # Activar scroll para la primera página
    st.rerun()

def completar_al_azar():
    """Genera respuestas aleatorias y va a resultados."""
    st.session_state.respuestas = {p['key']: random.choice(LIKERT_OPTIONS) for p in PREGUNTAS}
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.stage = 'resultados'
    st.session_state.should_scroll = True # Activar scroll para la página de resultados
    st.rerun()

def reiniciar_test():
    """Reinicia el test."""
    st.session_state.stage = 'inicio'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None
    st.session_state.should_scroll = True # Activar scroll para la página de inicio
    st.rerun()

def avanzar_dimension():
    """Avanza al siguiente índice de dimensión."""
    if st.session_state.current_dimension_index < len(DIMENSIONES_LIST) - 1:
        [cite_start]st.session_state.current_dimension_index += 1 [cite: 251]
        st.session_state.should_scroll = True # Activar scroll para la siguiente página
        st.rerun()
    else:
        # Calcular resultados y cambiar de stage (esto ya lo hace procesar...)
        procesar_y_mostrar_resultados()

def procesar_y_mostrar_resultados():
    """Calcula resultados, guarda fecha y cambia a stage 'resultados'."""
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    [cite_start]st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M") [cite: 252]
    [cite_start]st.session_state.stage = 'resultados' [cite: 252]
    st.session_state.should_scroll = True # Activar scroll para la página de resultados
    st.rerun()

# --- 6. VISTAS ---
def vista_inicio():
    """Vista de inicio."""
    # Scroll se maneja al final del script

    [cite_start]st.title("🧠 Test de Personalidad Big Five (OCEAN)") [cite: 237]
    [cite_start]st.markdown("### Evaluación Profesional de los Cinco Grandes Factores de Personalidad") [cite: 237]

    st.info("""
    El modelo Big Five (también conocido como OCEAN) es el marco más respaldado científicamente para
    [cite_start]comprender la personalidad humana[cite: 238]. Mide cinco dimensiones fundamentales que predicen
    [cite_start]comportamientos en múltiples contextos[cite: 238, 239].
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
          - [cite_start]💡 **O**penness (Apertura a la Experiencia) [cite: 240]
          - [cite_start]🎯 **C**onscientiousness (Responsabilidad) [cite: 240]
          - [cite_start]🗣️ **E**xtraversion (Extraversión) [cite: 240]
          - [cite_start]🤝 **A**greeableness (Amabilidad) [cite: 240]
          - [cite_start]🧘 **N**euroticism (Estabilidad Emocional*) [cite: 240]

        [cite_start]_*En este test medimos Estabilidad Emocional (opuesto a Neuroticismo)_ [cite: 240]
        [cite_start]""") [cite: 241]

    with col2:
        st.subheader("🚀 Comenzar")

        # Usamos on_click para llamar a la función de inicio
        if st.button("📝 Iniciar Test", type="primary", use_container_width=True):
            iniciar_test() # Esta función ahora incluye st.rerun() y activa el scroll

        st.markdown("---")

        st.caption("**Modo Demo:**")
        # Usamos on_click para la función aleatoria
        [cite_start]if st.button("🎲 Completar Aleatoriamente", type="secondary", use_container_width=True): [cite: 242]
            completar_al_azar() # Esta función ahora incluye st.rerun() y activa el scroll

def vista_test_activo():
    """Vista del test activo."""
    # Scroll se maneja al final del script

    current_index = st.session_state.current_dimension_index
    current_dim_name = DIMENSIONES_LIST[current_index]
    dim_info = DIMENSIONES[current_dim_name]

    st.title(f"{dim_info['icon']} Dimensión {current_index + 1} de {len(DIMENSIONES_LIST)}: {current_dim_name}")
    st.markdown(f"**{dim_info['desc']}**")

    # Progreso general
    [cite_start]total_respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None) [cite: 243]
    total_preguntas = len(PREGUNTAS)
    progreso = total_respondidas / total_preguntas

    [cite_start]st.progress(progreso, text=f"Progreso: {total_respondidas}/{total_preguntas} preguntas ({progreso*100:.0f}%)") [cite: 243]
    st.markdown("---")

    preguntas_dimension = [p for p in PREGUNTAS if p['dim'] == current_dim_name]

    # Usamos st.form para agrupar las respuestas de esta dimensión
    with st.form(f"form_dim_{current_index}"):
        st.subheader(f"Responde a las siguientes 10 afirmaciones:")

        # Diccionario temporal para almacenar respuestas DENTRO del form
        respuestas_form_actual = {}
        all_questions_in_form_answered = True # Flag para validación dentro del form

        [cite_start]for i, p in enumerate(preguntas_dimension, 1): [cite: 244]
            with st.container(border=True):
                [cite_start]st.markdown(f"**{i}. {p['text']}**") [cite: 245]

                # Obtener valor previo si existe para mantener selección
                initial_value = st.session_state.respuestas.get(p['key'])
                initial_index = LIKERT_OPTIONS.index(initial_value) if initial_value is not None else None

                # Guardar la selección del radio en el diccionario temporal del form
                widget_key = f"radio_{p['key']}" # Clave única para el widget
                respuestas_form_actual[p['key']] = st.radio(
                    [cite_start]label=f"Selecciona tu respuesta para: {p['text'][:30]}...", [cite: 246]
                    options=LIKERT_OPTIONS,
                    format_func=lambda x: ESCALA_LIKERT[x],
                    index=initial_index,
                    key=widget_key,
                    [cite_start]horizontal=True, [cite: 247]
                    [cite_start]label_visibility="collapsed" [cite: 247]
                )
                # Verificar si esta pregunta específica no fue respondida en el render actual
                if respuestas_form_actual[p['key']] is None:
                    all_questions_in_form_answered = False


        st.markdown("---")

        # Determinar etiqueta del botón
        if current_index == len(DIMENSIONES_LIST) - 1:
            [cite_start]button_label = "✅ Finalizar y Ver Resultados" [cite: 248]
        else:
            next_dim = DIMENSIONES_LIST[current_index + 1]
            button_label = f"➡️ Continuar a: {next_dim}"

        # Botón de submit del formulario
        submitted = st.form_submit_button(button_label, type="primary", use_container_width=True)

        if submitted:
            # Validar que todas las preguntas DENTRO del formulario actual tengan respuesta
            # Re-verificamos usando los valores capturados en respuestas_form_actual
            validation_passed = True
            for q_key in [q['key'] for q in preguntas_dimension]:
                if respuestas_form_actual.get(q_key) is None:
                     validation_passed = False
                     break

            [cite_start]if not validation_passed: [cite: 249]
                st.error(f"⚠️ Por favor, responde todas las preguntas de esta dimensión ({current_dim_name}) antes de continuar.")
            else:
                # Si la validación pasa, actualizar el estado GLOBAL con las respuestas de este form
                [cite_start]st.session_state.respuestas.update(respuestas_form_actual) [cite: 250]

                # Llamar a la función para avanzar (que incluye st.rerun y activa el scroll)
                avanzar_dimension() # Esta función maneja si es la última dimensión o no


def vista_resultados():
    """Vista de resultados profesional."""
    # Scroll se maneja al final del script

    resultados = st.session_state.resultados

    if resultados is None:
        st.warning("No hay resultados disponibles. Por favor, completa el test.")
        [cite_start]if st.button("Volver al Inicio"): [cite: 253]
            reiniciar_test()
            # No se necesita st.rerun aquí porque reiniciar_test ya lo hace
        return

    [cite_start]st.title("📊 Tu Informe de Personalidad Big Five") [cite: 253]
    # Asegura que la fecha exista antes de mostrarla
    fecha_eval = st.session_state.get('fecha_evaluacion', "Fecha no registrada")
    st.markdown(f"**Fecha de Evaluación:** {fecha_eval}")
    st.markdown("---")

    # --- 1. RESUMEN EJECUTIVO ---
    [cite_start]st.header("1. 📈 Resumen Ejecutivo") [cite: 254]

    promedio_total = np.mean(list(resultados.values()))

    # Usar st.metric para un look más moderno
    st.metric(label="Puntuación Promedio General", value=f"{promedio_total:.1f}/100", delta="Perfil Equilibrado")

    st.markdown("---")

    # --- 2. VISUALIZACIONES ---
    st.header("2. 📊 Visualización de tu Perfil")

    tab1, tab2, tab3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])

    with tab1:
        fig_radar = crear_grafico_radar(resultados)
        st.plotly_chart(fig_radar, use_container_width=True)
        [cite_start]st.caption("Gráfico de radar mostrando tu perfil en las 5 dimensiones.") [cite: 256]

    with tab2:
        fig_barras = crear_grafico_barras(resultados)
        st.plotly_chart(fig_barras, use_container_width=True)
        [cite_start]st.caption("Puntuaciones ordenadas de menor a mayor.") [cite: 256]

    with tab3:
        fig_comp = crear_grafico_comparativo(resultados)
        st.plotly_chart(fig_comp, use_container_width=True)
        st.caption("Comparación de tu perfil con el promedio poblacional (50 puntos).")

    st.markdown("---")

    # --- 3. ANÁLISIS DETALLADO ---
    [cite_start]st.header("3. 🔍 Análisis Detallado por Dimensión") [cite: 257]

    for dim_name in DIMENSIONES_LIST:
        score = resultados.get(dim_name, 50) # Fallback
        dim_info = DIMENSIONES[dim_name]
        nivel, color, etiqueta = get_nivel_interpretacion(score)

        with st.expander(f"{dim_info['icon']} **{dim_name}**: {score:.1f} puntos ({nivel})", expanded=True):
            [cite_start]col1, col2 = st.columns([1, 2]) [cite: 258]

            with col1:
                # [cite_start]Medidor circular [cite: 258]
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    [cite_start]domain={'x': [0, 1], 'y': [0, 1]}, [cite: 259]
                    title={'text': f"{dim_info['code']}", 'font': {'size': 20}}, # Ajustar tamaño
                    number={'font': {'size': 36}}, # Ajustar tamaño
                    gauge={
                        [cite_start]'axis': {'range': [None, 100], 'tickwidth': 1}, [cite: 260]
                        [cite_start]'bar': {'color': dim_info['color']}, [cite: 260]
                        'steps': [
                            [cite_start]{'range': [0, 25], 'color': '#f8d7da'}, [cite: 261]
                            [cite_start]{'range': [25, 40], 'color': '#fff3cd'}, [cite: 261]
                            [cite_start]{'range': [40, 60], 'color': '#d1ecf1'}, [cite: 261]
                            [cite_start]{'range': [60, 75], 'color': '#d4edda'}, [cite: 261]
                            [cite_start]{'range': [75, 100], 'color': '#c3e6cb'} [cite: 262]
                        ],
                        'threshold': {
                             'line': {'color': "black", 'width': 3}, # Línea negra
                             'thickness': 0.9, # Más gruesa
                             'value': score
                        [cite_start]} [cite: 263, 264] # Threshold line properties
                    }
                ))
                fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10)) # Ajustar layout
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col2:
                [cite_start]st.markdown(f"**Descripción:**") [cite: 265]
                [cite_start]st.markdown(dim_info['desc']) [cite: 265]

                [cite_start]st.markdown(f"**Nivel:** <span style='color:{color}; font-weight: bold; font-size: 1.1em;'>{nivel} ({etiqueta})</span>", unsafe_allow_html=True) [cite: 266]

                # Mostrar características altas o bajas según el score
                if score >= 60:
                    st.success(f"✅ **Puntuación Alta/Muy Alta**")
                    [cite_start]st.markdown(f"**Características Típicas:** {dim_info['caracteristicas_altas']}") [cite: 266]
                elif score <= 40:
                    st.warning(f"⚠️ **Puntuación Baja/Muy Baja**")
                    [cite_start]st.markdown(f"**Características Típicas:** {dim_info['caracteristicas_bajas']}") [cite: 268]
                else: # Promedio
                    [cite_start]st.info(f"ℹ️ **Puntuación Media**") [cite: 267]
                    [cite_start]st.markdown("Equilibrio entre las características altas y bajas.") [cite: 267]

            st.markdown("---", help="Separador visual") # Usar help para tooltip opcional

            # Interpretación profesional detallada (Idóneo/No Idóneo)
            st.markdown("**💼 Implicaciones y Aptitud Profesional:**")
            recomendacion_profesional = get_recomendaciones_detalladas(dim_name, score)
            # Usar st.markdown para renderizar el bold
            st.markdown(f" {recomendacion_profesional}") # Usar markdown en lugar de st.info/success

    st.markdown("---")

    # --- 4. FORTALEZAS Y ÁREAS DE DESARROLLO ---
    [cite_start]st.header("4. 💪 Fortalezas y Áreas de Desarrollo") [cite: 291]

    col_fort, col_des = st.columns(2)

    # Ordenar dimensiones por score
    sorted_dims = sorted(resultados.items(), key=lambda item: item[1], reverse=True)
    top_3 = sorted_dims[:3]
    # Para áreas de desarrollo, mostrar las 3 más bajas O las que estén por debajo de 40
    bottom_scores = sorted(resultados.items(), key=lambda item: item[1])
    areas_desarrollo = [item for item in bottom_scores if item[1] < 40]
    # Si hay menos de 3 por debajo de 40, completar hasta 3 con las más bajas (pero >= 40)
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
                 [cite_start]""") [cite: 292]
                 st.progress(score / 100) # Barra de progreso visual
                 st.markdown("") # Espacio

    with col_des:
        [cite_start]st.subheader("📈 Áreas Potenciales de Desarrollo") [cite: 293]
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
                     [cite_start]""", unsafe_allow_html=True) [cite: 294, 295]
                 else:
                     st.markdown(f"""
                     **{i}. {icon} {dim}**
                     - Puntuación: **{score:.1f}**/100 ({nivel})
                     - Nivel Adecuado.
                     [cite_start]""", unsafe_allow_html=True) [cite: 296]
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
    [cite_start]st.header("6. 📋 Tabla Resumen de Resultados") [cite: 297]

    df_resultados = pd.DataFrame({
        'Dimensión': [dim for dim in resultados.keys()],
        'Código': [DIMENSIONES[dim]['code'] for dim in resultados.keys()],
        'Puntuación': [f"{score:.1f}" for score in resultados.values()],
        'Nivel': [get_nivel_interpretacion(score)[0] for score in resultados.values()],
        'Etiqueta': [get_nivel_interpretacion(score)[2] for score in resultados.values()]
    [cite_start]}) [cite: 298]

    # Aplicar estilos para colorear puntuación
    def color_nivel_tabla(val):
        try:
            score = float(val)
            [cite_start]if score >= 75: return 'background-color: #c3e6cb; color: #155724; font-weight: bold;' [cite: 299]
            [cite_start]elif score >= 60: return 'background-color: #d4edda; color: #155724;' [cite: 300]
            [cite_start]elif score >= 40: return 'background-color: #d1ecf1; color: #0c5460;' [cite: 301]
            [cite_start]elif score >= 25: return 'background-color: #fff3cd; color: #856404;' [cite: 302]
            [cite_start]else: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;' [cite: 303]
        except: return ''

    styled_df = df_resultados.style.applymap(color_nivel_tabla, subset=['Puntuación'])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- 7. EXPORTAR Y ACCIONES ---
    [cite_start]st.header("7. 📥 Exportar y Acciones") [cite: 317]

    col_download, col_reiniciar = st.columns(2)

    with col_download:
        try:
             # Preparar CSV
             csv_data = df_resultados.to_csv(index=False).encode('utf-8')
             fecha_file = st.session_state.get('fecha_evaluacion', 'fecha').replace('/', '-').replace(' ', '_').replace(':', '-')
             st.download_button(
                 [cite_start]label="📊 Descargar Resultados (CSV)", [cite: 318]
                 data=csv_data,
                 [cite_start]file_name=f"BigFive_Resultados_{fecha_file}.csv", [cite: 318]
                 [cite_start]mime="text/csv", [cite: 318]
                 use_container_width=True
             )
        except Exception as e:
             st.error(f"Error al generar CSV: {e}")

    with col_reiniciar:
        # Usamos on_click para reiniciar
        if st.button("🔄 Realizar Nueva Evaluación", type="primary", use_container_width=True):
            reiniciar_test()
            # [cite_start]No se necesita st.rerun aquí [cite: 319]

    st.markdown("---")

    # [cite_start]Disclaimer [cite: 319, 320, 321]
    st.info("""
    **Disclaimer:** Los resultados de este test son orientativos y basados en tus respuestas. La personalidad es compleja. Este test ofrece una aproximación general y no reemplaza una evaluación profesional completa.
    """)

# --- 7. FLUJO PRINCIPAL ---

# Determinar la vista a mostrar según el estado
current_stage = st.session_state.get('stage', 'inicio')

if current_stage == 'inicio':
    vista_inicio()
elif current_stage == 'test_activo':
    vista_test_activo()
elif current_stage == 'resultados':
    vista_resultados()
else:
    # Fallback por si el estado es inválido
    st.error("Estado inválido de la aplicación. Reiniciando...")
    reiniciar_test()

# --- 8. EJECUCIÓN CONDICIONAL DEL SCROLL (FIX FINAL ROBUSTO) ---
# Se ejecuta al final, después de renderizar la vista, si la bandera está activa
if st.session_state.get('should_scroll', False):
    forzar_scroll_al_top() # Llama a la función que usa st.components.v1.html
    st.session_state.should_scroll = False # Desactiva la bandera para el próximo ciclo
