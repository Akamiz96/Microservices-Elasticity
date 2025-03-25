# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage.py
# DESCRIPCIÓN: Script en Python para visualizar el uso de CPU por pod a lo largo
#              del tiempo, a partir de datos registrados durante una prueba de carga.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   - Este gráfico permite analizar cómo se distribuye y varía la carga de CPU
#     entre los pods gestionados por Kubernetes.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------------------------------------------------------
# CARGA Y PROCESAMIENTO DE DATOS
# ---------------------------------------------------------------

# Ruta relativa al archivo CSV generado por metric_collector.sh
file_path = "../output/metrics.csv"  # Ajustar si se mueve el script

# Cargar datos como DataFrame
df = pd.read_csv(file_path, delimiter=",", dtype=str, on_bad_lines="skip")

# Convertir columnas necesarias a tipos adecuados
df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df["%cpu"] = df["%cpu"].str.replace(",", ".", regex=False)
df["%cpu"] = pd.to_numeric(df["%cpu"], errors="coerce")

# Filtrar columnas relevantes
df = df[["timestamp", "pod", "%cpu"]]

# ---------------------------------------------------------------
# VISUALIZACIÓN: Uso de CPU por pod en el tiempo
# ---------------------------------------------------------------

pods_unicos = df["pod"].unique()
palette = sns.color_palette("husl", len(pods_unicos))
fig, axes = plt.subplots(len(pods_unicos), 1, figsize=(12, 5 * len(pods_unicos)), sharex=True)

# Asegurar que axes sea iterable
if len(pods_unicos) == 1:
    axes = [axes]

# Crear gráfico por cada pod
for i, (pod, color) in enumerate(zip(pods_unicos, palette)):
    pod_df = df[df["pod"] == pod]
    axes[i].plot(pod_df["timestamp"], pod_df["%cpu"], label=f"CPU % - {pod}", marker="o", color=color)
    axes[i].set_ylabel("% CPU")
    axes[i].legend()
    axes[i].grid()

# Configuración general del gráfico
axes[-1].set_xlabel("Tiempo")
plt.suptitle("Uso de CPU por Pod en el Tiempo", y=0.90)
plt.xticks(rotation=45)
plt.tight_layout()

# ---------------------------------------------------------------
# GUARDADO DE LA IMAGEN
# ---------------------------------------------------------------

# Ruta donde se guardará el gráfico
output_dir = "images"
output_path = os.path.join(output_dir, "cpu_por_pod.png")

# Crear directorio si no existe
os.makedirs(output_dir, exist_ok=True)

# Guardar gráfico como imagen PNG
plt.savefig(output_path)

# Mostrar gráfico en pantalla
plt.show()
