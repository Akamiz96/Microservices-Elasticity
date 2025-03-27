# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count.py
# DESCRIPCIÓN: Script para graficar la evolución del número de pods en ejecución
#              durante el microbenchmark de carga en Kubernetes.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Adaptado para ejecución dentro de contenedor Docker con rutas relativas.
#   - Entrada: output/microbenchmark_metrics.csv
#   - Salida:  imagen generada en images/
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
file_path = "output/microbenchmark_metrics.csv"
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
plt.title("Pod Count Over Time – Microbenchmark")
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
