# ------------------------------------------------------------------------------
# ARCHIVO: plot_pod_count_with_events.py
# DESCRIPCIÓN: Grafica la evolución del número de pods durante la prueba de carga,
#              incluyendo líneas verticales que indican eventos de escalamiento
#              (scaleup / scaledown) del deployment.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 29 de marzo de 2025
# CONTEXTO:
#   - Requiere:
#       - output/basic_metrics.csv → para graficar número de pods en el tiempo.
#       - analysis/files/filtered_deployment_events.csv → para los eventos HPA.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------
# CARGA DE MÉTRICAS DE NÚMERO DE PODS
# ---------------------------------------------------------------
df = pd.read_csv("output/basic_metrics.csv", usecols=["timestamp", "num_pods"])
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["num_pods"] = pd.to_numeric(df["num_pods"], errors="coerce")

# ---------------------------------------------------------------
# CARGA DE EVENTOS DE ESCALAMIENTO
# ---------------------------------------------------------------
df_events = pd.read_csv("files/filtered_deployment_events.csv")
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

# ---------------------------------------------------------------
# GRAFICO: Evolución del número de pods con eventos de escalamiento
# ---------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["num_pods"], label="Active Pods", marker="o", linewidth=2)

# Dibujar líneas verticales para eventos
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
os.makedirs("images", exist_ok=True)
output_path = "images/pod_count_over_time_with_events.png"
plt.savefig(output_path)
plt.close()
