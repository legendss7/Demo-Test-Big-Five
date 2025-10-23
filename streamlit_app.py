import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Evaluación Big Five | Perfil Corporativo")

# Definición de las dimensiones del Big Five y colores (Paleta Corporativa)
DIMENSIONES = {
    "Apertura a la Experiencia (O)": {"code": "O", "color": "#0077b6", "icon": "💡", "desc": "Imaginación, curiosidad intelectual, aprecio por el arte."},
    "Responsabilidad (C)": {"code": "C", "color": "#00b4d8", "icon": "🎯", "desc": "Autodisciplina, cumplimiento de objetivos, sentido del deber."},
    "Extraversión (E)": {"code": "E", "color": "#48cae4", "icon": "🗣️", "desc": "Sociabilidad, asertividad, búsqueda de estimulación externa."},
    "Amabilidad (A)": {"code": "A", "color": "#90e0ef", "icon": "🤝", "desc": "Cooperación, compasión, respeto por los demás y confianza."},
    "Neuroticismo (N)": {"code": "N", "color": "#0096c7", "icon": "😟", "desc": "Tendencia a experimentar emociones desagradables como la ansiedad, el enfado o la depresión."},
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

# Escala Likert de respuesta
ESCALA_LIKERT = {
    5: "Totalmente de acuerdo (5)",
    4: "De acuerdo (4)",
    3: "Neutral (3)",
    2: "En desacuerdo (2)",
    1: "Totalmente en desacuerdo (1)",
}
LIKERT_OPTIONS = list(ESCALA_LIKERT.keys())
# La codificación inversa (R) es crucial
def reverse_score(score):
    return 6 - score

# 25 Preguntas de ejemplo (5 por dimensión)
PREGUNTAS = [
    # O - Apertura (2 Inversas, 3 Directas)
    {"text": "Disfruto con los retos intelectuales complejos.", "dim": "Apertura a la Experiencia (O)", "key": "O1", "reverse": False},
    {"text": "Tengo una imaginación muy activa.", "dim": "Apertura a la Experiencia (O)", "key": "O2", "reverse": False},
    {"text": "Me aburren las discusiones sobre arte o filosofía.", "dim": "Apertura a la Experiencia (O)", "key": "O3", "reverse": True},
    {"text": "Prefiero la rutina a probar cosas nuevas.", "dim": "Apertura a la Experiencia (O)", "key": "O4", "reverse": True},
    {"text": "Me gusta visitar exposiciones y museos.", "dim": "Apertura a la Experiencia (O)", "key": "O5", "reverse": False},
    
    # C - Responsabilidad (2 Inversas, 3 Directas)
    {"text": "Siempre estoy bien preparado.", "dim": "Responsabilidad (C)", "key": "C1", "reverse": False},
    {"text": "Soy minucioso y presto atención a los detalles.", "dim": "Responsabilidad (C)", "key": "C2", "reverse": False},
    {"text": "Dejo mis pertenencias tiradas por ahí.", "dim": "Responsabilidad (C)", "key": "C3", "reverse": True},
    {"text": "Me distraigo fácilmente y evito mis deberes.", "dim": "Responsabilidad (C)", "key": "C4", "reverse": True},
    {"text": "Sigo una planificación y cumplo mis compromisos.", "dim": "Responsabilidad (C)", "key": "C5", "reverse": False},
    
    # E - Extraversión (2 Inversas, 3 Directas)
    {"text": "Soy el alma de la fiesta y hablo mucho.", "dim": "Extraversión (E)", "key": "E1", "reverse": False},
    {"text": "Me siento cómodo interactuando con desconocidos.", "dim": "Extraversión (E)", "key": "E2", "reverse": False},
    {"text": "Me gusta pasar tiempo a solas y soy reservado.", "dim": "Extraversión (E)", "key": "E3", "reverse": True},
    {"text": "Tengo dificultades para expresarme en grandes grupos.", "dim": "Extraversión (E)", "key": "E4", "reverse": True},
    {"text": "Aporto energía y entusiasmo a mis actividades.", "dim": "Extraversión (E)", "key": "E5", "reverse": False},
    
    # A - Amabilidad (2 Inversas, 3 Directas)
    {"text": "Simpatizo fácilmente con los sentimientos de los demás.", "dim": "Amabilidad (A)", "key": "A1", "reverse": False},
    {"text": "Me preocupo por el bienestar de los demás.", "dim": "Amabilidad (A)", "key": "A2", "reverse": False},
    {"text": "No me interesa realmente la gente.", "dim": "Amabilidad (A)", "key": "A3", "reverse": True},
    {"text": "Soy cínico y escéptico respecto a las intenciones ajenas.", "dim": "Amabilidad (A)", "key": "A4", "reverse": True},
    {"text": "Soy considerado y trato a los demás con respeto.", "dim": "Amabilidad (A)", "key": "A5", "reverse": False},
    
    # N - Neuroticismo (2 Inversas, 3 Directas) - Más alto el score, más neurótico
    {"text": "Me preocupo mucho por las cosas triviales.", "dim": "Neuroticismo (N)", "key": "N1", "reverse": False},
    {"text": "Me irrito fácilmente.", "dim": "Neuroticismo (N)", "key": "N2", "reverse": False},
    {"text": "Me siento seguro y satisfecho conmigo mismo.", "dim": "Neuroticismo (N)", "key": "N3", "reverse": True}, # Neuroticismo bajo = Sentirse seguro
    {"text": "Soy emocionalmente estable y difícilmente me altero.", "dim": "Neuroticismo (N)", "key": "N4", "reverse": True}, # Neuroticismo bajo = Estable
    {"text": "A veces me siento indefenso y tengo pánico.", "dim": "Neuroticismo (N)", "key": "N5", "reverse": False},
]

# Inicialización del estado de la sesión
if 'stage' not in st.session_state:
    st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

# --- 2. FUNCIONES DE LÓGICA Y ANÁLISIS ---

def calcular_resultados(respuestas):
    """Calcula las puntuaciones promedio de las 5 dimensiones (Escala 0-100)."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    
    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'])
        
        # Si no fue respondida, se asume neutral (3). Esto no debería pasar si la validación funciona.
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
        # Escala de 1 a 5 (promedio). Se normaliza a 0-100.
        percent_score = ((avg_score - 1) / 4) * 100
        resultados[dim] = round(percent_score)
        
    return resultados

def get_nivel_interpretacion(score):
    """Clasifica el puntaje y retorna un nivel de texto y color corporativo."""
    if score >= 75: 
        return "Muy Alto", "#2a9d8f", "Dominante"
    elif score >= 60: 
        return "Alto", "#264653", "Marcado"
    elif score >= 40: 
        return "Promedio", "#e9c46a", "Moderado"
    elif score >= 25: 
        return "Bajo", "#f4a261", "Suave"
    else: 
        return "Muy Bajo", "#e76f51", "Recesivo"

def get_recomendaciones(dim, score):
    """Genera recomendaciones profesionales específicas por dimensión y nivel."""
    nivel_map = get_nivel_interpretacion(score)[0]
    
    rec = {
        "Apertura a la Experiencia (O)": {
            "Muy Alto": "Fomentar roles de **innovación, I+D y diseño estratégico**. Se adaptará bien a cambios y proyectos creativos.",
            "Bajo": "Ubicar en tareas con **procedimientos claros y poca ambigüedad**. Puede requerir entrenamiento para manejar el cambio o nuevas tecnologías.",
            "Promedio": "Apto para roles que requieren un balance entre **estabilidad y creatividad**. Fomentar la participación en grupos de mejora continua.",
        },
        "Responsabilidad (C)": {
            "Muy Alto": "Asignar funciones de **auditoría, gestión de proyectos y roles críticos** donde la precisión es vital. Excelente autogestión.",
            "Bajo": "Evitar roles que demanden alta autonomía en la planificación. Necesita **seguimiento estructurado y objetivos a corto plazo**.",
            "Promedio": "Capaz de mantener la **disciplina en roles definidos**. Potenciar con herramientas de planificación y gestión del tiempo.",
        },
        "Extraversión (E)": {
            "Muy Alto": "Ideal para **ventas, liderazgo de equipos y networking corporativo**. Prospera en ambientes sociales y le gusta influir.",
            "Bajo": "Apto para roles de **análisis profundo, desarrollo individual y especialistas técnicos**. Requiere un ambiente de trabajo tranquilo y enfocado.",
            "Promedio": "Perfil **adaptable**; puede funcionar bien en equipos y en tareas solitarias. Entrenar en habilidades de presentación y comunicación.",
        },
        "Amabilidad (A)": {
            "Muy Alto": "Excelente para **recursos humanos, servicio al cliente y resolución de conflictos**. Promueve un clima laboral positivo.",
            "Bajo": "Ubicar en posiciones que requieran **negociación dura o toma de decisiones complejas** sin sesgo emocional. Puede tener dificultades en la cohesión de equipos.",
            "Promedio": "Buen colaborador. Fomentar el **liderazgo servicial y la mediación** en situaciones grupales.",
        },
        "Neuroticismo (N)": {
            "Muy Alto": "Requiere **soporte de bienestar emocional y un ambiente laboral de baja presión**. Evaluar el impacto del estrés en el rendimiento.",
            "Bajo": "Es un perfil **resiliente y estable**. Ideal para roles bajo presión constante (ej. operaciones críticas, manejo de crisis).",
            "Promedio": "Muestra **buena gestión emocional, pero puede fluctuar**. Ofrecer talleres de manejo de estrés preventivo.",
        },
    }
    
    # Intenta obtener la recomendación específica, si no, usa la recomendación general.
    return rec[dim].get(nivel_map, rec[dim].get("Promedio", "Desarrollar un plan de acción basado en las fortalezas y oportunidades en esta dimensión."))

def procesar_y_mostrar_resultados():
    """Valida, calcula los resultados y simula el proceso con animación."""
    
    # Validación: Asegurarse de que todas las preguntas fueron respondidas
    if None in st.session_state.respuestas.values():
        st.error("🚨 Debe responder todas las 25 preguntas antes de finalizar el test.")
        return
        
    # Animación Corporativa
    st.markdown("""
        <style>
            .stSpinner > div > div {
                border-top-color: #0096c7; /* Color primario */
                border-right-color: #0077b6;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.spinner('Procesando datos y generando perfil de competencias...'):
        time.sleep(3) # Simular procesamiento
    
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.stage = 'resultados'
    st.rerun() # CORRECCIÓN: Usar st.rerun()

def iniciar_test():
    """Inicia la fase de test y reinicia las respuestas."""
    st.session_state.stage = 'test'
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS} 
    st.session_state.resultados = None
    st.rerun() # CORRECCIÓN: Usar st.rerun()

def reiniciar_test():
    """Reinicia la aplicación a la vista de inicio."""
    st.session_state.stage = 'inicio'
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS} 
    st.session_state.resultados = None
    st.rerun() # CORRECCIÓN: Usar st.rerun()

# --- 3. FUNCIONES DE VISUALIZACIÓN ---

def crear_grafico_radar(resultados):
    """Crea un gráfico de radar interactivo con estilo corporativo."""
    categories = list(resultados.keys())
    values = list(resultados.values())
    
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Tu Perfil',
                line_color=DIMENSIONES["Responsabilidad (C)"]["color"],
                fillcolor='rgba(0, 119, 182, 0.2)',
                marker=dict(size=10, symbol="circle", color=DIMENSIONES["Extraversión (E)"]["color"]),
            )
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[0, 25, 50, 75, 100],
                    ticktext=["0", "Bajo", "Promedio", "Alto", "100"],
                    linecolor="#cccccc"
                ),
                angularaxis=dict(
                    linecolor="#cccccc",
                    rotation=90,
                    direction="clockwise"
                ),
            ),
            showlegend=False,
            height=500,
            template="simple_white",
            hovermode="closest",
        )
    )
    fig.update_traces(hovertemplate='<b>%{theta}</b>: %{r} puntos<extra></extra>')
    
    return fig

# --- 4. VISTAS DE LA APLICACIÓN ---

def vista_inicio():
    st.title("💼 Plataforma de Evaluación Big Five (OCEAN)")
    st.markdown("### Perfil de Competencias y Potencial Profesional")

    col_info, col_start = st.columns([2, 1])
    
    with col_info:
        st.info("Este demo evalúa los **Cinco Grandes factores de personalidad**, esenciales para la selección de personal y el desarrollo profesional. El resultado es un perfil detallado de tus tendencias de comportamiento.")
        st.markdown(f"""
        <div style="border: 1px solid #0077b6; padding: 15px; border-radius: 8px; background-color: #e6f7ff;">
            <p style="font-weight: bold; color: #0077b6;">El test consta de 25 preguntas independientes (5 por dimensión).</p>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>{DIMENSIONES['Apertura a la Experiencia (O)']['icon']} Apertura a la Experiencia (O)</li>
                <li>{DIMENSIONES['Responsabilidad (C)']['icon']} Responsabilidad (C)</li>
                <li>{DIMENSIONES['Extraversión (E)']['icon']} Extraversión (E)</li>
                <li>{DIMENSIONES['Amabilidad (A)']['icon']} Amabilidad (A)</li>
                <li>{DIMENSIONES['Neuroticismo (N)']['icon']} Neuroticismo (N)</li>
            </ul>
            <p>Responda de forma honesta, sin un tiempo límite.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_start:
        st.subheader("Listo para comenzar?")
        # Botón con estilo corporativo
        st.markdown(f"""
        <style>
            .stButton>button {{
                background-color: #0096c7;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
                transition: background-color 0.3s ease;
                width: 100%;
            }}
            .stButton>button:hover {{
                background-color: #0077b6;
            }}
        </style>
        """, unsafe_allow_html=True)
        st.button("🚀 Iniciar Evaluación Profesional", type="primary", key="btn_inicio", on_click=iniciar_test)

def vista_test():
    st.title("📝 Evaluación Big Five: Cuestionario")
    st.markdown("Por favor, seleccione qué tan de acuerdo está con cada afirmación. Use la escala de **1 (Totalmente en desacuerdo)** a **5 (Totalmente de acuerdo)**.")
    st.markdown("---")
    
    # Contador de preguntas y barra de progreso
    respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None)
    total_preguntas = len(PREGUNTAS)
    progreso = respondidas / total_preguntas
    
    # Barra de progreso con color corporativo
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 10px;">
        Progreso: <b>{respondidas}</b> de <b>{total_preguntas}</b> preguntas respondidas.
    </div>
    """, unsafe_allow_html=True)
    st.progress(progreso)

    # Usamos un formulario para enviar todas las respuestas juntas y forzar la validación
    with st.form("big_five_form"):
        
        current_dim = ""
        for i, p in enumerate(PREGUNTAS):
            
            if p['dim'] != current_dim:
                current_dim = p['dim']
                dim_info = DIMENSIONES[current_dim]
                st.subheader(f"{dim_info['icon']} Sección: {current_dim}")
            
            # Contenedor para cada pregunta con borde sutil
            with st.container(border=True):
                col_num, col_text = st.columns([0.5, 9.5])
                
                with col_num:
                    st.markdown(f"**{i+1}.**")
                
                with col_text:
                    st.markdown(f"**Afirmación:** {p['text']}")
                    
                    # Usar st.radio para la selección de respuesta
                    respuesta_key = f"radio_{p['key']}"
                    
                    # Busca la selección actual para el índice. Si es None, el índice debe ser None.
                    initial_value = st.session_state.respuestas.get(p['key'])
                    
                    st.session_state.respuestas[p['key']] = st.radio(
                        label=f"Respuesta para la pregunta {i+1}",
                        options=LIKERT_OPTIONS,
                        format_func=lambda x: ESCALA_LIKERT[x],
                        index=LIKERT_OPTIONS.index(initial_value) if initial_value is not None else None,
                        key=respuesta_key,
                        horizontal=True,
                        label_visibility="collapsed"
                    )
            
        st.markdown("---")
        st.form_submit_button("✅ Finalizar Evaluación y Generar Perfil", type="primary", use_container_width=True, on_click=procesar_y_mostrar_resultados)


def vista_resultados():
    st.title("📄 Informe de Perfil Big Five (Corporativo)")
    st.markdown("### Análisis de Tendencias de Comportamiento")
    
    resultados = st.session_state.resultados
    
    # --- 1. Resumen Ejecutivo del Perfil ---
    st.header("1. Resumen Ejecutivo del Perfil")
    
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.subheader("1.1 Visualización de Tendencias")
        fig = crear_grafico_radar(resultados)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_table:
        st.subheader("1.2 Puntuación por Dimensión")
        
        data_resumen = []
        for dim in DIMENSIONES_LIST:
            score = resultados[dim]
            nivel, color_hex, tag = get_nivel_interpretacion(score)
            data_resumen.append({
                "Dimensión": dim,
                "Puntuación (0-100)": score,
                "Nivel": nivel,
                "Etiqueta": tag,
                "Descripción": DIMENSIONES[dim]["desc"]
            })
            
        df_resumen = pd.DataFrame(data_resumen)
        
        # Estilo para colorear las celdas según el nivel
        def color_score(s):
            styles = []
            for score in s:
                nivel, color_hex, tag = get_nivel_interpretacion(score)
                # Solo colorear Alto y Muy Alto (verde) o Bajo y Muy Bajo (rojo/naranja)
                if score >= 60:
                    styles.append('background-color: #2a9d8f; color: white; font-weight: bold;')
                elif score <= 40:
                    styles.append('background-color: #e76f51; color: white; font-weight: bold;')
                else:
                    styles.append('')
            return styles
        
        st.dataframe(
            df_resumen[['Dimensión', 'Puntuación (0-100)', 'Nivel', 'Etiqueta']].style.apply(
                color_score, subset=['Puntuación (0-100)'], axis=0
            ),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # --- 2. Análisis Detallado y Recomendaciones (Plan de Desarrollo) ---
    st.header("2. Análisis Detallado y Plan de Desarrollo Recomendado")
    
    for dim in DIMENSIONES_LIST:
        score = resultados[dim]
        nivel, color_hex, tag = get_nivel_interpretacion(score)
        
        with st.expander(f"**{DIMENSIONES[dim]['icon']} {dim}: Nivel {nivel} ({score} puntos)**", expanded=True):
            
            col_desc, col_rec = st.columns([1, 1])

            with col_desc:
                st.markdown(f"**Tendencia General:** {DIMENSIONES[dim]['desc']}")
                st.markdown(f"**Clasificación:** <span style='color:{color_hex}; font-weight: bold;'>{nivel} ({tag})</span>", unsafe_allow_html=True)
                
            with col_rec:
                # Recomendaciones de rol/desarrollo
                st.subheader("Recomendación Profesional")
                rec = get_recomendaciones(dim, score)
                st.success(rec)
            
            st.markdown("---")
            
    st.button("🔄 Realizar Nueva Evaluación", type="secondary", on_click=reiniciar_test)


# --- 5. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test':
    vista_test()
elif st.session_state.stage == 'resultados':
    vista_resultados()
