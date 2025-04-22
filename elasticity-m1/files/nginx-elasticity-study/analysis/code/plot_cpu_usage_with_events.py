# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage_with_events.py
# DESCRIPCIÓN: Graficar el uso de CPU por pod, incluyendo líneas verticales que
#              indican eventos de escalamiento (scaleup y scaledown).
#              Genera un gráfico general + uno individual por pod.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Utilizado en el estudio `exp2_nginx-elasticity-study`.
#   - Usa las variables de entorno:
#       HPA_ID  → configuración del autoscaler (C1-C9)
#       LOAD_ID → patrón de carga aplicado (L01-L06)
#   - Archivos de entrada:
#       output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_metrics.csv
#       output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_events_clean.csv
#   - Resultados:
#       images/HPA_<HPA_ID>_LOAD_<LOAD_ID>/cpu_pod/*.png
# ------------------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------
# LECTURA DE VARIABLES DE ENTORNO
# ---------------------------------------------------------------
HPA_ID = os.getenv("HPA_ID", "C1")
LOAD_ID = os.getenv("LOAD_ID", "L01")

# ---------------------------------------------------------------
# DEFINICIÓN DE RUTAS DE ENTRADA Y SALIDA
# ---------------------------------------------------------------
metrics_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_metrics.csv"
events_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_events_clean.csv"
output_dir = f"images/HPA_{HPA_ID}_LOAD_{LOAD_ID}/cpu_pod"
os.makedirs(output_dir, exist_ok=True)

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
df_events = pd.read_csv(events_file)
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

# ==============================================================================
# ETAPA 3: GRAFICO GENERAL CON TODOS LOS PODS
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

    for _, event in df_events.iterrows():
        line_color = "green" if event["scale_action"] == "scaleup" else "red"
        axes[i].axvline(event["timestamp"], color=line_color, linestyle="--", alpha=0.7)

axes[-1].set_xlabel("Tiempo")
plt.xticks(rotation=45)
plt.title("Uso de CPU por Pod en el Tiempo con Eventos de Escalamiento")
plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig(os.path.join(output_dir, "cpu_usage_per_pod_with_events.png"))
plt.close()

# ==============================================================================
# ETAPA 4: GRAFICOS INDIVIDUALES POR POD
# ==============================================================================
for idx, (pod, color) in enumerate(zip(pods_unicos, palette), start=1):
    pod_df = df[df["pod"] == pod]

    plt.figure(figsize=(10, 5))
    plt.plot(pod_df["timestamp"], pod_df["%cpu"], label=f"CPU % - {pod}", marker="o", color=color)

    for _, event in df_events.iterrows():
        line_color = "green" if event["scale_action"] == "scaleup" else "red"
        plt.axvline(event["timestamp"], color=line_color, linestyle="--", alpha=0.7)

    plt.title(f"Uso de CPU - {pod}")
    plt.xlabel("Tiempo")
    plt.ylabel("% CPU")
    plt.grid()
    plt.tight_layout()
    plt.xticks(rotation=45)

    filename = f"pod{idx}_cpu_with_events.png"
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()
