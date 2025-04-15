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
#   - Excluye eventos previos al inicio de la carga (según `k6_start_time.txt`).
#   - Genera un archivo limpio y estructurado: `scaling_events_clean.csv`.
# ------------------------------------------------------------------------------

import pandas as pd
import re
from datetime import datetime, timedelta

# ---------------------------------------------------------------
# CONFIGURACIÓN DE ARCHIVOS DE ENTRADA Y SALIDA
# ---------------------------------------------------------------
file_path = "output/scaling_events.csv"                  # Archivo crudo con eventos recolectados del clúster
output_file = "output/scaling_events_clean.csv"          # Archivo limpio que será generado
k6_start_file = "output/k6_start_time.txt"               # Archivo con timestamp del inicio real de la prueba

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
def parse_relative_time(time_str):
    """
    Convierte una cadena de tiempo relativo de Kubernetes (ej. "1m23s", "2m")
    a un objeto timedelta. Esto permite calcular el timestamp real del evento.
    """
    match = re.match(r"(\d+)([smh])(\d+)?([smh])?", time_str)
    if not match:
        return timedelta()  # Si no coincide el patrón, se asume cero

    value1, unit1, value2, unit2 = match.groups()
    value1 = int(value1)
    value2 = int(value2) if value2 else 0

    delta = timedelta()
    if unit1 == "s":
        delta += timedelta(seconds=value1)
    elif unit1 == "m":
        delta += timedelta(minutes=value1)
    elif unit1 == "h":
        delta += timedelta(hours=value1)

    if unit2:
        if unit2 == "s":
            delta += timedelta(seconds=value2)
        elif unit2 == "m":
            delta += timedelta(minutes=value2)
        elif unit2 == "h":
            delta += timedelta(hours=value2)

    return delta

# ---------------------------------------------------------------
# LECTURA DE FECHA DE INICIO DE CARGA DESDE K6
# ---------------------------------------------------------------
with open(k6_start_file, "r") as f:
    k6_start_timestamp = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------
# PARSEO Y FILTRADO DE EVENTOS RELEVANTES
# ---------------------------------------------------------------
events = []

# Leer archivo línea por línea
with open(file_path, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            timestamp_str, relative_time, event_type, _, deployment_name, reason = match.groups()
            base_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            corrected_timestamp = base_timestamp - parse_relative_time(relative_time)

            # Filtrar eventos que ocurrieron antes del inicio del test con k6
            if corrected_timestamp < k6_start_timestamp:
                continue

            # Clasificar el evento como "scaleup" o "scaledown"
            scale_action = "scaleup" if "Scaled up" in reason else "scaledown"

            # Guardar evento válido
            events.append((corrected_timestamp.strftime("%Y-%m-%d %H:%M:%S"), scale_action, reason))

# ---------------------------------------------------------------
# CONVERSIÓN A DATAFRAME Y EXPORTACIÓN A CSV
# ---------------------------------------------------------------
df = pd.DataFrame(events, columns=["timestamp", "scale_action", "reason"])
df = df.drop_duplicates()                   # Eliminar duplicados exactos
df = df.sort_values(by="timestamp")        # Orden cronológico
df.to_csv(output_file, index=False)        # Guardar resultados limpios
