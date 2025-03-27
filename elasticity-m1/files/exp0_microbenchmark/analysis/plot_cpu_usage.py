# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage.py
# DESCRIPCIÓN: Script para graficar el uso de CPU (%) de cada pod durante el
#              microbenchmark. Genera una visualización general y gráficos
#              individuales por pod.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Adaptado para ejecución en contenedor Docker con rutas relativas.
#   - Entrada: output/microbenchmark_metrics.csv
#   - Salida:  imágenes en images/
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
file_path = "output/microbenchmark_metrics.csv"
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
plt.suptitle("CPU Usage per Pod – Microbenchmark", fontsize=16)

# ---------------------------------------------------------------
# GUARDAR GRAFICO PRINCIPAL
# ---------------------------------------------------------------
output_dir = "images"
os.makedirs(output_dir, exist_ok=True)
main_image_path = os.path.join(output_dir, "cpu_usage_per_pod.png")
plt.savefig(main_image_path)
plt.show()

# ---------------------------------------------------------------
# GRAFICOS INDIVIDUALES POR POD
# ---------------------------------------------------------------
individual_dir = os.path.join(output_dir, "cpu_pod")
os.makedirs(individual_dir, exist_ok=True)

for idx, pod in enumerate(pods_unicos, start=1):
    pod_df = df[df["pod"] == pod]
    plt.figure(figsize=(10, 5))
    plt.plot(pod_df["timestamp"], pod_df["%cpu"], marker="o")
    plt.title(f"CPU Usage - {pod}")
    plt.xlabel("Time")
    plt.ylabel("% CPU")
    plt.grid()
    plt.tight_layout()

    filename = f"pod{idx}_cpu.png"
    path = os.path.join(individual_dir, filename)
    plt.savefig(path)
    plt.close()
