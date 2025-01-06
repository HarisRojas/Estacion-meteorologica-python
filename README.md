# Estación Meteorológica y Reloj en Python

Este proyecto es un script en Python que actúa como una estación meteorológica interactiva y un reloj en tiempo real. Obtiene datos meteorológicos en vivo de la API de OpenWeather y los presenta en una tabla interactiva en la terminal, utilizando la librería `rich` para visualizaciones dinámicas y atractivas.

## Características

- **Reloj en tiempo real**: Muestra la hora actual en formato ASCII artístico.
- **Estación meteorológica**: 
  - Obtiene datos como temperatura, humedad, velocidad del viento, calidad del aire, presión atmosférica, y más.
  - Guarda los datos obtenidos en un archivo CSV para análisis históricos.
  - Actualización automática de los datos meteorológicos en intervalos configurables.
  - Visualización de datos históricos (temperaturas mínimas y máximas).

## Requisitos

- Python 3.7 o superior.
- Librerías requeridas:
  - `requests`
  - `rich`
  - `pyfiglet`

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/HarisRojas/Estaci-n-metereol-gica-python.git
   cd Estaci-n-metereol-gica-python
2. **Instalar las dependencias**:
    ```bash
    pip install requests rich pyfiglet
3. **Configurar el script**:
    - Asegúrate de tener una clave de API de OpenWeather.
    - Modifica la variable API_KEY en el script y añade tu clave de API.

## Uso
Ejecuta el script directamente desde la terminal:
  ```bash
  python estacion.py

## Menú principal

El script ofrece un menú con tres opciones:
    1. **Reloj:** Muestra un reloj en tiempo real con estilo ASCII. Presiona Ctrl+C para regresar al menú.
    2. **Estación Meteorológica:** Obtiene y muestra los datos meteorológicos en vivo y los guarda en un archivo CSV. También muestra datos históricos de temperaturas mínimas y máximas.
    3. **Salir:** Sal del programa con una confirmación previa.

## Archivo CSV
    1. Si el archivo CSV ya existe, el script agrega los nuevos datos meteorológicos al archivo.
    2. Si no existe, el script lo crea en la ruta actual donde se encuentra el script y escribe los encabezados automáticamente.

El archivo tiene las siguientes columnas:
    - Fecha y Hora
    - Temp Min (°C)
    - Temp Max (°C)
    - Temp Actual (°C)
    - Humedad (%)
    - Viento (m/s)
    - Dirección Viento (°)
    - Presión (hPa)
    - Índice Calidad Aire
    - Nubosidad (%)
    - Precipitación (mm)

## Personalización
    - Ciudad: Cambia la variable CITY en el script para monitorear otra ubicación.
    - Intervalo de actualización: Modifica la constante INTERVALO_ACTUALIZACION (en segundos) para ajustar la frecuencia de actualización de los datos meteorológicos.

## Notas
    - Asegúrate de que tu conexión a Internet esté activa para obtener los datos meteorológicos en tiempo real.
    - El script funciona de forma óptima en sistemas con Python 3 y las librerías requeridas instaladas correctamente.

## Licencia

Este proyecto está bajo la Licencia MIT.
