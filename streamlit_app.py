import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="Big Five Personality Test Demo")

# Definición de las dimensiones del Big Five y sus colores
DIMENSIONES = {
    "Apertura a la Experiencia (O)": {"code": "O", "color": "#1f77b4", "icon": "💡"},
    "Responsabilidad (C)": {"code": "C", "color": "#ff7f0e", "icon": "🎯"},
    "Extraversión (E)": {"code": "E", "color": "#2ca02c", "icon": "🥳"},
    "Amabilidad (A)": {"code": "A", "color": "#d62728", "icon": "🤝"},
    "Neuroticismo (N)": {"code": "N", "color": "#9467bd", "icon": "😟"},
}
DIMENSIONES_LIST = list(DIMENSIONES.keys())

# Escala Likert de respuesta
ESCALA_LIKERT = {
    1: "Totalmente en desacuerdo",
    2: "En desacuerdo",
    3: "Neutral",
    4: "De acuerdo",
    5: "Totalmente de acuerdo",
}

# Preguntas de ejemplo (2 por dimensión, 10 en total)
# Nota: La codificación inversa (R) es crucial en los tests de personalidad
PREGUNTAS = [
    # Apertura
    {"text": "Disfruto de tener una gran variedad de experiencias.", "dim": "Apertura a la Experiencia (O)", "key": "q1", "reverse": False},
    {"text": "Evito los debates filosóficos o intelectuales.", "dim": "Apertura a la Experiencia (O)", "key": "q2", "reverse": True},
    # Responsabilidad
    {"text": "Siempre completo mis tareas a tiempo.", "dim": "Responsabilidad (C)", "key": "q3", "reverse": False},
    {"text": "Soy bastante desorganizado.", "dim": "Responsabilidad (C)", "key": "q4", "reverse": True},
    # Extraversión
    {"text": "Soy el alma de la fiesta.", "dim": "Extraversión (E)", "key": "q5", "reverse": False},
    {"text": "Me gusta pasar tiempo a solas.", "dim": "Extraversión (E)", "key": "q6", "reverse": True},
    # Amabilidad
    {"text": "Simpatizo fácilmente con los sentimientos de los demás.", "dim": "Amabilidad (A)", "key": "q7", "reverse": False},
    {"text": "No me molesto en ayudar si no es mi trabajo.", "dim": "Amabilidad (A)", "key": "q8", "reverse": True},
    # Neuroticismo
    {"text": "Me preocupo mucho por las cosas.", "dim": "Neuroticismo (N)", "key": "q9", "reverse": False},
    {"text": "Soy tranquilo y difícilmente me altero.", "dim": "Neuroticismo (N)", "key": "q10", "reverse": True},
]

# Inicialización del estado de la sesión
if 'stage' not in st.session_state:
    st.session_state.stage = 'inicio'
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {p['key']: 3 for p in PREGUNTAS}
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

# --- 2. FUNCIONES DE LÓGICA ---

def calcular_resultados(respuestas):
    """Calcula las puntuaciones de las 5 dimensiones."""
    scores = {dim: [] for dim in DIMENSIONES_LIST}
    
    for p in PREGUNTAS:
        respuesta = respuestas.get(p['key'], 3)
        
        # Aplicar la codificación inversa si es necesario
        if p['reverse']:
            score = 6 - respuesta # Escala de 1 a 5, inversa es 6 - respuesta
        else:
            score = respuesta
            
        scores[p['dim']].append(score)
        
    # Calcular el promedio y escalar a una puntuación de 0 a 100
    resultados = {}
    for dim, score_list in scores.items():
        # El puntaje promedio va de 1 a 5. Se escala a 0-100.
        avg_score = np.mean(score_list)
        # Escala: (Valor - Mín) / (Máx - Mín) * 100 -> (avg_score - 1) / 4 * 100
        percent_score = ((avg_score - 1) / 4) * 100
        resultados[dim] = round(percent_score)
        
    return resultados

def iniciar_test():
    st.session_state.stage = 'test'
    # Limpiar respuestas para el nuevo test
    st.session_state.respuestas = {p['key']: 3 for p in PREGUNTAS} 
    st.session_state.resultados = None

def procesar_y_mostrar_resultados():
    """Simula el proceso de cálculo con una animación de carga."""
    with st.spinner('Analizando tu personalidad...'):
        time.sleep(2) # Simular un cálculo complejo
    
    st.session_state.resultados = calcular_resultados(st.session_state.respuestas)
    st.session_state.stage = 'resultados'
    
def reiniciar_test():
    st.session_state.stage = 'inicio'
    st.session_state.respuestas = {p['key']: 3 for p in PREGUNTAS} 
    st.session_state.resultados = None

# --- 3. FUNCIONES DE VISUALIZACIÓN ---

def get_descripcion_nivel(dim, score):
    """Genera una descripción interpretativa basada en la puntuación 0-100."""
    icon = DIMENSIONES[dim]["icon"]
    if score >= 80:
        nivel = "Muy Alto"
        emoji = "🌟"
        consejo = "Esta es una característica dominante que influye fuertemente en tu comportamiento. Capitalízala."
    elif score >= 60:
        nivel = "Alto"
        emoji = "⬆️"
        consejo = "Esta característica es superior al promedio. Tienes una clara inclinación en esta área."
    elif score >= 40:
        nivel = "Promedio"
        emoji = "📏"
        consejo = "Tienes un balance en esta área. Puedes adaptarte fácilmente a diferentes contextos."
    elif score >= 20:
        nivel = "Bajo"
        emoji = "⬇️"
        consejo = "Esta característica es inferior al promedio. Podría ser un área de desarrollo o una preferencia por lo opuesto."
    else:
        nivel = "Muy Bajo"
        emoji = "🚩"
        consejo = "Esta es una característica notablemente baja. Considera si te está limitando en ciertos entornos."
        
    return f"{icon} **Nivel {nivel}** {emoji}: *{consejo}*"

def crear_grafico_radar(resultados):
    """Crea un gráfico de radar interactivo con Plotly."""
    categories = list(resultados.keys())
    values = list(resultados.values())
    
    # Crear la figura del radar
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Tu Perfil',
                line_color='#FF8C00', # Naranja fuerte
                fillcolor='rgba(255, 140, 0, 0.4)',
                marker=dict(size=10, symbol="circle", color="#FF4B4B"),
            )
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickvals=[25, 50, 75],
                    ticktext=["Bajo", "Promedio", "Alto"],
                    linecolor="#d3d3d3"
                ),
                angularaxis=dict(
                    linecolor="#d3d3d3"
                ),
            ),
            showlegend=False,
            height=550,
            # Añadir título y animaciones sutiles
            title=dict(text="Tu Perfil de Personalidad 'Big Five'", font=dict(size=20, color="#FF4B4B")),
            template="plotly_dark", # Tema oscuro para un aspecto moderno
            hovermode="closest",
        )
    )
    # Animación sutil de la etiqueta
    fig.update_traces(hovertemplate='<b>%{theta}</b>: %{r} puntos<extra></extra>')
    
    return fig


# --- 4. VISTAS DE LA APLICACIÓN ---

def vista_inicio():
    st.title("Test de Personalidad Big Five (Demo) 🧠")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("¿Qué mide el Big Five? 🤔")
        st.markdown("""
        El modelo de los Cinco Grandes (Big Five o OCEAN) es la teoría de la personalidad más aceptada.
        Mide 5 dimensiones fundamentales que describen la personalidad humana:
        
        * **O**penness (Apertura)
        * **C**onscientiousness (Responsabilidad)
        * **E**xtraversion (Extraversión)
        * **A**greeableness (Amabilidad)
        * **N**euroticism (Neuroticismo)
        
        Contesta con honestidad para ver tu perfil.
        """)
        
        st.button("🚀 Iniciar Test (10 Preguntas)", type="primary", use_container_width=True, on_click=iniciar_test)

    with col2:
        # Mini gráfico ilustrativo
        fig_intro = go.Figure(data=[
            go.Scatterpolar(
                r=[60, 80, 40, 70, 50],
                theta=DIMENSIONES_LIST,
                fill='toself',
                line_color='grey',
                opacity=0.4,
                hoverinfo='none',
            )
        ],
        layout=go.Layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            showlegend=False,
            height=300,
            template="plotly_dark"
        ))
        st.plotly_chart(fig_intro, use_container_width=True)

def vista_test():
    st.title("Preguntas del Test Big Five 📝")
    st.markdown("Por favor, puntúa qué tan de acuerdo estás con cada afirmación en la escala de **1 (Totalmente en desacuerdo)** a **5 (Totalmente de acuerdo)**.")
    
    # Animación: Barra de progreso
    n_respuestas = sum(1 for v in st.session_state.respuestas.values() if v is not None and v != 3) # Contar respondidas (si no es neutral)
    progreso = n_respuestas / len(PREGUNTAS)
    st.progress(progreso, text=f"Progreso del Test: {len(st.session_state.respuestas)} / {len(PREGUNTAS)}")


    with st.form("big_five_form"):
        # Se itera sobre las preguntas para crear los selectores
        for i, p in enumerate(PREGUNTAS):
            col_icon, col_text, col_slider = st.columns([0.5, 4, 2.5])
            
            with col_icon:
                st.markdown(f"<div style='font-size: 2em; line-height: 1.5; text-align: center; color:{DIMENSIONES[p['dim']]['color']};'>{DIMENSIONES[p['dim']]['icon']}</div>", unsafe_allow_html=True)
            
            with col_text:
                st.markdown(f"**{i+1}.** *{p['dim']}* | {p['text']}")
            
            with col_slider:
                st.session_state.respuestas[p['key']] = st.select_slider(
                    label="Puntuación",
                    options=list(ESCALA_LIKERT.keys()),
                    format_func=lambda x: ESCALA_LIKERT[x],
                    value=st.session_state.respuestas[p['key']],
                    key=f"slider_{p['key']}",
                    label_visibility="collapsed"
                )
            st.markdown("---")
            
        st.form_submit_button("✅ Finalizar y Obtener mi Perfil", type="primary", use_container_width=True, on_click=procesar_y_mostrar_resultados)


def vista_resultados():
    st.title("¡Tu Perfil Big Five está Listo! 🎉")
    st.balloons()
    
    resultados = st.session_state.resultados
    
    col_chart, col_summary = st.columns([1, 1])

    with col_chart:
        # 4.1 GRÁFICO RADAR INTERACTIVO
        st.subheader("4.1 Visualización de tu Perfil")
        fig = crear_grafico_radar(resultados)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_summary:
        # 4.2 DESGLOSE DE RESULTADOS
        st.subheader("4.2 Desglose y Análisis Dimensional")
        
        # DataFrame para la tabla resumen
        df_resumen = pd.DataFrame({
            "Dimensión": DIMENSIONES_LIST,
            "Puntuación (0-100)": [resultados[d] for d in DIMENSIONES_LIST],
            "Nivel": [get_descripcion_nivel(d, resultados[d]).split(" ")[1] for d in DIMENSIONES_LIST]
        })
        
        # Estilo de la tabla
        def highlight_score(val):
            color = 'background-color: #2ca02c' if val >= 75 else ('background-color: #d62728' if val <= 25 else '')
            return color

        st.dataframe(
            df_resumen.style.applymap(highlight_score, subset=['Puntuación (0-100)']),
            use_container_width=True,
            hide_index=True
        )
        
    st.markdown("---")

    # 4.3 INTERPRETACIONES DETALLADAS
    st.header("4.3 Interpretación Detallada de tu Perfil")
    
    for dim in DIMENSIONES_LIST:
        score = resultados[dim]
        color = DIMENSIONES[dim]["color"]
        
        with st.expander(f"**{DIMENSIONES[dim]['icon']} {dim}: {score} puntos**", expanded=score >= 70 or score <= 30):
            st.markdown(f"<div style='border-left: 5px solid {color}; padding: 10px; background-color: #f0f0f0;'>", unsafe_allow_html=True)
            st.markdown(get_descripcion_nivel(dim, score), unsafe_allow_html=True)
            
            # Ejemplo de interpretación basada en la dimensión (simulada)
            if dim == "Extraversión (E)":
                 if score >= 60:
                    st.markdown("Te orientas a la acción y disfrutas de la interacción social. Eres asertivo y te cargas de energía con otras personas.")
                 else:
                    st.markdown("Tiendes a ser reservado e independiente. Prefieres las actividades tranquilas o la soledad para recargar energía.")
            elif dim == "Neuroticismo (N)":
                 if score >= 60:
                    st.markdown("Eres propenso a experimentar emociones negativas como ansiedad y preocupación. Busca técnicas de manejo del estrés.")
                 else:
                    st.markdown("Eres emocionalmente estable, tranquilo y resiliente ante las dificultades. Mantienes la calma bajo presión.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("---")
    st.button("🔄 Realizar un Nuevo Test", type="secondary", on_click=reiniciar_test)


# --- 5. CONTROL DEL FLUJO PRINCIPAL ---

if st.session_state.stage == 'inicio':
    vista_inicio()
elif st.session_state.stage == 'test':
    vista_test()
elif st.session_state.stage == 'resultados':
    vista_resultados()