# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count.py
# DESCRIPCIÓN: Script para graficar la evolución del número de pods activos
#              durante la ejecución del experimento básico de elasticidad.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Este script forma parte del análisis del experimento `exp1_basic-autoscaling`.
#   - Utiliza como entrada 'output/basic_metrics.csv'.
#   - Guarda la imagen resultante en 'analysis/images/pod_count_over_time.png'.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
file_path = "output/basic_metrics.csv"
df = pd.read_csv(file_path, usecols=["timestamp", "num_pods"])
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

# ---------------------------------------------------------------
# GRAFICO: Evolución del número de pods
# ---------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["num_pods"], label="Pods activos", marker="o")
plt.xlabel("Tiempo")
plt.ylabel("Número de Pods")
plt.title("Número de Pods en el tiempo")
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
