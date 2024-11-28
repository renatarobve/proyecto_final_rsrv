# ETFs.py
import yfinance as yf
import json
import re
import os




# Lista de fondos con nombre, símbolo y descripción
fondos = [
    {
        "nombre": "AZ China",
        "simbolo": "CN",
        "descripcion": "Fondo de inversión que sigue el rendimiento del mercado de valores chino."
    },
    {
        "nombre": "AZ MSCI Taiwan Index Fund",
        "simbolo": "TW",
        "descripcion": "Fondo indexado al índice MSCI Taiwan, que rastrea el rendimiento de las empresas más grandes de Taiwán."
    },
    {
        "nombre": "AZ Russell 2000",
        "simbolo": "RU2K.L",
        "descripcion": "Fondo que sigue el rendimiento del índice Russell 2000, compuesto por pequeñas empresas de EE.UU."
    },
    {
        "nombre": "AZ Brasil",
        "simbolo": "BR",
        "descripcion": "Fondo que invierte en el mercado de valores brasileño, buscando aprovechar el crecimiento económico del país."
    },
    {
        "nombre": "AZ MSCI United Kingdom",
        "simbolo": "EWU",
        "descripcion": "Fondo que rastrea el índice MSCI del Reino Unido, que incluye empresas del mercado británico."
    },
    {
        "nombre": "AZ DJ US Financial Sector",
        "simbolo": "^DJUSFN",
        "descripcion": "Fondo que sigue el sector financiero de EE.UU., representado por el índice Dow Jones US Financial."
    },
    {
        "nombre": "AZ BRIC",
        "simbolo": "BKF",
        "descripcion": "Fondo que invierte en los mercados emergentes de Brasil, Rusia, India y China (BRIC)."
    },
    {
        "nombre": "AZ MSCI South Korea Index",
        "simbolo": "EWY",
        "descripcion": "Fondo indexado al índice MSCI de Corea del Sur, que rastrea el mercado surcoreano."
    },
    {
        "nombre": "AZ Barclays Aggregate",
        "simbolo": "AGG",
        "descripcion": "Fondo que sigue el índice Barclays Aggregate, un referente del mercado de bonos en EE.UU."
    },
    {
        "nombre": "AZ Mercados Emergentes",
        "simbolo": "EEM",
        "descripcion": "Fondo que invierte en una variedad de mercados emergentes alrededor del mundo."
    },{
        "nombre": "AZ MSCI EMU",
        "simbolo": "EZU",
        "descripcion": "Fondo que sigue el índice MSCI EMU, compuesto por empresas de la Unión Económica y Monetaria de la UE."
    },
    {
        "nombre": "AZ FTSE/Xinhua China 25",
        "simbolo": "FXI",
        "descripcion": "Fondo que sigue el índice FTSE/Xinhua China 25, que incluye las principales empresas chinas."
    },
    {
        "nombre": "AZ Oro",
        "simbolo": "GLD",
        "descripcion": "Fondo de inversión que rastrea el valor del oro como activo de refugio seguro."
    },
    {
        "nombre": "AZ Latixx Mex CETETRAC",
        "simbolo": "CETETRC.MX",
        "descripcion": "Fondo que sigue el rendimiento de los CETES en México, un instrumento de deuda gubernamental."
    },
    {
        "nombre": "AZ QQQ Nasdaq 100",
        "simbolo": "QQQ",
        "descripcion": "Fondo que rastrea el índice Nasdaq 100, compuesto por las 100 mayores empresas tecnológicas de EE.UU."
    },
    {
        "nombre": "AZ MSCI Asia Ex-Japan",
        "simbolo": "AAXJ",
        "descripcion": "Fondo que sigue el rendimiento del índice MSCI Asia Ex-Japan, que excluye a Japón del mercado asiático."
    },
    {
        "nombre": "AZ Latixx Mex M10TRAC",
        "simbolo": "M10TRACISHRS.MX",
        "descripcion": "Fondo que invierte en bonos del gobierno mexicano con vencimientos de 10 años."
    },
    {
        "nombre": "AZ Barclays 1-3 Year TR",
        "simbolo": "SHY",
        "descripcion": "Fondo que sigue el índice Barclays de bonos a corto plazo, con vencimientos de 1 a 3 años."
    },
    {
        "nombre": "AZ MSCI ACWI Index Fund",
        "simbolo": "ACWI",
        "descripcion": "Fondo indexado al MSCI ACWI, que sigue empresas de mercados desarrollados y emergentes a nivel mundial."
    },
    {
        "nombre": "AZ Latixx Mex M5TRAC",
        "simbolo": "M5TRACISHRS.MX",
        "descripcion": "Fondo que sigue el rendimiento de bonos del gobierno mexicano con vencimientos de 5 años."
    },
    {
        "nombre": "AZ Silver Trust",
        "simbolo": "SLV",
        "descripcion": "Fondo que invierte en plata, rastreando su valor como activo de refugio."
    },
    {
        "nombre": "AZ MSCI Hong Kong Index",
        "simbolo": "EWH",
        "descripcion": "Fondo que sigue el índice MSCI de Hong Kong, que rastrea las principales empresas de esta región."
    },
    {
        "nombre": "AZ Latixx Mex UDITRAC",
        "simbolo": "UDITRAC.MX",
        "descripcion": "Fondo que sigue el rendimiento de UDIS en México, un índice de unidades de inversión."
    },
    {
        "nombre": "AZ SPDR S&P 500 ETF Trust",
        "simbolo": "SPY",
        "descripcion": "Fondo que sigue el índice S&P 500, compuesto por las 500 principales empresas de EE.UU."
    },
    {
        "nombre": "AZ MSCI Japan Index Fund",
        "simbolo": "EWJ",
        "descripcion": "Fondo indexado al índice MSCI Japan, que sigue el mercado de valores japonés."
    },
    {
        "nombre": "AZ BG EUR Govt Bond 1-3",
        "simbolo": "IBGS.AS",
        "descripcion": "Fondo que invierte en bonos del gobierno europeo con vencimientos de entre 1 y 3 años."
    },
    {
        "nombre": "AZ SPDR DJIA Trust",
        "simbolo": "DIA",
        "descripcion": "Fondo que sigue el índice Dow Jones Industrial Average, uno de los más importantes de EE.UU."
    },
    {
        "nombre": "AZ MSCI France Index Fund",
        "simbolo": "EWQ",
        "descripcion": "Fondo que sigue el índice MSCI de Francia, que incluye las principales empresas francesas."
    },
    {
        "nombre": "AZ DJ US Oil & Gas Expl",
        "simbolo": "IEO",
        "descripcion": "Fondo que sigue el sector de exploración de petróleo y gas de EE.UU."
    },
    {
        "nombre": "AZ Vanguard Emerging Market ETF",
        "simbolo": "VWO",
        "descripcion": "Fondo que invierte en mercados emergentes, rastreando el rendimiento de economías en crecimiento."
    },
    {
        "nombre": "AZ MSCI Australia Index",
        "simbolo": "EWA",
        "descripcion": "Fondo indexado al índice MSCI de Australia, que rastrea las principales empresas australianas."
    },
    {
        "nombre": "AZ IPC Large Cap T R TR",
        "simbolo": "ILCTRAC.MX",
        "descripcion": "Fondo que sigue el índice de grandes capitalizaciones en la Bolsa Mexicana de Valores."
    },
    {
        "nombre": "AZ Financial Select Sector SPDR",
        "simbolo": "XLF",
        "descripcion": "Fondo que sigue el sector financiero de EE.UU. a través del ETF SPDR Financial Select."
    },
    {
        "nombre": "AZ MSCI Canada",
        "simbolo": "EWC",
        "descripcion": "Fondo que sigue el índice MSCI de Canadá, compuesto por las principales empresas canadienses."
    },
    {
        "nombre": "AZ S&P Latin America 40",
        "simbolo": "ILF",
        "descripcion": "Fondo que sigue el índice S&P Latin America 40, compuesto por las mayores empresas de América Latina."
    },
    {
        "nombre": "AZ Health Care Select Sector",
        "simbolo": "XLV",
        "descripcion": "Fondo que sigue el sector de salud de EE.UU., incluyendo empresas farmacéuticas y de biotecnología."
    },
    {
        "nombre": "AZ MSCI Germany Index",
        "simbolo": "EWG",
        "descripcion": "Fondo que sigue el índice MSCI de Alemania, que incluye las principales empresas alemanas."
    },
    {
        "nombre": "AZ DJ US Home Construct",
        "simbolo": "ITB",
        "descripcion": "Fondo que sigue el sector de construcción de viviendas en EE.UU., representado por el índice Dow Jones US Home Construction."
    }
]



def sanitize_filename(filename):
    """
    Reemplaza caracteres especiales y espacios en un nombre de archivo por guiones bajos.
    """
    return re.sub(r'[^\w\s]', '_', filename).replace(' ', '_')



def obtener_datos_historicos(fondos, periodo="10y"):
    """
    Función que descarga los datos históricos de los fondos usando `yfinance`
    y los guarda en archivos JSON separados, incluyendo nombre, símbolo y descripción.
    Si un fondo no admite el periodo '10y', cambia automáticamente a 'max'.
    """
    no_disponibles = []  # Lista para registrar los fondos que no tienen datos

    for fondo in fondos:
        nombre = fondo["nombre"]
        simbolo = fondo["simbolo"]
        descripcion = fondo["descripcion"]
        
        try:
            print(f"Obteniendo datos para {nombre} ({simbolo})...")
            
            # Descargar datos históricos del fondo
            ticker = yf.Ticker(simbolo)
            datos = ticker.history(period=periodo)
            
            # Verificar si los datos están vacíos y si es así, intentar con "max"
            if datos.empty:
                print(f"Advertencia: No se obtuvieron datos para {nombre} ({simbolo}) con el período '{periodo}', intentando con 'max'...")
                datos = ticker.history(period="max")
                
            # Si aún están vacíos, registrar el fondo como no disponible
            if datos.empty:
                print(f"Advertencia: No se obtuvieron datos para {nombre} ({simbolo}) incluso con el período 'max'.")
                no_disponibles.append(fondo)  # Añadir a la lista de no disponibles
                continue
            
            # Convertir el índice de fechas a strings
            datos.index = datos.index.strftime('%Y-%m-%d')
            
            # Convertir los datos a formato dict para guardar en JSON
            datos_dict = datos.reset_index().to_dict(orient="records")
            
            # Crear un diccionario final con el nombre, símbolo, descripción y datos históricos
            datos_fondo = {
                "nombre": nombre,
                "simbolo": simbolo,
                "descripcion": descripcion,
                "datos_historicos": datos_dict
            }
            
            # Generar un nombre de archivo seguro usando la función `sanitize_filename`
            filename = f"Data/{sanitize_filename(simbolo)}_{sanitize_filename(nombre)}.json"
            with open(filename, 'w') as f:
                json.dump(datos_fondo, f, indent=4)
            
            print(f"Datos guardados correctamente en {filename}")
        
        except Exception as e:
            print(f"Error al obtener datos para {nombre} ({simbolo}): {e}")
            no_disponibles.append(fondo)  # Añadir a la lista de no disponibles en caso de error

    # Guardar los fondos que no tienen datos en un archivo JSON de reporte
    if no_disponibles:
        with open("Data/fondos_no_disponibles.json", 'w') as f:
            json.dump(no_disponibles, f, indent=4)
        print("Fondos sin datos guardados en 'Data/fondos_no_disponibles.json'")

# Llamada a la función
if __name__ == "__main__":
    obtener_datos_historicos(fondos)