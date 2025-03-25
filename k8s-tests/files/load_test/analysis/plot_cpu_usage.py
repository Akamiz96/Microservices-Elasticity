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

# NOTA IMPORTANTE:
# Si deseas ejecutar este script localmente (fuera de Docker),
# cambia la variable `file_path` a "../output/metrics.csv"
# y `output_path` a "../analysis/images/evolucion_pods.png" o similar.

import pandas as pd
import matplotlib.pyplot as plt
import os

# Ruta dentro del contenedor Docker (ajustar si se ejecuta en local)
file_path = "output/metrics.csv"

# Cargar los datos
df = pd.read_csv(file_path, usecols=["timestamp", "num_pods"])
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

# Crear el gráfico
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["num_pods"], label="Pods en ejecución", marker="o")
plt.xlabel("Tiempo")
plt.ylabel("Número de Pods")
plt.title("Evolución de Pods en el Tiempo")
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()

# Guardar imagen
os.makedirs("images", exist_ok=True)
output_path = "images/evolucion_pods.png"
plt.savefig(output_path)
plt.show()
