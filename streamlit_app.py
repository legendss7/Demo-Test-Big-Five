import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import streamlit.components.v1 as components 
import random 

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="Evaluación Big Five | Perfil Corporativo")

# Colocamos un ancla invisible al inicio de la página para referencia (necesario para el scroll forzado)
st.html('<a id="top-anchor"></a>')

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

def reverse_score(score):
    """Calcula el puntaje inverso para preguntas negativas."""
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
    
    # N - Neuroticismo (2 Inversas, 3 Directas)
    {"text": "Me preocupo mucho por las cosas triviales.", "dim": "Neuroticismo (N)", "key": "N1", "reverse": False},
    {"text": "Me irrito fácilmente.", "dim": "Neuroticismo (N)", "key": "N2", "reverse": False},
    {"text": "Me siento seguro y satisfecho conmigo mismo.", "dim": "Neuroticismo (N)", "key": "N3", "reverse": True}, 
    {"text": "Soy emocionalmente estable y difícilmente me altero.", "dim": "Neuroticismo (N)", "key": "N4", "reverse": True}, 
    {"text": "A veces me siento indefenso y tengo pánico.", "dim": "Neuroticismo (N)", "key": "N5", "reverse": False},
]

# Inicialización del estado de la sesión
if 'stage' not in st.session_state:
    st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS}
if 'resultados' not in st.session_state:
    st.session_state.resultados = None
if 'current_dimension_index' not in st.session_state:
    st.session_state.current_dimension_index = 0
# Bandera de scroll
if 'should_scroll' not in st.session_state:
    st.session_state.should_scroll = False

# --- 2. FUNCIONES DE LÓGICA Y ANÁLISIS ---

def forzar_scroll_al_top():
    """Función MAXIMAMENTE FORZADA para el scroll al top (SIN KEY DINÁMICA para evitar TypeError)."""
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
            }, 250); 
        </script>
        """
    # Se usa una clave estática para evitar el TypeError
    st.components.v1.html(js_code, height=0, scrolling=False, key="static_scroll_comp") 

def calcular_resultados(respuestas):
    """Calcula las puntuaciones promedio de las 5 dimensiones (Escala 0-100)."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    
    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'])
        
        if respuesta is None: score = 3 
        elif p['reverse']: score = reverse_score(respuesta) 
        else: score = respuesta
            
        scores[p['dim']].append(score)
        
    resultados = {}
    for dim, score_list in scores.items():
        avg_score = np.mean(score_list)
        percent_score = ((avg_score - 1) / 4) * 100
        resultados[dim] = round(percent_score)
        
    return resultados

def get_nivel_interpretacion(score):
    """Clasifica el puntaje y retorna un nivel de texto y color corporativo."""
    if score >= 75: return "Muy Alto", "#2a9d8f", "Dominante"
    elif score >= 60: return "Alto", "#264653", "Marcado"
    elif score >= 40: return "Promedio", "#e9c46a", "Moderado"
    elif score >= 25: return "Bajo", "#f4a261", "Suave"
    else: return "Muy Bajo", "#e76f51", "Recesivo"

def get_recomendaciones(dim, score):
    """Genera recomendaciones profesionales específicas por dimensión y nivel, indicando aptitud."""
    nivel_map = get_nivel_interpretacion(score)[0]
    
    rec = {
        "Apertura a la Experiencia (O)": {
            "Muy Alto": "**Idóneo** para Innovación, I+D y Diseño Estratégico. Se adaptará bien a cambios constantes. **Apto para roles creativos y de estrategia.**", 
            "Bajo": "**No Idóneo** para roles de innovación disruptiva. Es apto para tareas con procedimientos claros y poca ambigüedad.", 
            "Promedio": "Apto para roles que requieren un balance entre estabilidad y creatividad."
        },
        "Responsabilidad (C)": {
            "Muy Alto": "**Idóneo** para Gerencia de Proyectos, Auditoría y roles críticos. Demuestra excelente autogestión. **Apto para roles de precisión y control.**", 
            "Bajo": "**No Idóneo** para Contraloría/Auditoría. Necesita seguimiento estructurado y objetivos a corto plazo.", 
            "Promedio": "Capaz de mantener la disciplina en roles definidos."
        },
        "Extraversión (E)": {
            "Muy Alto": "**Idóneo** para Dirección Comercial, Liderazgo de Equipos y Networking. Prospera en ambientes sociales. **Apto para roles de alta interacción.**", 
            "Bajo": "**No Idóneo** para Representante de Marca (PR) o Ventas de Campo. Es apto para roles de análisis profundo y especialistas técnicos.", 
            "Promedio": "Perfil adaptable; buen desempeño en equipos y tareas solitarias."
        },
        "Amabilidad (A)": {
            "Muy Alto": "**Idóneo** para Gerencia de RR.HH., Servicio al Cliente y Mediación. Promueve un clima laboral positivo. **Apto para roles de soporte y cohesión.**", 
            "Bajo": "**No Idóneo** para Soporte al Cliente o RR.HH. Es apto para posiciones que requieran negociación dura sin sesgo emocional.", 
            "Promedio": "Buen colaborador. Fomentar el liderazgo servicial."
        },
        "Neuroticismo (N)": {
            "Muy Alto": "**No Idóneo** para Operaciones de Crisis o manejo de alto estrés. Requiere un ambiente laboral de baja presión.", 
            "Bajo": "**Idóneo** para Gestión de Riesgos y Operaciones Críticas. Es un perfil resiliente y estable. **Apto para roles de alta presión.**", 
            "Promedio": "Muestra buena gestión emocional, pero puede fluctuar."
        },
    }
    
    return rec[dim].get(nivel_map, rec[dim].get("Promedio", "Desarrollar un plan de acción basado en las fortalezas y oportunidades en esta dimensión."))

def get_roles_no_recomendados(resultados):
    """Determina roles no recomendados basándose en puntajes extremos (resumen)."""
    no_aptos = set()
    UMBRAL_BAJO = 25
    UMBRAL_ALTO = 75

    # Lógica para mostrar la incompatibilidad solo cuando hay un puntaje extremo
    if resultados.get("Neuroticismo (N)", 0) > UMBRAL_ALTO:
        no_aptos.add("Liderazgo de Crisis (N>75)")
    if resultados.get("Responsabilidad (C)", 0) < UMBRAL_BAJO:
        no_aptos.add("Gestión de Proyectos Críticos (C<25)")
    if resultados.get("Amabilidad (A)", 0) < UMBRAL_BAJO:
        no_aptos.add("Recursos Humanos y Soporte al Cliente (A<25)")
    if resultados.get("Apertura a la Experiencia (O)", 0) < UMBRAL_BAJO:
        no_aptos.add("Investigación y Desarrollo (O<25)")
    if resultados.get("Extraversión (E)", 0) < UMBRAL_BAJO:
        no_aptos.add("Ventas y Relaciones Públicas (E<25)")

    if not no_aptos:
        return None 
    return " | ".join(sorted(list(no_aptos)))

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

# --- 3. FUNCIONES DE FLUJO DE PÁGINAS Y SCROLL ---

def procesar_y_mostrar_resultados():
    """Calcula y avanza a la vista de resultados con animación."""
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.stage = 'resultados'
    st.session_state.should_scroll = True
    st.rerun()

def iniciar_test():
    """Inicia el test en la primera dimensión."""
    st.session_state.stage = 'test_activo'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS} 
    st.session_state.resultados = None
    st.session_state.should_scroll = True 
    st.rerun()

def completar_al_azar():
    """Genera respuestas aleatorias y avanza a resultados."""
    respuestas_aleatorias = {p['key']: random.choice(LIKERT_OPTIONS) for p in PREGUNTAS}
    st.session_state.respuestas = respuestas_aleatorias
    procesar_y_mostrar_resultados()
    
def avanzar_dimension():
    """Avanza al siguiente índice de dimensión o finaliza el test."""
    if st.session_state.current_dimension_index < len(DIMENSIONES_LIST) - 1:
        st.session_state.current_dimension_index += 1
        st.session_state.should_scroll = True 
        st.rerun()
    else:
        procesar_y_mostrar_resultados()

def reiniciar_test():
    """Reinicia la aplicación a la vista de inicio."""
    st.session_state.stage = 'inicio'
    st.session_state.current_dimension_index = 0
    st.session_state.respuestas = {p['key']: None for p in PREGUNTAS} 
    st.session_state.resultados = None
    st.session_state.should_scroll = True
    st.rerun()

# --- 4. VISTAS DE LA APLICACIÓN ---

def vista_inicio():
    st.title("💼 Plataforma de Evaluación Big Five (OCEAN)")
    st.markdown("### Perfil de Competencias y Potencial Profesional")
    st.info("Este demo evalúa los **Cinco Grandes factores de personalidad**. El test consta de **25 preguntas divididas en 5 secciones**.")
    st.markdown("---")
    
    col_manual, col_azar = st.columns(2)
    
    with col_manual:
        st.subheader("Modo Manual")
        st.caption("Responde cada sección de forma honesta para generar tu perfil detallado.")
        st.button("🚀 Iniciar Evaluación Profesional", type="primary", use_container_width=True, on_click=iniciar_test)

    with col_azar:
        st.subheader("Modo Demo")
        st.caption("Genera un perfil aleatorio instantáneamente para probar la función de resultados.")
        st.button("🎲 Completar Test Aleatoriamente", type="secondary", use_container_width=True, on_click=completar_al_azar)


def vista_test_activo():
    
    current_index = st.session_state.current_dimension_index
    current_dim_name = DIMENSIONES_LIST[current_index]
    dim_info = DIMENSIONES[current_dim_name]
    
    st.title(f"📝 Dimensión {current_index + 1} de {len(DIMENSIONES_LIST)}: {dim_info['icon']} {current_dim_name}")
    st.markdown(f"**Descripción:** {dim_info['desc']}")
    st.markdown("---")
    
    # Barra de progreso general
    total_respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None)
    total_preguntas = len(PREGUNTAS)
    progreso_general = total_respondidas / total_preguntas
    st.progress(progreso_general, text=f"Progreso General: **{total_respondidas}** de **{total_preguntas}** preguntas respondidas.")
    st.markdown("---")

    preguntas_dimension = [p for p in PREGUNTAS if p['dim'] == current_dim_name]
    
    with st.form(f"form_dim_{current_index}"):
        
        respuestas_form = {} 
        
        for i, p in enumerate(preguntas_dimension):
            
            with st.container(border=True):
                col_num, col_text = st.columns([0.5, 9.5])
                
                with col_num:
                    st.markdown(f"**{i+1}.**")
                
                with col_text:
                    st.markdown(f"**Afirmación:** {p['text']}")
                    
                    initial_value = st.session_state.respuestas.get(p['key'])
                    initial_index = LIKERT_OPTIONS.index(initial_value) if initial_value is not None else None
                    
                    respuestas_form[p['key']] = st.radio(
                        label=f"Respuesta para la pregunta {p['key']}",
                        options=LIKERT_OPTIONS,
                        format_func=lambda x: ESCALA_LIKERT[x],
                        index=initial_index,
                        key=f"radio_{p['key']}", 
                        horizontal=True,
                        label_visibility="collapsed"
                    )
            
        st.markdown("---")
        
        button_label = "✅ Finalizar Evaluación y Generar Perfil" if current_index == len(DIMENSIONES_LIST) - 1 else f"➡️ Continuar a {DIMENSIONES_LIST[current_index+1]}"
        
        submitted = st.form_submit_button(button_label, type="primary", use_container_width=True)

        if submitted:
            # 1. Validar que las 5 preguntas de esta dimensión estén respondidas
            current_dim_answered = True
            for key, value in respuestas_form.items():
                if value is None:
                    current_dim_answered = False
                    break
            
            if not current_dim_answered:
                st.error(f"🚨 ¡ATENCIÓN! Debe responder **todas las preguntas** de la dimensión actual ({current_dim_name}) antes de continuar.")
            else:
                # 2. Persistir las respuestas del formulario en la sesión antes de avanzar/finalizar
                st.session_state.respuestas.update(respuestas_form)
                
                # 3. Avanzar o finalizar
                if current_index == len(DIMENSIONES_LIST) - 1:
                    procesar_y_mostrar_resultados()
                else:
                    avanzar_dimension()

def vista_resultados():
    st.title("📄 Informe de Perfil Big Five (Corporativo) 🎉")
    st.markdown("### Análisis de Tendencias de Comportamiento")
    
    resultados = st.session_state.resultados
    
    if resultados is None:
        st.warning("No se encontraron resultados. Por favor, complete la evaluación.")
        st.button("Volver al Inicio", on_click=reiniciar_test)
        return
        
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
            })
            
        df_resumen = pd.DataFrame(data_resumen)
        
        # Estilo para colorear las celdas según el nivel
        def color_score(s):
            styles = []
            for score in s:
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
    
    # --- 2. Roles No Recomendados ---
    st.header("2. Alerta de Incompatibilidad con Roles Clave 🛑")
    
    roles_no_aptos = get_roles_no_recomendados(resultados)
    
    if roles_no_aptos is None:
        st.success("Su perfil es **versátil**. No se identificaron incompatibilidades significativas para roles críticos en base a los puntajes extremos.")
    else:
        st.error(f"**Cargos NO Recomendados o de Alto Riesgo (Puntuación Extrema):** {roles_no_aptos}")
        st.caption("Esta lista se basa en puntuaciones extremas (Muy Alto o Muy Bajo) que sugieren una incompatibilidad significativa con las demandas típicas de estos roles.")
        
    st.markdown("---")

    # --- 3. Plan de Desarrollo Individual y Cargos Idóneos ---
    st.header("3. Plan de Desarrollo Individual y Aptitud Profesional ✅")
    
    for dim in DIMENSIONES_LIST:
        score = resultados[dim]
        nivel, color_hex, tag = get_nivel_interpretacion(score)
        
        with st.expander(f"**{DIMENSIONES[dim]['icon']} {dim}: Nivel {nivel} ({score} puntos)**", expanded=True):
            
            col_desc, col_rec = st.columns([1, 1])

            with col_desc:
                st.markdown(f"**Tendencia General:** {DIMENSIONES[dim]['desc']}")
                st.markdown(f"**Clasificación:** <span style='color:{color_hex}; font-weight: bold;'>{nivel} ({tag})</span>", unsafe_allow_html=True)
                
            with col_rec:
                st.subheader("Conclusión de Aptitud (Idóneo/No Idóneo)")
                rec = get_recomendaciones(dim, score)
                st.info(rec) 
            
            st.markdown("---")
            
    st.button("🔄 Realizar Nueva Evaluación", type="secondary", on_click=reiniciar_test, use_container_width=True)


# --- 5. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test_activo':
    vista_test_activo()
elif st.session_state.stage == 'resultados':
    vista_resultados()

# --- 6. EJECUCIÓN CONDICIONAL DEL SCROLL (FIX FINAL) ---
if st.session_state.should_scroll:
    forzar_scroll_al_top()
    st.session_state.should_scroll = False
