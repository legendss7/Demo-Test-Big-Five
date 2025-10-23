import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
import random
components.html('<div id="top-anchor"></div>', height=0)


from datetime import datetime
if "scroll_key" not in st.session_state:
    st.session_state.scroll_key = 0


# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(
    layout="wide", 
    page_title="Test Big Five (OCEAN) | Evaluación Profesional",
    page_icon="🧠"
)

# Ancla para scroll
components.html('<a id="top-anchor"></a>', height=0)


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
    return 6 - score

# 50 Preguntas del Big Five (10 por dimensión, 5 directas y 5 inversas)
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
if 'scroll_key' not in st.session_state:
    st.session_state.scroll_key = 0
if 'fecha_evaluacion' not in st.session_state:
    st.session_state.fecha_evaluacion = None

# --- 2. FUNCIONES DE SCROLL ---
def forzar_scroll_al_top():
    """Fuerza el scroll al inicio de la vista de forma segura (compatible con Streamlit Cloud)."""
    # Crear o actualizar la variable de control
    st.session_state.scroll_key = st.session_state.get("scroll_key", 0) + 1

    # Contenedor seguro para HTML (impide errores en Streamlit Cloud)
    placeholder = st.empty()

    js_code = """
        <script>
            window.addEventListener('load', function() {
                setTimeout(function() {
                    try {
                        const doc = window.parent?.document || document;
                        const anchor = doc.querySelector('#top-anchor');
                        if (anchor) {
                            anchor.scrollIntoView({ behavior: 'auto', block: 'start' });
                        } else {
                            const container = doc.querySelector('[data-testid="stAppViewContainer"]');
                            if (container) {
                                container.scrollTo({ top: 0, behavior: 'auto' });
                            } else {
                                window.scrollTo({ top: 0, behavior: 'auto' });
                            }
                        }
                    } catch (err) {
                        console.error('Scroll error:', err);
                    }
                }, 500);
            });
        </script>
    """

    # Renderizamos el script dentro de un contenedor temporal
    placeholder.html(js_code, height=0, key=f"scroll_{st.session_state.scroll_key}")


# --- 3. FUNCIONES DE CÁLCULO ---
def calcular_resultados(respuestas):
    """Calcula las puntuaciones de las 5 dimensiones (0-100)."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    
    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'])
        
        if respuesta is None:
            score = 3
        elif p['reverse']:
            score = reverse_score(respuesta)
        else:
            score = respuesta
            
        scores[p['dim']].append(score)
    
    resultados = {}
    for dim, score_list in scores.items():
        avg_score = np.mean(score_list)
        # Convertir de escala 1-5 a 0-100
        percent_score = ((avg_score - 1) / 4) * 100
        resultados[dim] = round(percent_score, 1)
    
    return resultados

def get_nivel_interpretacion(score):
    """Clasifica el puntaje y retorna nivel, color y etiqueta."""
    if score >= 75:
        return "Muy Alto", "#2a9d8f", "Dominante"
    elif score >= 60:
        return "Alto", "#264653", "Marcado"
    elif score >= 40:
        return "Promedio", "#e9c46a", "Moderado"
    elif score >= 25:
        return "Bajo", "#f4a261", "Suave"
    else:
        return "Muy Bajo", "#e76f51", "Mínimo"

# --- 4. FUNCIONES DE GRÁFICOS ---
def crear_grafico_radar(resultados):
    """Crea gráfico de radar del perfil."""
    categories = [DIMENSIONES[dim]['code'] + ' - ' + dim for dim in resultados.keys()]
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
    
    return fig

def crear_grafico_barras(resultados):
    """Crea gráfico de barras horizontales."""
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
            showscale=True,
            colorbar=dict(title="Puntuación", x=1.15)
        ),
        text=df['Puntuación'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Puntuación: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="Puntuaciones por Dimensión", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Puntuación (0-100)", range=[0, 110]),
        yaxis=dict(title=""),
        height=500,
        margin=dict(l=200),
        template="plotly_white"
    )
    
    return fig

def crear_grafico_comparativo(resultados):
    """Crea gráfico comparativo con la población promedio."""
    dimensiones = list(resultados.keys())
    tu_perfil = list(resultados.values())
    promedio = [50] * len(dimensiones)  # Población promedio = 50
    
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
        yaxis=dict(title="Puntuación (0-100)", range=[0, 110]),
        xaxis=dict(title=""),
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white"
    )
    
    return fig

# --- 5. FUNCIONES DE NAVEGACIÓN ---
def iniciar_test():
    """Inicia el test."""
    st.session_state.stage = 'test_activo'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None

def completar_al_azar():
    """Genera respuestas aleatorias."""
    st.session_state.respuestas = {p['key']: random.choice(LIKERT_OPTIONS) for p in PREGUNTAS}
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.stage = 'resultados'

def reiniciar_test():
    """Reinicia el test."""
    st.session_state.stage = 'inicio'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
    st.session_state.resultados = None

# --- 6. VISTAS ---
components.html('<a id="top-anchor"></a>', height=0)

def vista_inicio():
    """Vista de inicio."""
    forzar_scroll_al_top()
    
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
            st.rerun()
        
        st.markdown("---")
        
        st.caption("**Modo Demo:**")
        if st.button("🎲 Completar Aleatoriamente", type="secondary", use_container_width=True):
            completar_al_azar()
            st.rerun()

def vista_test_activo():
    """Vista del test activo."""
    forzar_scroll_al_top()
    
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
        
        respuestas_form = {}
        
        for i, p in enumerate(preguntas_dimension, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {p['text']}**")
                
                initial_value = st.session_state.respuestas.get(p['key'])
                initial_index = LIKERT_OPTIONS.index(initial_value) if initial_value is not None else None
                
                respuestas_form[p['key']] = st.radio(
                    label=f"Selecciona tu respuesta para: {p['text'][:30]}...",
                    options=LIKERT_OPTIONS,
                    format_func=lambda x: ESCALA_LIKERT[x],
                    index=initial_index,
                    key=f"radio_{p['key']}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
        
        st.markdown("---")
        
        if current_index == len(DIMENSIONES_LIST) - 1:
            button_label = "✅ Finalizar y Ver Resultados"
        else:
            next_dim = DIMENSIONES_LIST[current_index + 1]
            button_label = f"➡️ Continuar a: {next_dim}"
        
        submitted = st.form_submit_button(button_label, type="primary", use_container_width=True)
        
        if submitted:
            # Validar que todas estén respondidas
            todas_respondidas = all(v is not None for v in respuestas_form.values())
            
            if not todas_respondidas:
                st.error(f"⚠️ Por favor, responde todas las preguntas de esta dimensión antes de continuar.")
            else:
                # Guardar respuestas
                st.session_state.respuestas.update(respuestas_form)
                
                # Avanzar o finalizar
                if current_index < len(DIMENSIONES_LIST) - 1:
                    st.session_state.current_dimension_index += 1
                    st.rerun()
                else:
                    # Calcular resultados
                    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
                    st.session_state.fecha_evaluacion = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.session_state.stage = 'resultados'
                    st.rerun()

def vista_resultados():
    """Vista de resultados profesional."""
    forzar_scroll_al_top()
    
    resultados = st.session_state.resultados
    
    if resultados is None:
        st.warning("No hay resultados disponibles.")
        if st.button("Volver al Inicio"):
            reiniciar_test()
            st.rerun()
        return
    
    st.title("📊 Tu Informe de Personalidad Big Five")
    st.markdown(f"**Fecha de Evaluación:** {st.session_state.fecha_evaluacion}")
    st.markdown("---")
    
    # --- 1. RESUMEN EJECUTIVO ---
    st.header("1. 📈 Resumen Ejecutivo")
    
    promedio_total = np.mean(list(resultados.values()))
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%); 
                padding: 30px; border-radius: 15px; color: white; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-bottom: 30px;">
        <h2 style="margin: 0; font-size: 2.5em;">Puntuación Promedio: {promedio_total:.1f}/100</h2>
        <p style="margin: 15px 0 0 0; font-size: 1.2em; opacity: 0.9;">
            Perfil Equilibrado con Características Distintivas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 2. VISUALIZACIONES ---
    st.header("2. 📊 Visualización de tu Perfil")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Radar", "📊 Barras", "⚖️ Comparativo"])
    
    with tab1:
        st.plotly_chart(crear_grafico_radar(resultados), use_container_width=True)
        st.caption("Gráfico de radar mostrando tu perfil en las 5 dimensiones de personalidad.")
    
    with tab2:
        st.plotly_chart(crear_grafico_barras(resultados), use_container_width=True)
        st.caption("Puntuaciones ordenadas de menor a mayor.")
    
    with tab3:
        st.plotly_chart(crear_grafico_comparativo(resultados), use_container_width=True)
        st.caption("Comparación de tu perfil con el promedio poblacional (50 puntos).")
    
    st.markdown("---")
    
    # --- 3. ANÁLISIS DETALLADO ---
    st.header("3. 🔍 Análisis Detallado por Dimensión")
    
    for dim_name in DIMENSIONES_LIST:
        score = resultados[dim_name]
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
                    title={'text': f"{dim_info['code']}", 'font': {'size': 24}},
                    number={'font': {'size': 40}},
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
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': score
                        }
                    }
                ))
                fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.markdown(f"**Descripción:**")
                st.markdown(dim_info['desc'])
                
                st.markdown(f"**Nivel:** <span style='color:{color}; font-weight: bold; font-size: 1.2em;'>{nivel} ({etiqueta})</span>", unsafe_allow_html=True)
                
                if score >= 60:
                    st.success(f"✅ **Puntuación Alta**")
                    st.markdown(f"**Características destacadas:** {dim_info['caracteristicas_altas']}")
                elif score >= 40:
                    st.info(f"ℹ️ **Puntuación Media**")
                    st.markdown("Tu puntuación se encuentra en el rango promedio, mostrando un equilibrio en esta dimensión.")
                else:
                    st.warning(f"⚠️ **Puntuación Baja**")
                    st.markdown(f"**Características destacadas:** {dim_info['caracteristicas_bajas']}")
            
            st.markdown("---")
            
            # Interpretación profesional específica
            st.markdown("**💼 Implicaciones Profesionales:**")
            
            if dim_name == "Apertura a la Experiencia":
                if score >= 60:
                    st.markdown("""
                    - ✅ **Idóneo para:** Innovación, I+D, Diseño Creativo, Estrategia, Consultoría
                    - Excelente adaptabilidad a cambios y entornos dinámicos
                    - Alta capacidad para generar ideas originales y soluciones novedosas
                    """)
                elif score <= 40:
                    st.markdown("""
                    - ✅ **Idóneo para:** Roles con procedimientos establecidos, Operaciones, Manufactura
                    - Preferencia por entornos estructurados y predecibles
                    - ⚠️ Puede requerir apoyo en contextos de alta incertidumbre
                    """)
                else:
                    st.markdown("""
                    - ✅ **Perfil versátil:** Balance entre creatividad y pragmatismo
                    - Apto para roles que combinen innovación con procesos estructurados
                    """)
            
            elif dim_name == "Responsabilidad":
                if score >= 60:
                    st.markdown("""
                    - ✅ **Idóneo para:** Gestión de Proyectos, Auditoría, Control de Calidad, Finanzas
                    - Excelente autogestión y cumplimiento de plazos
                    - Alta confiabilidad y atención al detalle
                    """)
                elif score <= 40:
                    st.markdown("""
                    - ✅ **Idóneo para:** Roles creativos con flexibilidad, Trabajo por proyectos cortos
                    - Mayor espontaneidad y adaptabilidad
                    - ⚠️ Puede necesitar estructura externa y seguimiento
                    """)
                else:
                    st.markdown("""
                    - ✅ **Perfil equilibrado:** Capaz de ser disciplinado cuando es necesario
                    - Apto para la mayoría de roles con supervisión moderada
                    """)
            
            elif dim_name == "Extraversión":
                if score >= 60:
                    st.markdown("""
                    - ✅ **Idóneo para:** Ventas, Liderazgo de Equipos, Relaciones Públicas, Networking
                    - Prospera en ambientes sociales y roles de alta interacción
                    - Excelente para posiciones que requieren influenciar a otros
                    """)
                elif score <= 40:
                    st.markdown("""
                    - ✅ **Idóneo para:** Análisis, Investigación, Programación, Roles Técnicos
                    - Mayor concentración en trabajo individual
                    - Preferencia por comunicación escrita sobre oral
                    """)
                else:
                    st.markdown("""
                    - ✅ **Perfil ambivertido:** Adaptable a trabajo en equipo y solitario
                    - Versatilidad en diferentes contextos sociales
                    """)
            
            elif dim_name == "Amabilidad":
                if score >= 60:
                    st.markdown("""
                    - ✅ **Idóneo para:** Recursos Humanos, Servicio al Cliente, Mediación, Trabajo Social
                    - Excelente para crear ambientes colaborativos
                    - Alta capacidad de empatía y resolución de conflictos
                    """)
                elif score <= 40:
                    st.markdown("""
                    - ✅ **Idóneo para:** Negociación, Roles competitivos, Toma de decisiones difíciles
                    - Mayor objetividad en situaciones complejas
                    - Capacidad para tomar decisiones impopulares cuando es necesario
                    """)
                else:
                    st.markdown("""
                    - ✅ **Perfil equilibrado:** Balance entre empatía y objetividad
                    - Apto para roles que requieran diplomacia y firmeza
                    """)
            
            elif dim_name == "Estabilidad Emocional":
                if score >= 60:
                    st.markdown("""
                    - ✅ **Idóneo para:** Gestión de Crisis, Operaciones de Alto Estrés, Liderazgo Ejecutivo
                    - Excelente resiliencia y manejo del estrés
                    - Capacidad para mantener la calma bajo presión
                    """)
                elif score <= 40:
                    st.markdown("""
                    - ✅ **Idóneo para:** Roles con ambiente predecible y bajo estrés
                    - Mayor sensibilidad emocional (puede ser ventajoso en roles creativos)
                    - ⚠️ Puede requerir apoyo en situaciones de alta presión
                    """)
                else:
                    st.markdown("""
                    - ✅ **Perfil normal:** Gestión emocional adecuada
                    - Apto para la mayoría de contextos laborales
                    """)
    
    st.markdown("---")
    
    # --- 4. FORTALEZAS Y ÁREAS DE DESARROLLO ---
    st.header("4. 💪 Fortalezas y Áreas de Desarrollo")
    
    col_fort, col_des = st.columns(2)
    
    # Top 3 fortalezas
    sorted_dims = sorted(resultados.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_dims[:3]
    bottom_3 = sorted_dims[-3:]
    
    with col_fort:
        st.subheader("🌟 Tus 3 Principales Fortalezas")
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
        st.subheader("📈 Áreas de Desarrollo")
        for i, (dim, score) in enumerate(bottom_3, 1):
            icon = DIMENSIONES[dim]['icon']
            nivel, _, _ = get_nivel_interpretacion(score)
            
            if score < 40:
                st.markdown(f"""
                **{i}. {icon} {dim}**
                - Puntuación: **{score:.1f}**/100 ({nivel})
                - Considerar desarrollo si es relevante para tus objetivos
                """)
            else:
                st.markdown(f"""
                **{i}. {icon} {dim}**
                - Puntuación: **{score:.1f}**/100 ({nivel})
                - Nivel adecuado, sin necesidad crítica de desarrollo
                """)
            st.progress(score / 100)
            st.markdown("")
    
    st.markdown("---")
    
    # --- 5. TABLA DE RESULTADOS ---
    st.header("5. 📋 Tabla Resumen de Resultados")
    
    df_resultados = pd.DataFrame({
        'Dimensión': [dim for dim in resultados.keys()],
        'Código': [DIMENSIONES[dim]['code'] for dim in resultados.keys()],
        'Puntuación': [f"{score:.1f}" for score in resultados.values()],
        'Nivel': [get_nivel_interpretacion(score)[0] for score in resultados.values()],
        'Etiqueta': [get_nivel_interpretacion(score)[2] for score in resultados.values()]
    })
    
    # Aplicar estilos
    def color_nivel(val):
        try:
            score = float(val)
            if score >= 75:
                return 'background-color: #c3e6cb; color: #155724; font-weight: bold;'
            elif score >= 60:
                return 'background-color: #d4edda; color: #155724;'
            elif score >= 40:
                return 'background-color: #d1ecf1; color: #0c5460;'
            elif score >= 25:
                return 'background-color: #fff3cd; color: #856404;'
            else:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        except:
            return ''
    
    styled_df = df_resultados.style.applymap(color_nivel, subset=['Puntuación'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- 6. RECOMENDACIONES PROFESIONALES ---
    st.header("6. 💼 Recomendaciones Profesionales")
    
    # Análisis de perfil dominante
    perfil_dominante = max(resultados.items(), key=lambda x: x[1])
    dim_dominante, score_dominante = perfil_dominante
    
    st.subheader(f"🎯 Perfil Dominante: {DIMENSIONES[dim_dominante]['icon']} {dim_dominante}")
    
    st.markdown(f"""
    Tu dimensión más destacada es **{dim_dominante}** con una puntuación de **{score_dominante:.1f}/100**.
    Esto sugiere que tu perfil está especialmente orientado hacia características de {dim_dominante.lower()}.
    """)
    
    # Recomendaciones basadas en el perfil
    st.markdown("### 📌 Roles Profesionales Sugeridos:")
    
    roles_recomendados = []
    
    if resultados["Apertura a la Experiencia"] >= 60 and resultados["Responsabilidad"] >= 60:
        roles_recomendados.append("**Consultor Estratégico** - Combina creatividad con disciplina")
    
    if resultados["Extraversión"] >= 60 and resultados["Amabilidad"] >= 60:
        roles_recomendados.append("**Gerente de Recursos Humanos** - Sociable y empático")
    
    if resultados["Responsabilidad"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        roles_recomendados.append("**Director de Proyectos** - Organizado y resiliente")
    
    if resultados["Apertura a la Experiencia"] >= 60 and resultados["Extraversión"] <= 40:
        roles_recomendados.append("**Investigador/Analista** - Creativo e independiente")
    
    if resultados["Amabilidad"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        roles_recomendados.append("**Coach o Mentor** - Empático y estable")
    
    if resultados["Extraversión"] >= 60 and resultados["Estabilidad Emocional"] >= 60:
        roles_recomendados.append("**Director Comercial** - Sociable y maneja presión")
    
    if resultados["Responsabilidad"] >= 60 and resultados["Apertura a la Experiencia"] <= 40:
        roles_recomendados.append("**Gerente de Operaciones** - Disciplinado y orientado a procesos")
    
    if not roles_recomendados:
        roles_recomendados.append("**Perfil Versátil** - Apto para diversos roles según intereses")
    
    for rol in roles_recomendados:
        st.markdown(f"- {rol}")
    
    st.markdown("---")
    
    # --- 7. INTERPRETACIÓN CIENTÍFICA ---
    with st.expander("📚 **Sobre el Modelo Big Five**", expanded=False):
        st.markdown("""
        ### El Modelo de los Cinco Grandes (Big Five)
        
        El modelo Big Five, también conocido como OCEAN, es el marco de personalidad más respaldado 
        por la investigación científica en psicología. Se basa en décadas de estudios empíricos y 
        ha demostrado ser válido en múltiples culturas y contextos.
        
        **Las Cinco Dimensiones:**
        
        1. **Apertura a la Experiencia (O)**: Refleja la tendencia a ser imaginativo, curioso y abierto 
           a nuevas experiencias versus práctico y convencional.
        
        2. **Responsabilidad (C)**: Mide el grado de organización, disciplina y orientación a objetivos 
           versus espontaneidad y flexibilidad.
        
        3. **Extraversión (E)**: Indica la tendencia hacia la sociabilidad, asertividad y búsqueda de 
           estimulación social versus reserva y preferencia por la soledad.
        
        4. **Amabilidad (A)**: Refleja cooperación, empatía y confianza versus competitividad, 
           escepticismo y objetividad.
        
        5. **Estabilidad Emocional (N)**: Mide la capacidad de mantener la calma y gestionar el estrés 
           versus sensibilidad emocional y reactividad.
        
        **Aplicaciones:**
        - Orientación vocacional y desarrollo profesional
        - Selección de personal y evaluación de ajuste cultural
        - Desarrollo personal y autoconocimiento
        - Coaching y mentoring
        - Investigación en psicología organizacional
        
        **Nota Importante:** Este test es una herramienta de autoexploración y orientación. Para 
        evaluaciones formales en contextos de selección o clínicos, se recomienda utilizar 
        instrumentos estandarizados administrados por profesionales cualificados.
        """)
    
    st.markdown("---")
    
    # --- 8. EXPORTAR Y ACCIONES ---
    st.header("7. 📥 Exportar Resultados")
    
    col_download, col_reiniciar = st.columns(2)
    
    with col_download:
        # Preparar CSV
        csv_data = df_resultados.to_csv(index=False)
        
        st.download_button(
            label="📊 Descargar Resultados (CSV)",
            data=csv_data,
            file_name=f"BigFive_Resultados_{st.session_state.fecha_evaluacion.replace('/', '-').replace(' ', '_').replace(':', '-')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_reiniciar:
        if st.button("🔄 Realizar Nueva Evaluación", type="primary", use_container_width=True):
            reiniciar_test()
            st.rerun()
    
    st.markdown("---")
    
    # Disclaimer
    st.info("""
    **Disclaimer:** Los resultados de este test son orientativos y están basados en tus respuestas 
    autorreportadas. La personalidad es compleja y multidimensional. Este test proporciona una 
    aproximación general a tu perfil, pero no reemplaza una evaluación profesional completa.
    """)

# --- 7. FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    components.html('<a id="top-anchor"></a>', height=0)

    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 8. FOOTER ---
st.markdown("---")
st.markdown("""
<p style='text-align: center; font-size: 0.9em; color: #666; padding: 20px 0;'>
    🧠 <strong>Test Big Five (OCEAN)</strong> - Evaluación de Personalidad Profesional<br>
    Basado en el modelo científico de los Cinco Grandes Factores de Personalidad<br>
    © 2025 - Herramienta educativa y de orientación | No reemplaza evaluación profesional
</p>
""", unsafe_allow_html=True)


