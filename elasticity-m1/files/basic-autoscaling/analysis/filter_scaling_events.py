# ------------------------------------------------------------------------------
# ARCHIVO: filter_scaling_events.py
# DESCRIPCIÓN: Este script filtra eventos relevantes de escalamiento ("Scaled up"
#              y "Scaled down") a partir del log plano generado por el script
#              `capture_deployment_events.sh`, y ajusta los timestamps al momento real
#              del evento con base en el tiempo relativo registrado por Kubernetes.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 30 de marzo de 2025
# CONTEXTO:
#   - Requiere un archivo `scaling_events.csv` generado previamente.
#   - Genera un archivo limpio y estructurado: `scaling_events_clean.csv`
# ------------------------------------------------------------------------------

import pandas as pd
import re
from datetime import datetime, timedelta

# ---------------------------------------------------------------
# CONFIGURACIÓN DE ARCHIVOS DE ENTRADA Y SALIDA
# ---------------------------------------------------------------

file_path = "output/scaling_events.csv"                  # Archivo crudo con eventos recolectados del clúster
output_file = "output/scaling_events_clean.csv"       # Archivo limpio y filtrado que será generado

# ---------------------------------------------------------------
# EXPRESIÓN REGULAR PARA PARSEAR CADA LÍNEA DEL LOG
# ---------------------------------------------------------------
# Extrae:
#   - Timestamp absoluto del log [YYYY-MM-DD HH:MM:SS]
#   - Tiempo relativo del evento dentro de Kubernetes (ej: "37s", "1m23s")
#   - Tipo de evento (Normal/Warning)
#   - Tipo de objeto (ej. "ScalingReplicaSet")
#   - Nombre del deployment
#   - Mensaje de evento generado
pattern = re.compile(r"\[(.*?)\]\s+(\d+[smh]?\d*[smh]?)\s+(\w+)\s+(\w+)\s+deployment/([\w-]+)\s+(.*)")

# ---------------------------------------------------------------
# FUNCIÓN AUXILIAR: Convierte tiempo relativo → timedelta
# ---------------------------------------------------------------
# Kubernetes reporta los eventos con una marca de tiempo relativa como:
# - "37s"  →  37 segundos
# - "1m23s" → 1 minuto y 23 segundos
# - "2m"    → 2 minutos
# - "1h5m"  → 1 hora y 5 minutos
#
# Esta función convierte esas cadenas a un objeto `timedelta` de Python,
# que luego se usa para restar y obtener el timestamp real del evento.
# ---------------------------------------------------------------
def parse_relative_time(time_str):
    # Intentar hacer match con patrones como "1m23s", "2m", "37s", "1h5m"
    match = re.match(r"(\d+)([smh])(\d+)?([smh])?", time_str)
    if not match:
        return timedelta()  # Si no coincide, se asume sin desfase

    # Separar componentes capturados por la expresión regular
    value1, unit1, value2, unit2 = match.groups()
    
    # Convertir valores a enteros
    value1 = int(value1)
    value2 = int(value2) if value2 else 0

    # Inicializar timedelta
    delta = timedelta()

    # Asignar el primer componente temporal
    if unit1 == "s":
        delta += timedelta(seconds=value1)
    elif unit1 == "m":
        delta += timedelta(minutes=value1)
    elif unit1 == "h":
        delta += timedelta(hours=value1)

    # Si existe un segundo componente, agregarlo también
    if unit2:
        if unit2 == "s":
            delta += timedelta(seconds=value2)
        elif unit2 == "m":
            delta += timedelta(minutes=value2)
        elif unit2 == "h":
            delta += timedelta(hours=value2)

    return delta

# ---------------------------------------------------------------
# PARSEO Y FILTRADO DE EVENTOS RELEVANTES
# ---------------------------------------------------------------
events = []

# Leer archivo línea por línea
with open(file_path, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            # Extraer partes de la línea usando la expresión regular
            timestamp_str, relative_time, event_type, _, deployment_name, reason = match.groups()

            # Convertir el timestamp base del log a objeto datetime
            base_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

            # Calcular el timestamp real del evento usando el tiempo relativo
            corrected_timestamp = base_timestamp - parse_relative_time(relative_time)

            # Clasificar el evento como "scaleup" o "scaledown"
            scale_action = "scaleup" if "Scaled up" in reason else "scaledown"

            # Guardar el evento en la lista final
            events.append((corrected_timestamp.strftime("%Y-%m-%d %H:%M:%S"), scale_action, reason))

# ---------------------------------------------------------------
# CONVERSIÓN A DATAFRAME Y EXPORTACIÓN A CSV
# ---------------------------------------------------------------
# Crear DataFrame con columnas adecuadas
df = pd.DataFrame(events, columns=["timestamp", "scale_action", "reason"])

# Eliminar eventos duplicados exactos (mismo timestamp + mensaje)
df = df.drop_duplicates()

# Ordenar eventos cronológicamente
df = df.sort_values(by="timestamp")

# Guardar DataFrame como archivo CSV para análisis y graficación
df.to_csv(output_file, index=False)
