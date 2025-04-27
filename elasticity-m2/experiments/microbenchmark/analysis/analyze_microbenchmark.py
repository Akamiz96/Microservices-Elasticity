# ------------------------------------------------------------------------------
# ARCHIVO: analyze_microbenchmark.py
# DESCRIPCIÓN: Calcula métricas derivadas del microbenchmark, usando la carga
#              generada por k6 y el consumo de CPU registrado en Kubernetes.
#              Procesa múltiples deployments de forma separada.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de abril de 2025
# CONTEXTO:
#   - Cada deployment genera su propio resumen en archivos TXT y CSV.
# ------------------------------------------------------------------------------

import json
import pandas as pd
import os
import glob

# ---------------------------------------------------------------
# CARGA DE MÉTRICAS DE K6 (carga generada)
# ---------------------------------------------------------------
with open("output/k6_summary.json", "r") as f:
    k6_data = json.load(f)

total_requests = k6_data["metrics"]["http_reqs"]["count"]
vus_max = int(k6_data["metrics"]["vus_max"]["value"])

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
input_dir = "output"
output_dir = "files"
os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------------
# PROCESAR TODOS LOS ARCHIVOS DE MÉTRICAS
# ---------------------------------------------------------------
metric_files = glob.glob(os.path.join(input_dir, "microbenchmark_metrics_*.csv"))

for file_path in metric_files:
    # Extraer nombre del deployment a partir del nombre del archivo
    filename = os.path.basename(file_path)
    deployment_name = filename.replace("microbenchmark_metrics_", "").replace(".csv", "")
    print(f"Analizando métricas para deployment: {deployment_name}")

    # Crear carpeta de salida específica para este deployment
    deployment_output_dir = os.path.join(output_dir, deployment_name)
    os.makedirs(deployment_output_dir, exist_ok=True)

    # ---------------------------------------------------------------
    # CARGA DE MÉTRICAS DE KUBERNETES
    # ---------------------------------------------------------------
    df = pd.read_csv(file_path, dtype=str)
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
        f"📊 Microbenchmark Summary – {deployment_name}",
        f"Total requests: {total_requests}",
        f"Máximo de VUs: {vus_max}",
        f"Total CPU usada: {cpu_total_millicores:.2f} millicores",
        f"CPU por request: {cpu_per_request:.2f} millicores/request",
        f"CPU por VU: {cpu_per_vu:.2f} millicores/VU"
    ]

    # Imprimir por consola
    print("\n".join(summary))

    # Guardar resumen en texto plano
    txt_path = os.path.join(deployment_output_dir, "microbenchmark_summary.txt")
    with open(txt_path, "w") as out_file:
        out_file.write("\n".join(summary))

    # Guardar también en CSV estructurado
    csv_path = os.path.join(deployment_output_dir, "microbenchmark_summary.csv")
    csv_data = pd.DataFrame([{
        "deployment": deployment_name,
        "total_requests": total_requests,
        "vus_max": vus_max,
        "cpu_total_millicores": round(cpu_total_millicores, 2),
        "cpu_per_request": round(cpu_per_request, 4),
        "cpu_per_vu": round(cpu_per_vu, 4)
    }])

    csv_data.to_csv(csv_path, index=False)
