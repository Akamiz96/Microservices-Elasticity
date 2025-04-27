# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage.py
# DESCRIPCIÓN: Script para graficar el uso de CPU (%) de cada pod durante el
#              microbenchmark. Procesa múltiples archivos de métricas para
#              generar visualizaciones separadas por deployment.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de abril de 2025
# CONTEXTO:
#   - Adaptado para ejecución en contenedor Docker con rutas relativas.
#   - Entrada: output/microbenchmark_metrics_*.csv
#   - Salida:  imágenes en images/<deployment>/
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
input_dir = "output"
output_dir = "images"
os.makedirs(output_dir, exist_ok=True)

# ---------------------------------------------------------------
# PROCESAR TODOS LOS ARCHIVOS DE MÉTRICAS
# ---------------------------------------------------------------
metric_files = glob.glob(os.path.join(input_dir, "microbenchmark_metrics_*.csv"))

for file_path in metric_files:
    # Extraer nombre del deployment a partir del nombre del archivo
    filename = os.path.basename(file_path)
    deployment_name = filename.replace("microbenchmark_metrics_", "").replace(".csv", "")
    print(f"Procesando métricas para deployment: {deployment_name}")

    # Crear carpeta de imágenes para este deployment
    deployment_output_dir = os.path.join(output_dir, deployment_name)
    os.makedirs(deployment_output_dir, exist_ok=True)
    individual_dir = os.path.join(deployment_output_dir, "cpu_pod")
    os.makedirs(individual_dir, exist_ok=True)

    # ---------------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------------
    df = pd.read_csv(file_path, delimiter=",", dtype=str, on_bad_lines="skip")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df["%cpu"] = df["%cpu"].str.replace(",", ".", regex=False)
    df["%cpu"] = pd.to_numeric(df["%cpu"], errors="coerce")
    df = df[["timestamp", "pod", "%cpu"]]

    # ---------------------------------------------------------------
    # GRAFICO PRINCIPAL: Uso de CPU por pod en subgráficos
    # ---------------------------------------------------------------
    pods_unicos = df["pod"].unique()
    palette = sns.color_palette("husl", len(pods_unicos))
    fig, axes = plt.subplots(len(pods_unicos), 1, figsize=(12, 5 * len(pods_unicos)), sharex=True)

    if len(pods_unicos) == 1:
        axes = [axes]

    for i, (pod, color) in enumerate(zip(pods_unicos, palette)):
        pod_df = df[df["pod"] == pod]
        axes[i].plot(pod_df["timestamp"], pod_df["%cpu"], label=f"CPU % - {pod}", marker="o", color=color)
        axes[i].set_ylabel("% CPU")
        axes[i].legend()
        axes[i].grid()

    axes[-1].set_xlabel("Tiempo")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.suptitle(f"CPU Usage per Pod – {deployment_name}", fontsize=16)

    # Guardar gráfico principal
    main_image_path = os.path.join(deployment_output_dir, "cpu_usage_per_pod.png")
    plt.savefig(main_image_path)
    plt.close()

    # ---------------------------------------------------------------
    # GRAFICOS INDIVIDUALES POR POD
    # ---------------------------------------------------------------
    for idx, pod in enumerate(pods_unicos, start=1):
        pod_df = df[df["pod"] == pod]
        plt.figure(figsize=(10, 5))
        plt.plot(pod_df["timestamp"], pod_df["%cpu"], marker="o")
        plt.title(f"CPU Usage - {pod}")
        plt.xlabel("Tiempo")
        plt.ylabel("% CPU")
        plt.grid()
        plt.tight_layout()

        filename = f"pod{idx}_cpu.png"
        path = os.path.join(individual_dir, filename)
        plt.savefig(path)
        plt.close()
