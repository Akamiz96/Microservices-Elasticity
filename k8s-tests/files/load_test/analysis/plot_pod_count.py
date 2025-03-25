# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count.py
# DESCRIPCIÓN: Script para graficar la evolución del número de pods en ejecución
#              durante una prueba de carga basada en Kubernetes.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   - Este script se ejecuta automáticamente dentro de un contenedor Docker
#     como parte del análisis de resultados, pero también puede usarse en local.
# ------------------------------------------------------------------------------

# NOTA:
# Si deseas ejecutar este script localmente, cambia 'output/metrics.csv'
# por '../output/metrics.csv' y guarda la imagen en '../analysis/images/'.

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
file_path = "output/metrics.csv"
df = pd.read_csv(file_path, usecols=["timestamp", "num_pods"])
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

# ---------------------------------------------------------------
# GRAFICO: Evolución del número de pods
# ---------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["num_pods"], label="Active Pods", marker="o")
plt.xlabel("Time")
plt.ylabel("Number of Pods")
plt.title("Pod Count Over Time")
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()

# ---------------------------------------------------------------
# GUARDADO DE LA IMAGEN
# ---------------------------------------------------------------
os.makedirs("images", exist_ok=True)
output_path = "images/pod_count_over_time.png"
plt.savefig(output_path)
plt.show()
