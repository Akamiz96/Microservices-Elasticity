# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage.py
# DESCRIPCIÓN: Script para graficar el uso de CPU (%) de cada pod durante una
#              prueba de carga. Los datos se leen desde un archivo CSV generado
#              por el script de recolección de métricas.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   - Este script se usa dentro de un contenedor Docker para generar gráficos
#     automáticamente, pero también puede ejecutarse en local.
# ------------------------------------------------------------------------------

# NOTA IMPORTANTE:
# Si deseas ejecutar este script localmente (fuera de Docker),
# cambia la variable `file_path` a "../output/metrics.csv"
# y `output_path` a "../analysis/images/cpu_por_pod.png" o similar.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ruta dentro del contenedor Docker (ajustar si se ejecuta en local)
file_path = "output/metrics.csv"

# Cargar los datos
df = pd.read_csv(file_path, delimiter=",", dtype=str, on_bad_lines="skip")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df["%cpu"] = df["%cpu"].str.replace(",", ".", regex=False)
df["%cpu"] = pd.to_numeric(df["%cpu"], errors="coerce")
df = df[["timestamp", "pod", "%cpu"]]

# Preparar visualización
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
plt.suptitle("Uso de CPU por Pod en el Tiempo", y=0.90)
plt.xticks(rotation=45)
plt.tight_layout()

# Guardar imagen
os.makedirs("images", exist_ok=True)
output_path = "images/cpu_por_pod.png"
plt.savefig(output_path)
plt.show()
