# Functions.py
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import json
import os
import glob
from datetime import datetime
import re
from datetime import timedelta



#####################################################################################################
def sanitize_filename(filename):
    """
    Reemplaza caracteres especiales y espacios en un nombre de archivo por guiones bajos.
    """
    return re.sub(r'[^\w\s]', '_', filename).replace(' ', '_')



def obtener_ruta_fondo(fondo_ticker):
    """
    Obtiene la ruta del archivo JSON para un fondo, manejando caracteres especiales en el nombre del archivo.
    """
    ticker_normalizado = sanitize_filename(fondo_ticker)
    patron_archivo = f"Data/{ticker_normalizado}_*.json"
    archivos = glob.glob(patron_archivo)
    
    if not archivos:
        raise FileNotFoundError(f"Archivo de datos no encontrado para el fondo: {fondo_ticker}. Asegúrate de que el archivo esté en la carpeta 'Data' y tenga el formato correcto.")
    
    return archivos[0]


def obtener_rendimiento_logaritmico_json(fondo_ticker):
    """
    Calcula el rendimiento logarítmico histórico de un fondo a partir de su archivo JSON.
    
    Parámetros:
    - fondo_ticker: Ticker del fondo.

    Retorna:
    - Rendimiento logarítmico anual del fondo.
    """
    # Obtener la ruta correcta del archivo
    filepath = obtener_ruta_fondo(fondo_ticker)

    with open(filepath, 'r') as f:
        data = json.load(f)

    precios_cierre = [entry["Close"] for entry in data["datos_historicos"] if "Close" in entry]
    
    if len(precios_cierre) < 2:
        raise ValueError(f"Datos insuficientes para calcular el rendimiento de {fondo_ticker}")

    precio_inicial = precios_cierre[0]
    precio_final = precios_cierre[-1]
    años = len(precios_cierre) / 252  # Aproximar años con días laborales

    log_return = np.log(precio_final / precio_inicial) / años
    return log_return



def obtener_rendimiento_geometrico_json(fondo_ticker):
    """
    Calcula el rendimiento geométrico promedio histórico de un fondo a partir de su archivo JSON.

    Parámetros:
    - fondo_ticker: Ticker del fondo.

    Retorna:
    - Rendimiento geométrico anual del fondo.
    """
    filepath = obtener_ruta_fondo(fondo_ticker)

    with open(filepath, 'r') as f:
        data = json.load(f)

    precios_cierre = [entry["Close"] for entry in data["datos_historicos"] if "Close" in entry]
    
    if len(precios_cierre) < 2:
        raise ValueError(f"Datos insuficientes para calcular el rendimiento de {fondo_ticker}")

    precio_inicial = precios_cierre[0]
    precio_final = precios_cierre[-1]
    años = len(precios_cierre) / 252

    rendimiento_geométrico = (precio_final / precio_inicial) ** (1 / años) - 1
    return rendimiento_geométrico



def calcular_tasa_retorno_ponderada(fondos_seleccionados):
    """
    Calcula la tasa de retorno promedio ponderada de los fondos seleccionados con ponderaciones iguales.

    Parámetros:
    - fondos_seleccionados: Lista de tickers de los fondos seleccionados.

    Retorna:
    - Tasa de retorno ponderada calculada a partir de los rendimientos logarítmicos.
    """
    n = len(fondos_seleccionados)
    if n == 0:
        raise ValueError("Debe seleccionar al menos un fondo para calcular la tasa de retorno ponderada.")
    
    ponderacion_igual = 1 / n  # Ponderación igual para cada fondo
    tasas = []
    
    for ticker in fondos_seleccionados:
        rendimiento = obtener_rendimiento_logaritmico_json(ticker)
        tasas.append(rendimiento * ponderacion_igual)  # Rendimiento ponderado con ponderación igual
    
    tasa_retorno_ponderada = sum(tasas)
    return tasa_retorno_ponderada

def calcular_tasa_geometrica_ponderada(fondos_seleccionados):
    """
    Calcula la tasa geométrica promedio ponderada de los fondos seleccionados con ponderaciones iguales.

    Parámetros:
    - fondos_seleccionados: Lista de tickers de los fondos seleccionados.

    Retorna:
    - Tasa geométrica promedio ponderada.
    """
    n = len(fondos_seleccionados)
    if n == 0:
        raise ValueError("Debe seleccionar al menos un fondo para calcular la tasa geométrica ponderada.")
    
    ponderacion_igual = 1 / n  # Ponderación igual para cada fondo
    tasas = []
    
    for ticker in fondos_seleccionados:
        rendimiento_geométrico = obtener_rendimiento_geometrico_json(ticker)
        tasas.append(rendimiento_geométrico * ponderacion_igual)  # Rendimiento ponderado

    tasa_geometrica_ponderada = sum(tasas)
    return tasa_geometrica_ponderada


def proyectar_crecimiento_inversion_ponderado(monto_inicial, tasa_retorno, años):
    """
    Proyecta el crecimiento de una inversión utilizando una tasa de retorno ponderada.

    Parámetros:
    - monto_inicial: Monto inicial de la inversión.
    - tasa_retorno: Tasa de retorno promedio ponderada.
    - años: Número de años de la inversión.

    Retorna:
    - DataFrame con el crecimiento anual del monto invertido.
    """
    # Calcular el crecimiento proyectado utilizando la fórmula de interés compuesto
    valores = [monto_inicial * np.exp(tasa_retorno * año) for año in range(años + 1)]
    df_proyeccion = pd.DataFrame({
        "Año": range(años + 1),
        "Monto Proyectado": valores
    })
    return df_proyeccion

def mostrar_proyeccion_crecimiento_ponderado(monto_inicial, fondos_seleccionados, años):
    """
    Calcula y muestra el gráfico de la proyección de crecimiento en Streamlit usando la tasa de retorno ponderada,
    y retorna la tasa de rendimiento anual para mostrar en el frontend.

    Retorna:
    - tasa_retorno: La tasa de retorno promedio ponderada.
    """
    # Calcular la tasa de retorno ponderada
    tasa_retorno = calcular_tasa_retorno_ponderada(fondos_seleccionados)
    
    # Validar que la tasa de retorno no sea None antes de continuar
    if tasa_retorno is None:
        st.error("Error: La tasa de retorno ponderada no se calculó correctamente.")
        return None

    # Obtener el DataFrame de proyección de crecimiento
    df_proyeccion = proyectar_crecimiento_inversion_ponderado(monto_inicial, tasa_retorno, años)
    
    # Crear el gráfico interactivo con Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_proyeccion["Año"], 
        y=df_proyeccion["Monto Proyectado"],
        mode="lines+markers",
        line=dict(color="blue"),
        marker=dict(size=6),
        name="Crecimiento proyectado"
    ))

    # Configuración del layout del gráfico
    fig.update_layout(
        title="Proyección del Crecimiento de la Inversión (Ponderada)",
        xaxis_title="Año",
        yaxis_title="Monto Proyectado (MXN)",
        template="plotly_white"
    )
    
    # Mostrar en Streamlit
    st.plotly_chart(fig)
    st.write(df_proyeccion)
    
    return tasa_retorno


def mostrar_proyeccion_geometrica(monto_inicial, fondos_seleccionados):
    """
    Calcula y muestra el gráfico de proyección de crecimiento a 5 años utilizando el rendimiento geométrico promedio.
    
    Parámetros:
    - monto_inicial: Monto inicial de la inversión.
    - fondos_seleccionados: Lista de tickers de los fondos seleccionados.

    Retorna:
    - La tasa de rendimiento geométrica promedio.
    """
    # Calcular la tasa de rendimiento geométrica ponderada
    tasa_geometrica = calcular_tasa_geometrica_ponderada(fondos_seleccionados)
    años = 5
    
    # Calcular la proyección de crecimiento a 5 años
    valores = [monto_inicial * (1 + tasa_geometrica) ** año for año in range(años + 1)]
    df_proyeccion = pd.DataFrame({
        "Año": range(años + 1),
        "Monto Proyectado": valores
    })

    # Graficar la proyección usando Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_proyeccion["Año"],
        y=df_proyeccion["Monto Proyectado"],
        mode="lines+markers",
        line=dict(color="green"),
        marker=dict(size=6),
        name="Proyección Geométrica"
    ))

    fig.update_layout(
        title="Proyección de Crecimiento a 5 Años (Geométrica)",
        xaxis_title="Año",
        yaxis_title="Monto Proyectado (MXN)",
        template="plotly_white"
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig)
    st.write(df_proyeccion)
    return tasa_geometrica

####Calcular rendimiento YTD
def calcular_rendimiento_ytd(datos_historicos):
    """
    Calcula el rendimiento YTD (año hasta la fecha) de un fondo.

    Parámetros:
    - datos_historicos: Lista de precios históricos (debe incluir el campo 'Date' y 'Close').

    Retorna:
    - Rendimiento YTD en porcentaje.
    """
    inicio_año = datetime(datetime.now().year, 1, 1)
    
    precios_ytd = []
    for entry in datos_historicos:
        if "Date" in entry and "Close" in entry:
            try:
                entry_date = datetime.strptime(entry["Date"], "%Y-%m-%d")
                if entry_date >= inicio_año:
                    precios_ytd.append(entry["Close"])
            except ValueError:
                continue  # Skip any entries with invalid dates
    
    if len(precios_ytd) < 2:
        return None
    
    rendimiento_ytd = (precios_ytd[-1] / precios_ytd[0] - 1) * 100
    return rendimiento_ytd

#Calcular el dividend yield
def calcular_rendimiento_dividendos(datos_historicos):
    """
    Calcula el rendimiento de dividendos de un fondo.

    Parámetros:
    - datos_historicos: Lista de precios históricos (debe incluir los campos 'Dividends' y 'Close').

    Retorna:
    - Rendimiento de dividendos en porcentaje.
    """
    # Sumar solo los dividendos disponibles en los datos históricos
    dividendos_totales = sum(entry.get("Dividends", 0) for entry in datos_historicos)
    precio_actual = datos_historicos[-1].get("Close")

    if precio_actual is None or precio_actual == 0:
        return None  # Evitar división por cero o valores inexistentes

    rendimiento_dividendos = (dividendos_totales / precio_actual) * 100
    return rendimiento_dividendos

#Calcular dividends per share 
def calcular_dividendos_por_accion(datos_historicos):
    """
    Calcula los dividendos por acción de un fondo.

    Parámetros:
    - datos_historicos: Lista de precios históricos (debe incluir el campo 'Dividends').

    Retorna:
    - Total de dividendos por acción.
    """
    # Usar get para evitar errores si 'Dividends' no está presente
    dividendos_totales = sum(entry.get("Dividends", 0) for entry in datos_historicos)
    return dividendos_totales


def calcular_rendimiento_volatilidad(datos_historicos, periodo="5y"):
    """
    Calcula el rendimiento y la volatilidad anualizada para un periodo dado.
    
    Parámetros:
    - datos_historicos: Lista de precios históricos (debe incluir el campo 'Close').
    - periodo: Periodo para el cálculo (por defecto "5y").
    
    Retorna:
    - rendimiento_anualizado, volatilidad_anualizada en porcentaje.
    """
    # Extraer precios de cierre
    precios_cierre = [entry["Close"] for entry in datos_historicos if "Close" in entry]
    
    # Calcular los rendimientos diarios logarítmicos
    rendimientos_diarios = np.log(np.array(precios_cierre[1:]) / np.array(precios_cierre[:-1]))

    # Calcular rendimiento y volatilidad anualizada
    rendimiento_anualizado = np.mean(rendimientos_diarios) * 252 * 100  # % anualizado
    volatilidad_anualizada = np.std(rendimientos_diarios) * np.sqrt(252) * 100  # % anualizada
    
    return rendimiento_anualizado, volatilidad_anualizada


############################ Optimizacion de portafolios ######################################

def obtener_datos_para_optimizar(fondos_seleccionados):
    """
    Genera una lista con las métricas necesarias para optimizar el portafolio.
    Incluye el rendimiento anualizado y la volatilidad anualizada.

    Parámetros:
    - fondos_seleccionados: Lista de nombres de los fondos seleccionados.

    Retorna:
    - Una lista de diccionarios con las métricas necesarias para la optimización.
    """
    datos_para_optimizar = []

    for fondo in fondos_seleccionados:
        try:
            # Obtener el archivo correspondiente
            archivo_fondo = obtener_ruta_fondo(fondo)
            with open(archivo_fondo, 'r') as f:
                datos_historicos = json.load(f)["datos_historicos"]

            # Calcular métricas
            rendimiento_anualizado, volatilidad_anualizada = calcular_rendimiento_volatilidad(datos_historicos)

            # Agregar los resultados a la lista
            datos_para_optimizar.append({
                "nombre": fondo,
                "rendimiento": rendimiento_anualizado,
                "volatilidad": volatilidad_anualizada
            })

        except FileNotFoundError:
            print(f"Advertencia: No se encontraron datos para el fondo {fondo}.")
        except Exception as e:
            print(f"Error al procesar el fondo {fondo}: {e}")

    return datos_para_optimizar


def normalizar_pesos(pesos):
    """
    Normaliza una lista de pesos para que sumen 1 (o el 100%).
    """
    suma = sum(pesos)
    return [peso / suma for peso in pesos]


# Funciones de optimización (son 5)

#Minimiza la volatilidad asignando más peso a los fondos con menor volatilidad.
def optimizar_portafolio_conservador():
    """
    Optimiza un portafolio conservador basado en mínima volatilidad.
    """
    if "fondos_data" not in st.session_state or not st.session_state.fondos_data:
        st.error("No se encontraron datos para optimizar. Verifica que seleccionaste fondos y calculaste las métricas.")
        return None, None, None, None

    datos_fondos = st.session_state.fondos_data
    datos_fondos = sorted(datos_fondos, key=lambda x: x["volatilidad"])  # Ordenar por volatilidad

    seleccionados = datos_fondos[:5]  # Seleccionar los 5 con menor volatilidad

    # Pesos dinámicos: inverso de la volatilidad
    pesos_iniciales = [1 / fondo["volatilidad"] for fondo in seleccionados]
    pesos = normalizar_pesos(pesos_iniciales)

    # Calcular rendimiento y volatilidad del portafolio
    rendimiento = sum(fondo["rendimiento"] * peso for fondo, peso in zip(seleccionados, pesos))
    volatilidad = np.sqrt(sum((fondo["volatilidad"] ** 2) * (peso ** 2) for fondo, peso in zip(seleccionados, pesos)))

    return seleccionados, pesos, rendimiento, volatilidad

#Balancea rendimiento y riesgo utilizando el ratio de Sharpe.
def optimizar_portafolio_moderado():
    """
    Optimiza un portafolio moderado balanceando riesgo y rendimiento.
    """
    if "fondos_data" not in st.session_state or not st.session_state.fondos_data:
        st.error("No se encontraron datos para optimizar. Verifica que seleccionaste fondos y calculaste las métricas.")
        return None, None, None, None

    datos_fondos = st.session_state.fondos_data

    # Calcular ratio de Sharpe (rendimiento / volatilidad) y ordenar
    for fondo in datos_fondos:
        fondo["sharpe"] = fondo["rendimiento"] / fondo["volatilidad"] if fondo["volatilidad"] > 0 else 0
    datos_fondos = sorted(datos_fondos, key=lambda x: x["sharpe"], reverse=True)

    seleccionados = datos_fondos[:5]  # Seleccionar los 5 mejores Sharpe ratios

    # Pesos dinámicos: basado en el ratio de Sharpe
    pesos_iniciales = [fondo["sharpe"] for fondo in seleccionados]
    pesos = normalizar_pesos(pesos_iniciales)

    # Calcular rendimiento y volatilidad del portafolio
    rendimiento = sum(fondo["rendimiento"] * peso for fondo, peso in zip(seleccionados, pesos))
    volatilidad = np.sqrt(sum((fondo["volatilidad"] ** 2) * (peso ** 2) for fondo, peso in zip(seleccionados, pesos)))

    return seleccionados, pesos, rendimiento, volatilidad

# Maximiza el rendimiento esperado priorizando los fondos con mayor rendimiento.
def optimizar_portafolio_agresivo():
    """
    Optimiza un portafolio agresivo priorizando máximo rendimiento.
    """
    if "fondos_data" not in st.session_state or not st.session_state.fondos_data:
        st.error("No se encontraron datos para optimizar. Verifica que seleccionaste fondos y calculaste las métricas.")
        return None, None, None, None

    datos_fondos = st.session_state.fondos_data
    datos_fondos = sorted(datos_fondos, key=lambda x: x["rendimiento"], reverse=True)  # Ordenar por rendimiento

    seleccionados = datos_fondos[:5]  # Seleccionar los 5 con mayor rendimiento

    # Pesos dinámicos: basado en rendimiento
    pesos_iniciales = [fondo["rendimiento"] for fondo in seleccionados]
    pesos = normalizar_pesos(pesos_iniciales)

    # Calcular rendimiento y volatilidad del portafolio
    rendimiento = sum(fondo["rendimiento"] * peso for fondo, peso in zip(seleccionados, pesos))
    volatilidad = np.sqrt(sum((fondo["volatilidad"] ** 2) * (peso ** 2) for fondo, peso in zip(seleccionados, pesos)))

    return seleccionados, pesos, rendimiento, volatilidad

# Maximiza rendimiento priorizando fondos con alta volatilidad y rendimiento.
def optimizar_portafolio_muy_agresivo():
    """
    Optimiza un portafolio muy agresivo priorizando rendimiento y alta volatilidad.
    """
    if "fondos_data" not in st.session_state or not st.session_state.fondos_data:
        st.error("No se encontraron datos para optimizar. Verifica que seleccionaste fondos y calculaste las métricas.")
        return None, None, None, None

    datos_fondos = st.session_state.fondos_data

    # Ordenar por rendimiento y volatilidad
    datos_fondos = sorted(datos_fondos, key=lambda x: (x["rendimiento"], x["volatilidad"]), reverse=True)

    seleccionados = datos_fondos[:5]  # Seleccionar los 5 mejores combinados

    # Pesos dinámicos: rendimiento * volatilidad
    pesos_iniciales = [fondo["rendimiento"] * fondo["volatilidad"] for fondo in seleccionados]
    pesos = normalizar_pesos(pesos_iniciales)

    # Calcular rendimiento y volatilidad del portafolio
    rendimiento = sum(fondo["rendimiento"] * peso for fondo, peso in zip(seleccionados, pesos))
    volatilidad = np.sqrt(sum((fondo["volatilidad"] ** 2) * (peso ** 2) for fondo, peso in zip(seleccionados, pesos)))

    return seleccionados, pesos, rendimiento, volatilidad

# Sigue las instrucciones del cliente de incluir todos los fondos, aunque en menor proporción
def optimizar_portafolio_personalizado():
    """
    Optimiza un portafolio basado en los fondos seleccionados sin restricciones estrictas.
    """
    if "fondos_data" not in st.session_state or not st.session_state.fondos_data:
        st.error("No se encontraron datos para optimizar. Verifica que seleccionaste fondos y calculaste las métricas.")
        return None, None, None, None

    datos_fondos = st.session_state.fondos_data

    # Pesos igualitarios para todos los fondos seleccionados
    pesos_iniciales = [1 for _ in datos_fondos]
    pesos = normalizar_pesos(pesos_iniciales)

    # Calcular rendimiento y volatilidad del portafolio
    rendimiento = sum(fondo["rendimiento"] * peso for fondo, peso in zip(datos_fondos, pesos))
    volatilidad = np.sqrt(sum((fondo["volatilidad"] ** 2) * (peso ** 2) for fondo, peso in zip(datos_fondos, pesos)))

    return datos_fondos, pesos, rendimiento, volatilidad


