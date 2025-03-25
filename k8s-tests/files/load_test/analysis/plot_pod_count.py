# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count.py
# DESCRIPCIÓN: Script en Python para graficar la evolución del número de pods en ejecución
#              durante una prueba de carga. Se basa en los datos recolectados por el script
#              metric_collector.sh, específicamente en la columna `num_pods`.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   - Permite observar visualmente cómo Kubernetes (a través del HPA) reacciona
#     ante cambios en la carga generada, ajustando dinámicamente el número de pods.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------

# Ruta del archivo CSV generado por el script de recolección de métricas
file_path = "../output/metrics.csv"  # Ajustar si se ejecuta desde otra ubicación

# Leer solo las columnas necesarias
df = pd.read_csv(file_path, usecols=["timestamp", "num_pods"])

# Convertir la columna timestamp a formato datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Convertir columna num_pods a numérica
df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

# ---------------------------------------------------------------
# VISUALIZACIÓN: Evolución del número de pods en el tiempo
# ---------------------------------------------------------------

plt.figure(figsize=(12, 6))

# Graficar número de pods activos
plt.plot(df["timestamp"], df["num_pods"], label="Pods en ejecución", marker="o")

# Personalización del gráfico
plt.xlabel("Tiempo")
plt.ylabel("Número de Pods")
plt.title("Evolución de Pods en el Tiempo")
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()

# ---------------------------------------------------------------
# GUARDAR IMAGEN EN LA CARPETA DE ANÁLISIS
# ---------------------------------------------------------------

# Ruta de salida para guardar el gráfico
output_dir = "images"
output_path = os.path.join(output_dir, "evolucion_pods.png")

# Crear directorio si no existe
os.makedirs(output_dir, exist_ok=True)

# Guardar la figura como imagen
plt.savefig(output_path)

# Mostrar la figura (opcional)
plt.show()
