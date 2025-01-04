import requests
import time
import sys
import csv
from datetime import datetime
from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import pyfiglet
import os

API_KEY = "36fb65f7fcb2d917cef74ea405239d5e"
BASE_URL = "http://api.openweathermap.org/data/2.5/"
INTERVALO_ACTUALIZACION = 43200  # 12 horas en segundos
console = Console()

# Diccionario de ciudades españolas
CIUDADES = {
    "1": ("Madrid", 40.4168, -3.7038),
    "2": ("Barcelona", 41.3879, 2.16992),
    "3": ("Valencia", 39.4699, -0.3763),
    "4": ("Sevilla", 37.3886, -5.9823),
    "5": ("Zaragoza", 41.6488, -0.8891),
    "6": ("Logroño", 42.4627, -2.4447),
}

# Inicializar archivo CSV para cada ciudad
def inicializar_csv(ciudad):
    csv_file = f"{ciudad}_datos_meteorologicos.csv"
    if not os.path.exists(csv_file):
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Fecha y Hora",
                "Temp Min (°C)",
                "Temp Max (°C)",
                "Temp Actual (°C)",
                "Humedad Actual (%)",
                "Viento (m/s)",
                "Dirección Viento (°)",
                "Presión (hPa)",
                "Índice Calidad Aire",
                "Nubosidad (%)",
                "Precipitación (mm)"
            ])
    return csv_file

# Escribir datos en el CSV
def escribir_csv(csv_file, datos):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(datos)

# Obtener temperaturas históricas
def obtener_temperaturas_historicas(csv_file):
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            temperaturas_min = []
            temperaturas_max = []
            for fila in reader:
                temperaturas_min.append(float(fila["Temp Min (°C)"]))
                temperaturas_max.append(float(fila["Temp Max (°C)"]))

            temp_min_historica = min(temperaturas_min) if temperaturas_min else "N/A"
            temp_max_historica = max(temperaturas_max) if temperaturas_max else "N/A"
            return temp_min_historica, temp_max_historica
    except FileNotFoundError:
        return "N/A", "N/A"

# Generar tabla meteorológica
def generar_tabla(ciudad, latitud, longitud):
    try:
        # URLs de las APIs
        WEATHER_URL = f"{BASE_URL}weather?q={ciudad}&appid={API_KEY}&units=metric"
        AIR_QUALITY_URL = f"{BASE_URL}air_pollution?lat={latitud}&lon={longitud}&appid={API_KEY}"

        # Datos del clima
        weather_response = requests.get(WEATHER_URL)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        temperatura_min = weather_data["main"]["temp_min"]
        temperatura_max = weather_data["main"]["temp_max"]
        temperatura_actual = weather_data["main"]["temp"]
        humedad = weather_data["main"]["humidity"]
        viento_velocidad = weather_data["wind"]["speed"]
        viento_direccion = weather_data["wind"]["deg"]
        presion = weather_data["main"]["pressure"]
        nubosidad = weather_data["clouds"]["all"]
        precipitacion = weather_data.get("rain", {}).get("1h", 0.0)

        # Calidad del aire
        air_quality_response = requests.get(AIR_QUALITY_URL)
        air_quality_response.raise_for_status()
        air_quality_data = air_quality_response.json()
        calidad_aire = air_quality_data["list"][0]["main"]["aqi"]

        # Archivo CSV
        csv_file = inicializar_csv(ciudad)
        datos_csv = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            temperatura_min,
            temperatura_max,
            temperatura_actual,
            humedad,
            viento_velocidad,
            viento_direccion,
            presion,
            calidad_aire,
            nubosidad,
            precipitacion
        ]
        escribir_csv(csv_file, datos_csv)

        # Datos históricos
        temp_min_historica, temp_max_historica = obtener_temperaturas_historicas(csv_file)

        # Crear tabla
        tabla = Table(title=f"Datos Meteorológicos para: {ciudad}")
        tabla.add_column("Parámetro", style="cyan", justify="left")
        tabla.add_column("Valor", style="magenta", justify="right")

        tabla.add_row("Temp Min (°C)", f"{temperatura_min}")
        tabla.add_row("Temp Max (°C)", f"{temperatura_max}")
        tabla.add_row("Temp Actual (°C)", f"{temperatura_actual}")
        tabla.add_row("Humedad Actual (%)", f"{humedad}")
        tabla.add_row("Viento (m/s)", f"{viento_velocidad}")
        tabla.add_row("Dirección Viento (°)", f"{viento_direccion}")
        tabla.add_row("Presión (hPa)", f"{presion}")
        tabla.add_row("Índice Calidad Aire", f"{calidad_aire}")
        tabla.add_row("Nubosidad (%)", f"{nubosidad}")
        tabla.add_row("Precipitación (mm)", f"{precipitacion}")
        tabla.add_row("Temp Min Histórica (°C)", f"{temp_min_historica}")
        tabla.add_row("Temp Max Histórica (°C)", f"{temp_max_historica}")

        return tabla

    except requests.exceptions.RequestException as e:
        return Panel(f"[bold red]Error al obtener los datos:[/bold red] {e}", title="Error")

# Submenú de selección de ciudad
def seleccionar_ciudad():
    ciudades_menu = "\n".join([f"[bold green]{key}.[/] {value[0]}" for key, value in CIUDADES.items()])
    ciudades_panel = Panel(ciudades_menu, title="Selecciona una Ciudad", border_style="cyan")
    console.print(ciudades_panel)
    opcion = Prompt.ask("[bold green]Selecciona una opción[/bold green]", choices=CIUDADES.keys())
    return CIUDADES[opcion]

# Mostrar estación meteorológica
def mostrar_estacion_meteorologica():
    ciudad, latitud, longitud = seleccionar_ciudad()
    with Live(refresh_per_second=1) as live:
        while True:
            tabla = generar_tabla(ciudad, latitud, longitud)
            for segundos in range(INTERVALO_ACTUALIZACION, 0, -1):
                panel_temporizador = Panel(
                    f"[bold yellow]Próxima actualización en:[/bold yellow] [bold cyan]{segundos}[/bold cyan] segundos",
                    title="Temporizador"
                )
                contenido = Group(tabla, panel_temporizador)
                live.update(contenido)
                time.sleep(1)

# Menú principal
def mostrar_menu():
    menu = Panel(
        """
[bold green]1.[/] Reloj
[bold green]2.[/] Estación Meteorológica
[bold green]3.[/] Salir
        """,
        title="Menú Principal",
        border_style="cyan"
    )
    console.print(menu)

# Limpieza de pantalla
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

# Función principal
def main():
    while True:
        console.clear()
        mostrar_menu()
        opcion = Prompt.ask("[bold green]Selecciona una opción[/bold green]", choices=["1", "2", "3"], default="3")
        
        if opcion == "1":
            console.clear()
            console.print("[bold cyan]Mostrando el reloj. Presiona Ctrl+C para regresar al menú.[/bold cyan]")
            try:
                mostrar_reloj()
            except KeyboardInterrupt:
                console.print("[bold red]\nVolviendo al menú principal...[/bold red]")
        
        elif opcion == "2":
            console.clear()
            console.print("[bold cyan]Mostrando la estación meteorológica. Presiona Ctrl+C para regresar al menú.[/bold cyan]")
            try:
                mostrar_estacion_meteorologica()
            except KeyboardInterrupt:
                console.print("[bold red]\nVolviendo al menú principal...[/bold red]")
        
        elif opcion == "3":
            salir = Confirm.ask("[bold red]¿Estás seguro de que quieres salir?[/bold red]", default=False)
            if salir:
                limpiar_pantalla()
                console.print("[bold yellow]¡Hasta luego![/bold yellow]")
                sys.exit()
            else:
                console.print("[bold green]Regresando al menú principal...[/bold green]")

if __name__ == "__main__":
    main()
