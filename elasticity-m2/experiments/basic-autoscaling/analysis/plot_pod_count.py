# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count.py
# DESCRIPCIÓN: Script para graficar la evolución del número de pods en ejecución
#              durante el microbenchmark de carga en Kubernetes. Procesa múltiples
#              archivos de métricas para generar visualizaciones separadas por deployment.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de abril de 2025
# CONTEXTO:
#   - Adaptado para ejecución dentro de contenedor Docker con rutas relativas.
#   - Entrada: output/microbenchmark_metrics_*.csv
#   - Salida:  imágenes en images/<deployment>/
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
input_dir = "output"
output_dir = "images/cpu_pod"
os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------------
# PROCESAR TODOS LOS ARCHIVOS DE MÉTRICAS
# ---------------------------------------------------------------
metric_files = glob.glob(os.path.join(input_dir, "basic_metrics_*.csv"))

for file_path in metric_files:
    # Extraer nombre del deployment a partir del nombre del archivo
    filename = os.path.basename(file_path)
    deployment_name = filename.replace("basic_metrics_", "").replace(".csv", "")
    print(f"Procesando evolución de pods para deployment: {deployment_name}")

    # Crear carpeta de salida para este deployment
    deployment_output_dir = os.path.join(output_dir, deployment_name)
    os.makedirs(deployment_output_dir, exist_ok=True)

    # ---------------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------------
    df = pd.read_csv(file_path, usecols=["timestamp", "num_pods"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

    # ---------------------------------------------------------------
    # GRAFICO: Evolución del número de pods
    # ---------------------------------------------------------------
    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["num_pods"], label="Active Pods", marker="o")
    plt.xlabel("Tiempo")
    plt.ylabel("Número de Pods")
    plt.title(f"Pod Count Over Time – {deployment_name}")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardado de la imagen
    output_path = os.path.join(deployment_output_dir, "pod_count_over_time.png")
    plt.savefig(output_path)
    plt.close()
