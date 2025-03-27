# ------------------------------------------------------------------------------
# ARCHIVO: analyze_microbenchmark.py
# DESCRIPCIÓN: Calcula métricas derivadas del microbenchmark, usando la carga
#              generada por k6 y el consumo de CPU registrado en Kubernetes.
#              Los resultados se imprimen en consola y se guardan en archivo.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Este script complementa los gráficos al ofrecer estimaciones numéricas clave.
#   - El archivo de salida se guarda en 'files/' para que persista vía volumen Docker.
# ------------------------------------------------------------------------------

import json
import pandas as pd
import os

# ---------------------------------------------------------------
# CARGA DE MÉTRICAS DE K6
# ---------------------------------------------------------------
with open("output/k6_summary.json", "r") as f:
    k6_data = json.load(f)

total_requests = k6_data["metrics"]["http_reqs"]["count"]
vus_max = int(k6_data["metrics"]["vus_max"]["value"])

# ---------------------------------------------------------------
# CARGA DE MÉTRICAS DE KUBERNETES
# ---------------------------------------------------------------
df = pd.read_csv("output/microbenchmark_metrics.csv", dtype=str)
df["cpu(millicores)"] = pd.to_numeric(df["cpu(millicores)"], errors="coerce")

# Total de CPU usada (sumando todas las muestras de todos los pods)
cpu_total_millicores = df["cpu(millicores)"].sum()

# ---------------------------------------------------------------
# CÁLCULOS DERIVADOS
# ---------------------------------------------------------------
cpu_per_request = cpu_total_millicores / total_requests if total_requests else 0
cpu_per_vu = cpu_total_millicores / vus_max if vus_max else 0

# ---------------------------------------------------------------
# FORMATO DE SALIDA
# ---------------------------------------------------------------
summary = [
    "📊 Microbenchmark Summary",
    f"Total requests: {total_requests}",
    f"Máximo de VUs: {vus_max}",
    f"Total CPU usada: {cpu_total_millicores:.2f} millicores",
    f"CPU por request: {cpu_per_request:.2f} millicores/request",
    f"CPU por VU: {cpu_per_vu:.2f} millicores/VU"
]

# Imprimir por consola
print("\n".join(summary))

# Guardar en archivo
os.makedirs("files", exist_ok=True)
with open("files/microbenchmark_summary.txt", "w") as out_file:
    out_file.write("\n".join(summary))
