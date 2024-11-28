# app_front.py
import streamlit as st
import json
import glob
from functions import (mostrar_proyeccion_crecimiento_ponderado, mostrar_proyeccion_geometrica, calcular_rendimiento_ytd, calcular_rendimiento_dividendos, calcular_dividendos_por_accion, calcular_rendimiento_volatilidad, obtener_datos_para_optimizar,optimizar_portafolio_agresivo,optimizar_portafolio_muy_agresivo,optimizar_portafolio_moderado,optimizar_portafolio_conservador,optimizar_portafolio_personalizado)
import pandas as pd
import re
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np

####### NORMALIZAR EL NOMBRE DE LOS ARCHIVOS QUE SE GUARDAN EN JSON #######
def sanitize_filename(filename):
    """
    Reemplaza caracteres especiales y espacios en un nombre de archivo por guiones bajos.
    """
    return re.sub(r'[^\w\s]', '_', filename).replace(' ', '_')

def obtener_nombre_archivo(fondo_info):
    """
    Genera un nombre de archivo normalizado para el JSON del fondo.
    """
    nombre_normalizado = sanitize_filename(fondo_info['nombre'])
    simbolo_normalizado = sanitize_filename(fondo_info['simbolo'])
    return f"{simbolo_normalizado}_{nombre_normalizado}.json"

# Configuración de la página de Streamlit
st.set_page_config(page_title="Simulador de Inversiones", page_icon="💹", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    .main-container {
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }
    .sidebar .sidebar-content {
        background-color: #F5F5F5;
        padding: 20px;
    }
    h1, h2, h3 {
        color: #004C99;
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar los fondos desde archivos JSON
@st.cache_data
def cargar_fondos():
    fondos = []
    for file in glob.glob("Data/*.json"):
        with open(file, 'r') as f:
            datos = json.load(f)
            fondos.append({
                "nombre": datos["nombre"],
                "simbolo": datos["simbolo"],
                "descripcion": datos["descripcion"]
            })
    return fondos

# Cargar los fondos disponibles
fondos_disponibles = cargar_fondos()

# Crear tabs
tab1, tab2 = st.tabs(["Cuestionario", "Resultados"])

################## --- Tab 1: Cuestionario --- ###########################
with tab1:
    st.title("Simulador de Inversiones en Fondos 💹")
    st.markdown("""
    ¡Bienvenido al simulador de inversiones! Completa los datos y responde el cuestionario para personalizar tu portafolio.  
    Esta herramienta te ayudará a evaluar el rendimiento de diferentes fondos y optimizar tus inversiones según tus metas financieras.
    """)

    # Inputs en la barra lateral
    st.sidebar.title("Datos Personales y Fondos")
    nombre = st.sidebar.text_input("Nombre", placeholder="Ingresa tu nombre completo")
    edad_actual = st.sidebar.number_input("Edad actual", min_value=18, max_value=100, step=1)
    edad_retiro = st.sidebar.number_input(
        "Edad a la que deseas terminar el plan de ahorro", 
        min_value=edad_actual + 1, max_value=100, step=1
    )
    monto_inicial = st.sidebar.slider(
        "Monto de inversión (mínimo $100,000 MXN)",
        min_value=100000, 
        max_value=10000000, 
        step=5000
    )
    
    # Mostrar el monto formateado justo debajo del slider en la barra lateral con espacio arriba y abajo
    st.sidebar.markdown(
    f"<div style='font-family: \"Source Sans Pro\", sans-serif; font-size:14px; color:#333333; margin-top:10px; margin-bottom:20px;'>"
    f"Monto de inversión seleccionado: <strong>${monto_inicial:,.0f} MXN</strong>"
    f"</div>",
    unsafe_allow_html=True
    )

    fondos_seleccionados = st.sidebar.multiselect(
        "Selecciona los Fondos de Inversión", 
        options=[fondo["nombre"] for fondo in fondos_disponibles],
        format_func=lambda x: f"{x} ({next(f['simbolo'] for f in fondos_disponibles if f['nombre'] == x)})"
    )

    # Mostrar información de los fondos seleccionados
    if fondos_seleccionados:
        st.sidebar.subheader("Descripción de los Fondos Seleccionados")
        for fondo_nombre in fondos_seleccionados:
            fondo_info = next((f for f in fondos_disponibles if f["nombre"] == fondo_nombre), None)
            if fondo_info:
                st.sidebar.write(f"**{fondo_info['nombre']}**")
                st.sidebar.write(f"*{fondo_info['descripcion']}*")

    # Validar datos ingresados
    if nombre and edad_actual and edad_retiro > edad_actual and monto_inicial and fondos_seleccionados:
        st.header("Cuestionario para Determinar tu Perfil de Inversión")

        preguntas = [
            "¿Cuál es tu principal objetivo al invertir?",
            "¿Qué harías si tu portafolio de inversión pierde el 10% de su valor en un mes?",
            "¿Cuánto tiempo estás dispuesto a mantener tus inversiones antes de necesitar los fondos?",
            "¿Qué nivel de conocimiento tienes sobre inversiones y mercados financieros?",
            "¿Cuál sería tu reacción si una inversión aumenta un 15% en seis meses?",
            "¿Qué proporción de tu patrimonio estás dispuesto a destinar a inversiones de riesgo?",
            "¿Qué opinas sobre la volatilidad en las inversiones?",
            "¿Cómo diversificarías tus inversiones?"
        ]

        respuestas_por_pregunta = [
            ["a) Preservar mi capital y evitar pérdidas a toda costa.",
             "b) Obtener un crecimiento moderado de mi dinero con riesgo limitado.",
             "c) Lograr un crecimiento alto, aunque implique asumir más riesgos.",
             "d) Maximizar mis ganancias, incluso si hay una alta posibilidad de pérdidas."],
            ["a) Retiraría mi inversión inmediatamente para evitar más pérdidas.",
             "b) Haría algunos ajustes, pero preferiría ser más conservador.",
             "c) No me preocuparía demasiado, los mercados fluctúan y esperaría.",
             "d) Vería la oportunidad de invertir más, buscando beneficios a largo plazo."],
            ["a) Menos de 1 año.",
             "b) Entre 1 y 3 años.",
             "c) Entre 3 y 5 años.",
             "d) Más de 5 años."],
            ["a) Ninguno, soy principiante y prefiero no complicarme.",
             "b) Básico, entiendo algunos conceptos como riesgo y diversificación.",
             "c) Intermedio, conozco bien cómo funcionan los mercados y algunos instrumentos financieros.",
             "d) Avanzado, tengo experiencia invirtiendo y gestionando portafolios."],
            ["a) Vendería inmediatamente para asegurar las ganancias.",
             "b) Consideraría vender una parte y proteger la ganancia.",
             "c) Mantendría la inversión esperando mayores ganancias.",
             "d) Invertiría más en esa oportunidad para maximizar los beneficios."],
            ["a) Menos del 10%.",
             "b) Entre 10% y 30%.",
             "c) Entre 30% y 50%.",
             "d) Más del 50%."],
            ["a) Prefiero evitarla, no me siento cómodo con las fluctuaciones.",
             "b) La tolero en un nivel moderado, siempre y cuando sea manejable.",
             "c) Es una oportunidad de obtener mejores rendimientos si se maneja correctamente.",
             "d) Es parte del juego y estoy dispuesto a asumir riesgos significativos."],
            ["a) Todo en instrumentos de bajo riesgo como bonos o fondos seguros.",
             "b) Principalmente en opciones conservadoras con algo de exposición a acciones.",
             "c) Una mezcla balanceada entre acciones, bonos y otros activos.",
             "d) En su mayoría acciones y activos de alto rendimiento."]
        ]

        puntos_respuesta = {"a": 1, "b": 2, "c": 3, "d": 4}
        
        # Inicializar estado del cuestionario
        if "pregunta_actual" not in st.session_state:
            st.session_state.pregunta_actual = 0
        if "respuestas" not in st.session_state:
            st.session_state.respuestas = [None] * len(preguntas)  # Lista para almacenar respuestas

        # Obtener la pregunta actual
        pregunta_actual = st.session_state.pregunta_actual
        st.markdown(f"**Pregunta {pregunta_actual + 1}/{len(preguntas)}: {preguntas[pregunta_actual]}**")

        # Crear un formulario para la interacción con la pregunta actual
        with st.form(key=f"form_pregunta_{pregunta_actual}"):
            # Mostrar las opciones de respuesta
            respuesta = st.radio(
                label="Selecciona tu respuesta:",
                options=["a", "b", "c", "d"],
                format_func=lambda x: respuestas_por_pregunta[pregunta_actual][ord(x) - ord('a')],
                key=f"radio_pregunta_{pregunta_actual}"
            )

            # Botón para avanzar
            siguiente = st.form_submit_button("Siguiente")

            if siguiente:
                # Guardar la respuesta seleccionada
                st.session_state.respuestas[pregunta_actual] = puntos_respuesta[respuesta]

                # Avanzar a la siguiente pregunta si hay más preguntas
                if st.session_state.pregunta_actual + 1 < len(preguntas):
                    st.session_state.pregunta_actual += 1
                else:
                    # Calcular el puntaje total y determinar el perfil
                    puntaje_total = sum(st.session_state.respuestas)
                    if 8 <= puntaje_total <= 14:
                        st.session_state.perfil = "Conservador"
                        st.session_state.descripcion = "Buscas estabilidad y seguridad. Prefieres evitar pérdidas, incluso a costa de menores rendimientos."
                    elif 15 <= puntaje_total <= 20:
                        st.session_state.perfil = "Moderado"
                        st.session_state.descripcion = "Toleras algo de riesgo para lograr rendimientos superiores, pero priorizas la protección del capital."
                    elif 21 <= puntaje_total <= 26:
                        st.session_state.perfil = "Agresivo"
                        st.session_state.descripcion = "Dispuesto a asumir riesgos significativos para maximizar tus rendimientos."
                    else:
                        st.session_state.perfil = "Muy Agresivo"
                        st.session_state.descripcion = "Alta tolerancia al riesgo, enfocado en maximizar ganancias con alta volatilidad."

                    # Mostrar un mensaje de éxito
                    st.success(f"Cuestionario completado. Tu perfil es: **{st.session_state.perfil}**. Dirígete a la sección de Resultados para continuar con la elaboración de tu portafolio")

                    # Reiniciar el estado del cuestionario para evitar errores al volver a empezar
                    st.session_state.pregunta_actual = 0
                    st.session_state.respuestas = [None] * len(preguntas)


############################# --- Tab 2: Resultados --- ##################################
with tab2:
    if "perfil" in st.session_state and st.session_state.perfil:
        st.header("Resultados de la Simulación 📊")
        st.markdown(f"Tu Perfil de Inversión es: **{st.session_state.perfil}**")
        st.write(f"Descripción: *{st.session_state.descripcion}*")

        datos_fondos=[]

        for fondo in fondos_seleccionados:
            fondo_info = next((f for f in fondos_disponibles if f["nombre"] == fondo), None)
            if not fondo_info:
                st.write(f"No se encontraron datos para el fondo: {fondo}")
                continue

            # Obtener datos históricos
            archivo_fondo = obtener_nombre_archivo(fondo_info)
            try:
                with open(f"Data/{archivo_fondo}", 'r') as f:
                    datos_historicos = json.load(f)["datos_historicos"]
            except FileNotFoundError:
                st.write(f"Archivo de datos no encontrado para el fondo: {fondo}")
                continue

            # Calcular métricas con funciones del backend
            rendimiento_ytd = calcular_rendimiento_ytd(datos_historicos)
            rendimiento_dividendos = calcular_rendimiento_dividendos(datos_historicos)
            dividendos_por_accion = calcular_dividendos_por_accion(datos_historicos)
            rendimiento_anualizado, volatilidad_anualizada = calcular_rendimiento_volatilidad(datos_historicos)

            # Agregar resultados
            datos_fondos.append({
                "nombre": fondo,
                "Rendimiento YTD": f"{rendimiento_ytd:.2f}%" if rendimiento_ytd is not None else "No disponible",
                "Rendimiento de Dividendos": f"{rendimiento_dividendos:.2f}%" if rendimiento_dividendos is not None else "No disponible",
                "Dividendos por Acción": f"${dividendos_por_accion:.2f}" if dividendos_por_accion is not None else "No disponible"
            })

        # Mostrar resultados como tabla
        if datos_fondos:
            st.subheader("Resumen de Métricas")
            st.markdown("Antes de ver tu **portafolio optimizado**, puedes revisar las métricas de los fondos que seleccionaste para decidir si quieres agregar otros o cambiar los seleccionados.")
            df_fondos = pd.DataFrame(datos_fondos)
            st.table(df_fondos)
    

        # Gráfica de Rendimiento vs. Riesgo
        st.subheader("Rendimiento vs. Riesgo de Fondos Seleccionados")
        nombres_fondos, rendimientos, volatilidades = [], [], []

        for fondo in fondos_seleccionados:
            fondo_info = next((f for f in fondos_disponibles if f["nombre"] == fondo), None)
            archivo_fondo = obtener_nombre_archivo(fondo_info)
            try:
                with open(f"Data/{archivo_fondo}", 'r') as f:
                    data = json.load(f)
                    datos_historicos = data.get("datos_historicos", [])
                    if not datos_historicos:
                        st.write(f"El fondo {fondo['nombre']} no tiene datos históricos.")
                        continue

                    # Calcular rendimiento y volatilidad
                    rendimiento, volatilidad = calcular_rendimiento_volatilidad(datos_historicos, periodo="5y")
                    nombres_fondos.append(fondo_info["nombre"])
                    rendimientos.append(rendimiento)
                    volatilidades.append(volatilidad)
            except Exception as e:
                st.write(f"Error al procesar {fondo['nombre']}: {e}")

        if nombres_fondos:
            df_fondos_riesgo = pd.DataFrame({
                "Fondo": nombres_fondos,
                "Rendimiento Anualizado (%)": [f"{x:.2f}%" for x in rendimientos],
                "Volatilidad Anualizada (%)": [f"{x:.2f}%" for x in volatilidades]
            })

            fig = px.scatter(
                df_fondos_riesgo,
                x="Volatilidad Anualizada (%)",
                y="Rendimiento Anualizado (%)",
                text="Fondo",
                title="Rendimiento vs. Riesgo",
                labels={"Volatilidad Anualizada (%)": "Riesgo (Volatilidad)", "Rendimiento Anualizado (%)": "Rendimiento"},
                color="Fondo"
            )
            fig.update_traces(textposition="top center", textfont_size=15, marker=dict(size=13))
            st.plotly_chart(fig)

        fondos_data = []

        for fondo in fondos_seleccionados:
            fondo_info = next((f for f in fondos_disponibles if f["nombre"] == fondo), None)
            archivo_fondo = obtener_nombre_archivo(fondo_info)
            try:
                with open(f"Data/{archivo_fondo}", 'r') as f:
                    data = json.load(f)
                    datos_historicos = data.get("datos_historicos", [])
                    if not datos_historicos:
                        st.write(f"El fondo {fondo} no tiene datos históricos.")
                        continue

                    # Calcular rendimiento y volatilidad
                    rendimiento, volatilidad = calcular_rendimiento_volatilidad(datos_historicos, periodo="5y")
                    
                    # Guardar los datos necesarios para optimización
                    fondos_data.append({
                        "nombre": fondo,
                        "rendimiento": rendimiento,
                        "volatilidad": volatilidad
                    })
            except Exception as e:
                st.write(f"Error al procesar {fondo}: {e}")

        # Mostrar los datos calculados para verificación
        #st.write("Datos calculados para optimización:", fondos_data)
        
        #Pasar los datos al backend
        st.session_state.fondos_data = fondos_data


        # Incluir el checkbox para todos los fondos seleccionados
        incluir_todos = st.checkbox(
            "Quiero dar la misma ponderación a todos los fondos que elegí. (Cada fondo de tu portafolio tendrá el mismo peso)",
            value=True
        )

        # Decidir la función de optimización según el valor de incluir_todos
        if incluir_todos:
            # Llamar a la optimización flexible que incluye todos los fondos seleccionados
            if "fondos_data" not in st.session_state or not st.session_state.fondos_data:
                st.error("No se encontraron datos para optimizar. Verifica que seleccionaste fondos y calculaste las métricas.")
            else:
                seleccionados, pesos, rendimiento, riesgo = optimizar_portafolio_personalizado()

        else:
            # Llamar a la optimización según el perfil del cliente
            if st.session_state.perfil == "Conservador":
                seleccionados, pesos, rendimiento, riesgo = optimizar_portafolio_conservador()
            elif st.session_state.perfil == "Moderado":
                seleccionados, pesos, rendimiento, riesgo = optimizar_portafolio_moderado()
            elif st.session_state.perfil == "Agresivo":
                seleccionados, pesos, rendimiento, riesgo = optimizar_portafolio_agresivo()
            elif st.session_state.perfil == "Muy Agresivo":
                seleccionados, pesos, rendimiento, riesgo = optimizar_portafolio_muy_agresivo()
            else:
                seleccionados, pesos, rendimiento, riesgo = None, None, None, None

        # Mostrar resultados si la optimización fue exitosa
        if seleccionados and pesos:
            # Crear un DataFrame con los resultados de optimización
            df_resultados = pd.DataFrame({
                'Fondo': [fondo["nombre"] for fondo in seleccionados],
                'Rendimiento Anualizado (%)': [fondo["rendimiento"] for fondo in seleccionados],
                'Volatilidad Anualizada (%)': [fondo["volatilidad"] for fondo in seleccionados],
                'Peso (%)': [peso * 100 for peso in pesos]
            })

            # Mostrar la tabla con los resultados
            st.write("### Portafolio Optimizado")
            st.write(df_resultados)

            # Mostrar el rendimiento y riesgo total del portafolio
            st.write(f"**Rendimiento Total del Portafolio:** {rendimiento :.2f}%")
            st.write(f"**Volatilidad Total del Portafolio:** {riesgo :.2f}%")

            # Graficar la distribución de los pesos
            st.write("### Distribución del Portafolio")
            st.bar_chart(df_resultados.set_index('Fondo')['Peso (%)'])
        else:
            st.error("No se pudieron obtener métricas suficientes para optimizar el portafolio.")

        def calcular_proyeccion_inversion(monto_inicial, rendimiento, anos_inversion):
            """
            Calcula el valor futuro de una inversión utilizando el gradiente geométrico (crecimiento compuesto).
            
            Args:
                monto_inicial: Monto inicial de la inversión.
                rendimiento: Rendimiento anualizado de la inversión (como un decimal).
                anos_inversion: Número de años para proyectar la inversión.
            
            Returns:
                float: Valor proyectado de la inversión.
            """
            return monto_inicial * (1 + rendimiento) ** anos_inversion

                # Calcular los años hasta el retiro
        anos_inversion = edad_retiro - edad_actual

        # Verifica si el rendimiento anualizado está disponible
        if rendimiento:
            # Calcular la proyección del crecimiento de la inversión
            valor_proyectado = calcular_proyeccion_inversion(monto_inicial, rendimiento / 100, anos_inversion)
            
            # Mostrar la proyección en la interfaz de usuario
            st.subheader(f"Proyección de Crecimiento de tu Inversión hasta los {edad_retiro} años")
            st.write(f"Con un rendimiento anualizado del **{rendimiento:.2f}%**, tu inversión de **${monto_inicial:,.0f} MXN** crecería a:")
            st.write(f"**${valor_proyectado:,.0f} MXN** después de **{anos_inversion} años**.^^")
            st.markdown("*^^Este calculo es el resultado de utilizar el gradiente geométrico basado en el desempeño histórico de los fondos que forman parte del portafolio. Esta proyección no tiene rendimientos garantizados, sin embargo es un cálculo para estimar el crecimiento aproximado de tu capital.*")

            # Graficar la proyección de crecimiento año a año
            anos = list(range(anos_inversion + 1))
            valores_proyeccion = [calcular_proyeccion_inversion(monto_inicial, rendimiento / 100, i) for i in anos]

            st.subheader("Gráfica de Proyección del Crecimiento de la Inversión")
            st.line_chart(valores_proyeccion)
        else:
            st.error("No se pudo calcular el rendimiento anualizado. Asegúrate de que todos los fondos seleccionados tengan datos históricos suficientes.")




                
