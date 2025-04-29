# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage_with_events.py
# DESCRIPCIÓN: Graficar el uso de CPU por pod, incluyendo líneas verticales que
#              indican eventos de escalamiento (scaleup y scaledown).
#              Procesa múltiples deployments, generando un gráfico general y
#              gráficos individuales por pod.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para experiments/basic-autoscaling.
#   - Entradas:
#       - experiments/basic-autoscaling/output/basic_metrics_<deployment>.csv
#       - experiments/basic-autoscaling/output/scaling_events_clean_<deployment>.csv
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob

# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================
input_dir = "experiments/basic-autoscaling/output"
images_base_dir = "experiments/basic-autoscaling/images"
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
    # ETAPA 1: CARGA DE MÉTRICAS DE USO DE CPU
    # ==============================================================================
    df = pd.read_csv(metrics_file, delimiter=",", dtype=str, on_bad_lines="skip")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df["%cpu"] = df["%cpu"].str.replace(",", ".", regex=False)
    df["%cpu"] = pd.to_numeric(df["%cpu"], errors="coerce")
    df = df[["timestamp", "pod", "%cpu"]]

    # ==============================================================================
    # ETAPA 2: CARGA DE EVENTOS DE ESCALAMIENTO
    # ==============================================================================
    df_events = pd.read_csv(event_file)
    df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

    # ==============================================================================
    # ETAPA 3: PREPARAR CARPETAS DE SALIDA
    # ==============================================================================
    deployment_img_dir = os.path.join(images_base_dir, deployment_name, "cpu_pod")
    os.makedirs(deployment_img_dir, exist_ok=True)

    # ==============================================================================
    # ETAPA 4: GRAFICO GENERAL CON TODOS LOS PODS DEL DEPLOYMENT
    # ==============================================================================
    pods_unicos = df["pod"].unique()
    palette = sns.color_palette("husl", len(pods_unicos))
    fig, axes = plt.subplots(len(pods_unicos), 1, figsize=(14, 5 * len(pods_unicos)), sharex=True)

    if len(pods_unicos) == 1:
        axes = [axes]

    for i, (pod, color) in enumerate(zip(pods_unicos, palette)):
        pod_df = df[df["pod"] == pod]
        axes[i].plot(pod_df["timestamp"], pod_df["%cpu"], label=f"CPU % - {pod}", marker="o", color=color)
        axes[i].set_ylabel("% CPU")
        axes[i].legend(loc="upper center")
        axes[i].grid()

        # Dibujar eventos de escalamiento
        for _, event in df_events.iterrows():
            line_color = "green" if event["scale_action"] == "scaleup" else "red"
            axes[i].axvline(event["timestamp"], color=line_color, linestyle="--", alpha=0.7)

    axes[-1].set_xlabel("Tiempo")
    plt.xticks(rotation=45)
    plt.suptitle(f"Uso de CPU por Pod – {deployment_name} – Con Eventos de Escalamiento", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    # Guardar gráfico general
    general_output_path = os.path.join(deployment_img_dir, "cpu_usage_per_pod_with_events.png")
    plt.savefig(general_output_path)
    plt.close()

    # ==============================================================================
    # ETAPA 5: GRAFICOS INDIVIDUALES POR POD
    # ==============================================================================
    for idx, (pod, color) in enumerate(zip(pods_unicos, palette), start=1):
        pod_df = df[df["pod"] == pod]

        plt.figure(figsize=(10, 5))
        plt.plot(pod_df["timestamp"], pod_df["%cpu"], label=f"CPU % - {pod}", marker="o", color=color)

        # Dibujar eventos
        for _, event in df_events.iterrows():
            line_color = "green" if event["scale_action"] == "scaleup" else "red"
            plt.axvline(event["timestamp"], color=line_color, linestyle="--", alpha=0.7)

        plt.title(f"Uso de CPU - {pod}")
        plt.xlabel("Tiempo")
        plt.ylabel("% CPU")
        plt.grid()
        plt.tight_layout()
        plt.xticks(rotation=45)

        output_path = os.path.join(deployment_img_dir, f"pod{idx}_cpu_with_events.png")
        plt.savefig(output_path)
        plt.close()
