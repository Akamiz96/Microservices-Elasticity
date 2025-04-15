# ------------------------------------------------------------------------------
# ARCHIVO: plot_cpu_usage.py
# DESCRIPCIÓN: Script para graficar el uso de CPU (%) de cada pod durante la
#              ejecución del experimento `exp2_nginx-elasticity-study`.
#              Genera una visualización compuesta y gráficos individuales por pod.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Se ejecuta dentro de un contenedor con las variables de entorno:
#       HPA_ID  → configuración del autoscaler (C1-C9)
#       LOAD_ID → patrón de carga aplicado (L01-L06)
#   - Utiliza como entrada el archivo:
#       output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_metrics.csv
#   - Guarda los resultados en:
#       images/HPA_<HPA_ID>_LOAD_<LOAD_ID>/cpu_pod/
# ------------------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------
# LECTURA DE IDENTIFICADORES DESDE VARIABLES DE ENTORNO
# ---------------------------------------------------------------
HPA_ID = os.getenv("HPA_ID", "C1")
LOAD_ID = os.getenv("LOAD_ID", "L01")

# ---------------------------------------------------------------
# DEFINICIÓN DE RUTAS DE ENTRADA Y SALIDA
# ---------------------------------------------------------------
file_path = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_metrics.csv"
output_base = f"images/HPA_{HPA_ID}_LOAD_{LOAD_ID}/cpu_pod"

# Crear las carpetas de salida si no existen
os.makedirs(output_base, exist_ok=True)

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
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
plt.suptitle("Uso de CPU por pod a lo largo del tiempo", fontsize=16)

# ---------------------------------------------------------------
# GUARDAR GRAFICO PRINCIPAL
# ---------------------------------------------------------------
main_image_path = os.path.join(output_base, "cpu_usage_per_pod.png")
plt.savefig(main_image_path)
plt.show()

# ---------------------------------------------------------------
# GRAFICOS INDIVIDUALES POR POD
# ---------------------------------------------------------------
for idx, pod in enumerate(pods_unicos, start=1):
    pod_df = df[df["pod"] == pod]
    plt.figure(figsize=(10, 5))
    plt.plot(pod_df["timestamp"], pod_df["%cpu"], marker="o")
    plt.title(f"Uso de CPU - {pod}")
    plt.xlabel("Tiempo")
    plt.ylabel("% CPU")
    plt.grid()
    plt.tight_layout()

    filename = f"pod{idx}_cpu.png"
    path = os.path.join(output_base, filename)
    plt.savefig(path)
    plt.close()
