# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count_with_events.py
# DESCRIPCIÓN: Grafica la evolución del número de pods durante la prueba de carga,
#              incluyendo líneas verticales que indican eventos de escalamiento
#              (scaleup / scaledown) para cada deployment.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para experiments/basic-autoscaling.
#   - Entrada:
#       - output/basic_metrics_<deployment>.csv
#       - output/scaling_events_clean_<deployment>.csv
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================
input_dir = "output"
images_base_dir = "images/pod_count"
os.makedirs(images_base_dir, exist_ok=True)

# Buscar todos los eventos disponibles
event_files = glob.glob(os.path.join(input_dir, "scaling_events_clean_*.csv"))

# ==============================================================================
# PROCESAR CADA DEPLOYMENT
# ==============================================================================
for event_file in event_files:
    # Extraer nombre del deployment
    filename = os.path.basename(event_file)
    deployment_name = filename.replace("scaling_events_clean_", "").replace(".csv", "")

    # Ruta específica de métricas de este deployment
    metrics_file = os.path.join(input_dir, f"basic_metrics_{deployment_name}.csv")

    # Verificar que exista el archivo de métricas correspondiente
    if not os.path.exists(metrics_file):
        print(f"[Warning] No se encontró archivo de métricas para {deployment_name}. Se omite.")
        continue

    # ==============================================================================
    # ETAPA 1: CARGA DE MÉTRICAS DE NÚMERO DE PODS
    # ==============================================================================
    df = pd.read_csv(metrics_file, usecols=["timestamp", "num_pods"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

    # ==============================================================================
    # ETAPA 2: CARGA DE EVENTOS DE ESCALAMIENTO
    # ==============================================================================
    df_events = pd.read_csv(event_file)
    df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

    # ==============================================================================
    # ETAPA 3: PREPARAR CARPETA DE SALIDA
    # ==============================================================================
    deployment_img_dir = os.path.join(images_base_dir, deployment_name, "pod_count")
    os.makedirs(deployment_img_dir, exist_ok=True)

    # ==============================================================================
    # ETAPA 4: GRAFICO DE EVOLUCIÓN DE NÚMERO DE PODS
    # ==============================================================================
    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["num_pods"], label="Active Pods", marker="o", linewidth=2)

    # Dibujar líneas verticales para eventos de escalamiento
    for _, event in df_events.iterrows():
        color = "green" if event["scale_action"] == "scaleup" else "red"
        plt.axvline(x=event["timestamp"], color=color, linestyle="--", alpha=0.7)

    plt.xlabel("Tiempo")
    plt.ylabel("Número de Pods")
    plt.title(f"Evolución del Número de Pods – {deployment_name}")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardado de la imagen
    output_path = os.path.join(deployment_img_dir, "pod_count_over_time_with_events.png")
    plt.savefig(output_path)
    plt.close()
