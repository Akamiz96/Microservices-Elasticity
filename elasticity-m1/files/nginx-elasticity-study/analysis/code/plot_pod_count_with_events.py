# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count_with_events.py
# DESCRIPCIÓN: Grafica la evolución del número de pods durante la prueba de carga,
#              incluyendo líneas verticales que indican eventos de escalamiento
#              (scaleup / scaledown) del deployment.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Utilizado en el estudio `exp2_nginx-elasticity-study`.
#   - Variables de entorno:
#       HPA_ID  → configuración del autoscaler (C1-C9)
#       LOAD_ID → patrón de carga aplicado (L01-L06)
#   - Archivos requeridos:
#       output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_metrics.csv
#       output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_events_clean.csv
#   - Salida:
#       images/HPA_<HPA_ID>_LOAD_<LOAD_ID>/pod_count/pod_count_over_time_with_events.png
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
input_metrics = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_metrics.csv"
input_events = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_events_clean.csv"
output_dir = f"images/HPA_{HPA_ID}_LOAD_{LOAD_ID}/pod_count"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "pod_count_over_time_with_events.png")

# ---------------------------------------------------------------
# CARGA DE MÉTRICAS DE NÚMERO DE PODS
# ---------------------------------------------------------------
df = pd.read_csv(input_metrics, usecols=["timestamp", "num_pods"])
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

# ---------------------------------------------------------------
# CARGA DE EVENTOS DE ESCALAMIENTO
# ---------------------------------------------------------------
df_events = pd.read_csv(input_events)
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

# ---------------------------------------------------------------
# GRAFICO: Evolución del número de pods con eventos de escalamiento
# ---------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["num_pods"], label="Active Pods", marker="o", linewidth=2)

for _, event in df_events.iterrows():
    color = "green" if event["scale_action"] == "scaleup" else "red"
    plt.axvline(x=event["timestamp"], color=color, linestyle="--", alpha=0.7)

plt.xlabel("Tiempo")
plt.ylabel("Número de Pods")
plt.title("Evolución del Número de Pods con Eventos de Escalamiento")
plt.legend()
plt.grid()
plt.xticks(rotation=45)
plt.tight_layout()

# ---------------------------------------------------------------
# GUARDADO DE LA IMAGEN
# ---------------------------------------------------------------
plt.savefig(output_path)
plt.close()
