# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count.py
# DESCRIPCIÓN: Script para graficar la evolución del número de pods activos
#              durante la ejecución del experimento `exp2_nginx-elasticity-study`.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Se ejecuta dentro de un contenedor con las variables de entorno:
#       HPA_ID  → configuración del autoscaler (C1-C9)
#       LOAD_ID → patrón de carga aplicado (L01-L06)
#   - Entrada:
#       output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_metrics.csv
#   - Salida:
#       images/HPA_<HPA_ID>_LOAD_<LOAD_ID>/pod_count/pod_count_over_time.png
# ------------------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# LECTURA DE VARIABLES DE ENTORNO
# ---------------------------------------------------------------
HPA_ID = os.getenv("HPA_ID", "C1")
LOAD_ID = os.getenv("LOAD_ID", "L01")

# ---------------------------------------------------------------
# DEFINICIÓN DE RUTAS
# ---------------------------------------------------------------
input_path = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_metrics.csv"
output_dir = f"images/HPA_{HPA_ID}_LOAD_{LOAD_ID}/pod_count"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "pod_count_over_time.png")

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
df = pd.read_csv(input_path, usecols=["timestamp", "num_pods"])
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
plt.savefig(output_path)
plt.close()