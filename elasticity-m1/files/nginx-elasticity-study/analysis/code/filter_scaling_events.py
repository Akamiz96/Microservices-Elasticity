# ------------------------------------------------------------------------------
# ARCHIVO: filter_scaling_events.py
# DESCRIPCIÓN: Este script filtra eventos relevantes de escalamiento ("Scaled up"
#              y "Scaled down") a partir del log generado por el script
#              `capture_deployment_events.sh`. Ajusta los timestamps usando
#              el tiempo relativo registrado por Kubernetes y el tiempo real
#              del sistema, ignorando eventos previos al inicio de la carga.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Utilizado en el estudio `exp2_nginx-elasticity-study`.
#   - Lee los identificadores de experimento desde las variables de entorno:
#         HPA_ID  → configuración del autoscaler (C1-C9)
#         LOAD_ID → patrón de carga aplicado (L01-L06)
#   - Genera un archivo limpio con eventos de escalamiento filtrados por tiempo.
# ------------------------------------------------------------------------------

import os
import pandas as pd
import re
from datetime import datetime, timedelta

# ---------------------------------------------------------------
# CONFIGURACIÓN DE ARCHIVOS USANDO VARIABLES DE ENTORNO
# ---------------------------------------------------------------
HPA_ID = os.getenv("HPA_ID", "C1")
LOAD_ID = os.getenv("LOAD_ID", "L01")

file_path = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_events.csv"
output_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_events_clean.csv"
k6_start_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_k6_start_time.txt"

# ---------------------------------------------------------------
# EXPRESIÓN REGULAR PARA PARSEAR CADA LÍNEA DEL LOG
# ---------------------------------------------------------------
# Extrae:
#   - Timestamp absoluto del log [YYYY-MM-DD HH:MM:SS]
#   - Tiempo relativo del evento dentro de Kubernetes (ej: "37s", "1m23s")
#   - Tipo de evento (Normal/Warning)
#   - Tipo de objeto (ej. "ScalingReplicaSet")
#   - Nombre del deployment
#   - Mensaje de evento generado por Kubernetes (ej. "Scaled up replica set nginx-6d4c7b8f5b to 2")
pattern = re.compile(r"\[(.*?)\]\s+(\d+[smh]?\d*[smh]?)\s+(\w+)\s+(\w+)\s+deployment/([\w-]+)\s+(.*)")

# ---------------------------------------------------------------
# FUNCIÓN AUXILIAR: Convierte tiempo relativo → timedelta
# ---------------------------------------------------------------}
def parse_relative_time(time_str):
    """
    Convierte una cadena de tiempo relativo de Kubernetes (ej. "1m23s", "2m")
    a un objeto timedelta. Esto permite calcular el timestamp real del evento.
    """
    match = re.match(r"(\d+)([smh])(\d+)?([smh])?", time_str)
    if not match:
        return timedelta()
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
# LECTURA DEL TIMESTAMP DE INICIO DE CARGA K6
# ---------------------------------------------------------------
with open(k6_start_file, "r") as f:
    k6_start_timestamp = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------
# PARSEO Y FILTRADO DE EVENTOS DE ESCALAMIENTO
# ---------------------------------------------------------------
events = []

with open(file_path, "r") as file:
    for line in file:
        match = pattern.search(line)
        if match:
            timestamp_str, relative_time, event_type, _, deployment_name, reason = match.groups()
            base_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            corrected_timestamp = base_timestamp - parse_relative_time(relative_time)
            if corrected_timestamp < k6_start_timestamp:
                continue
            scale_action = "scaleup" if "Scaled up" in reason else "scaledown"
            events.append((corrected_timestamp.strftime("%Y-%m-%d %H:%M:%S"), scale_action, reason))

# ---------------------------------------------------------------
# EXPORTACIÓN A CSV LIMPIO
# ---------------------------------------------------------------
df = pd.DataFrame(events, columns=["timestamp", "scale_action", "reason"])
df = df.drop_duplicates()
df = df.sort_values(by="timestamp")
df.to_csv(output_file, index=False)
