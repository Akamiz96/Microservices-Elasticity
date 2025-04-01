# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage_with_events.py
# DESCRIPCIÓN: Graficar el uso de CPU por pod, incluyendo líneas verticales que
#              indican eventos de escalamiento (scaleup y scaledown).
#              Genera un gráfico general + uno individual por pod.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 29 de marzo de 2025
# CONTEXTO:
#   - Utiliza como entrada:
#       - output/basic_metrics.csv → oferta observada (CPU real).
#       - output/scaling_events_clean.csv → eventos reales del HPA.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==============================================================================
# ETAPA 1: CARGA DE MÉTRICAS DE USO DE CPU
# ==============================================================================
df = pd.read_csv("output/basic_metrics.csv", delimiter=",", dtype=str, on_bad_lines="skip")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df["%cpu"] = df["%cpu"].str.replace(",", ".", regex=False)
df["%cpu"] = pd.to_numeric(df["%cpu"], errors="coerce")
df = df[["timestamp", "pod", "%cpu"]]

# ==============================================================================
# ETAPA 2: CARGA DE EVENTOS DE ESCALAMIENTO
# ==============================================================================
df_events = pd.read_csv("output/scaling_events_clean.csv")
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

    # Dibujar eventos de escalamiento
    for _, event in df_events.iterrows():
        line_color = "green" if event["scale_action"] == "scaleup" else "red"
        axes[i].axvline(event["timestamp"], color=line_color, linestyle="--", alpha=0.7)

axes[-1].set_xlabel("Tiempo")
plt.xticks(rotation=45)
plt.suptitle("Uso de CPU por Pod en el Tiempo con Eventos de Escalamiento", y=0.92)
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Guardar gráfico general
plt.savefig("images/cpu_usage_per_pod_with_events.png")
plt.close()

# ==============================================================================
# ETAPA 4: GRAFICOS INDIVIDUALES POR POD
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

    output_path = f"images/cpu_pod/pod{idx}_cpu_with_events.png"
    plt.savefig(output_path)
    plt.close()
