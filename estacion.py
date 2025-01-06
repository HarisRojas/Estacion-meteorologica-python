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

API_KEY = "TU API KEY"
CITY = "TU CIUDAD"
BASE_URL = "http://api.openweathermap.org/data/2.5/"
WEATHER_URL = f"{BASE_URL}weather?q={CITY}&appid={API_KEY}&units=metric"
AIR_QUALITY_URL = f"{BASE_URL}air_pollution?lat=42.4627&lon=-2.4447&appid={API_KEY}"
INTERVALO_ACTUALIZACION = 3600  # 12 horas en segundos
CSV_FILE = f"{CITY}_datos_meteorologicos.csv"

console = Console()

def mostrar_reloj():
    with Live(refresh_per_second=1) as live:
        while True:
            hora_actual = datetime.now().strftime('%H:%M:%S')
            hora_ascii = pyfiglet.figlet_format(hora_actual)
            reloj_panel = Panel(
                f"[bold yellow]Hora actual:[/bold yellow]\n[bold cyan]{hora_ascii}[/bold cyan]",
                title="Reloj",
                border_style="magenta"
            )
            live.update(reloj_panel)
            time.sleep(1)

# Inicializar archivo CSV si no existe
def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Fecha y Hora",
                "Temp Min (°C)",
                "Temp Max (°C)",
                "Temp Actual (°C)",
                "Humedad (%)",
                "Viento (m/s)",
                "Dirección Viento (°)",
                "Presión (hPa)",
                "Índice Calidad Aire",
                "Nubosidad (%)",
                "Precipitación (mm)"
            ])
            console.print(f"[bold green]Archivo CSV inicializado: {CSV_FILE}[/bold green]")

# Escribir datos en el CSV
def escribir_csv(datos):
    # Crear encabezados si el archivo no existe
    if not os.path.exists(CSV_FILE):
        inicializar_csv()
    # Agregar nueva línea al archivo existente
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(datos)

# Leer datos históricos del CSV
def obtener_temperaturas_historicas():
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
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

# Generar la tabla meteorológica
def generar_tabla():
    try:
        # Obtener datos del clima
        weather_response = requests.get(WEATHER_URL)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Datos básicos
        temperatura_min = weather_data["main"]["temp_min"]
        temperatura_max = weather_data["main"]["temp_max"]
        temperatura_actual = weather_data["main"]["temp"]
        humedad = weather_data["main"]["humidity"]
        viento_velocidad = weather_data["wind"]["speed"]
        viento_direccion = weather_data["wind"]["deg"]
        presion = weather_data["main"]["pressure"]
        nubosidad = weather_data["clouds"]["all"]
        precipitacion = weather_data.get("rain", {}).get("1h", 0.0)

        # Obtener calidad del aire
        air_quality_response = requests.get(AIR_QUALITY_URL)
        air_quality_response.raise_for_status()
        air_quality_data = air_quality_response.json()
        calidad_aire = air_quality_data["list"][0]["main"]["aqi"]

        # Guardar datos en CSV
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
        escribir_csv(datos_csv)

        # Obtener datos históricos
        temp_min_historica, temp_max_historica = obtener_temperaturas_historicas()

        # Crear la tabla
        tabla = Table(title=f"Datos Meteorológicos para: {CITY}")
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

# Mostrar estación meteorológica
def mostrar_estacion_meteorologica():
    with Live(refresh_per_second=1) as live:
        while True:
            tabla = generar_tabla()
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
    inicializar_csv()
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
