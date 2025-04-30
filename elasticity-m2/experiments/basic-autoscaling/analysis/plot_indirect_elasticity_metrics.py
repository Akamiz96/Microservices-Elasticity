# ------------------------------------------------------------------------------
# ARCHIVO: plot_indirect_elasticity_metrics.py
# DESCRIPCIÓN: Generación de gráficas de métricas indirectas (latencia, errores,
#              throughput) junto con eventos de escalamiento para evaluar el
#              comportamiento de elasticidad del sistema.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para experiments/basic-autoscaling.
#   - Entrada:
#       - output/k6_results.csv
#       - output/scaling_events_clean_nginx-app.csv
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# =============================
# CONFIGURACIÓN INICIAL
# =============================

# Rutas de entrada y salida
input_dir = "output"
output_dir = "images/indirect_metrics"

INPUT_CSV = os.path.join(input_dir, "k6_results.csv")
EVENTS_CSV = os.path.join(input_dir, "scaling_events_clean_nginx-app.csv")  # Usamos eventos de NGINX
K6_START_FILE = os.path.join(input_dir, "k6_start_time.txt")

# Crear carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Leer el tiempo real de inicio del experimento desde el archivo externo
with open(K6_START_FILE, "r") as f:
    k6_start_time = pd.to_datetime(f.read().strip())

# =============================
# CARGA Y PROCESAMIENTO DE DATOS
# =============================

# Leer resultados de k6 y convertir timestamps
df_k6 = pd.read_csv(INPUT_CSV)
df_k6["timestamp"] = pd.to_datetime(df_k6["timestamp"], unit="s")
offset = k6_start_time - df_k6["timestamp"].min()
df_k6["timestamp"] += offset

# Agrupar métricas y pivotear
grouped = df_k6.groupby(["timestamp", "metric_name"]).agg({"metric_value": "mean"}).reset_index()
pivoted = grouped.pivot(index="timestamp", columns="metric_name", values="metric_value").fillna(0)

# Leer eventos de escalamiento de nginx
df_events = pd.read_csv(EVENTS_CSV)
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

def add_scaling_event_lines(ax, df_events):
    """
    Agrega líneas verticales al gráfico para indicar eventos de escalamiento.

    Parámetros:
    - ax (matplotlib.axes.Axes): Eje sobre el cual se agregan las líneas.
    - df_events (pd.DataFrame): DataFrame con columnas 'timestamp' y 'scale_action'.
    """
    for _, event in df_events.iterrows():
        color = "green" if event["scale_action"] == "scaleup" else "red"
        ax.axvline(x=event["timestamp"], color=color, linestyle="--", alpha=0.7)

# =============================
# 1. LATENCIA PROMEDIO
# =============================

# Latencia promedio sin eventos
fig1, ax1 = plt.subplots(figsize=(10, 4))
pivoted["http_req_duration"].plot(ax=ax1)
ax1.set_title("Latencia Promedio a lo largo del tiempo")
ax1.set_ylabel("Duración (s)")
ax1.set_xlabel("Tiempo")
fig1.savefig(os.path.join(output_dir, "latency_avg.png"))

# Latencia promedio con eventos
fig1e, ax1e = plt.subplots(figsize=(10, 4))
pivoted["http_req_duration"].plot(ax=ax1e)
add_scaling_event_lines(ax1e, df_events)
ax1e.set_title("Latencia Promedio con eventos de escalamiento")
ax1e.set_ylabel("Duración (s)")
ax1e.set_xlabel("Tiempo")
fig1e.savefig(os.path.join(output_dir, "latency_avg_events.png"))

# =============================
# 2. ERRORES HTTP POR SEGUNDO
# =============================

errors_series = pd.Series(0, index=pivoted.index, name="Errores")

# Errores sin eventos
fig2, ax2 = plt.subplots(figsize=(10, 4))
errors_series.plot(ax=ax2)
ax2.set_title("Errores HTTP por segundo")
ax2.set_ylabel("Errores")
ax2.set_xlabel("Tiempo")
fig2.savefig(os.path.join(output_dir, "http_errors.png"))

# Errores con eventos
fig2e, ax2e = plt.subplots(figsize=(10, 4))
errors_series.plot(ax=ax2e)
add_scaling_event_lines(ax2e, df_events)
ax2e.set_title("Errores HTTP con eventos de escalamiento")
ax2e.set_ylabel("Errores")
ax2e.set_xlabel("Tiempo")
fig2e.savefig(os.path.join(output_dir, "http_errors_events.png"))

# =============================
# 3. REQUESTS POR SEGUNDO (THROUGHPUT)
# =============================

# Throughput sin eventos
fig3, ax3 = plt.subplots(figsize=(10, 4))
pivoted["http_reqs"].plot(ax=ax3)
ax3.set_title("Requests por segundo (Throughput)")
ax3.set_ylabel("Requests/s")
ax3.set_xlabel("Tiempo")
fig3.savefig(os.path.join(output_dir, "throughput.png"))

# Throughput con eventos
fig3e, ax3e = plt.subplots(figsize=(10, 4))
pivoted["http_reqs"].plot(ax=ax3e)
add_scaling_event_lines(ax3e, df_events)
ax3e.set_title("Throughput con eventos de escalamiento")
ax3e.set_ylabel("Requests/s")
ax3e.set_xlabel("Tiempo")
fig3e.savefig(os.path.join(output_dir, "throughput_events.png"))

# =============================
# 4. THROUGHPUT VS VUs
# =============================

vus_df = df_k6[df_k6["metric_name"] == "vus"].groupby("timestamp").agg({"metric_value": "mean"})
rps_df = df_k6[df_k6["metric_name"] == "http_reqs"].groupby("timestamp").agg({"metric_value": "mean"})

merged = pd.merge(vus_df, rps_df, left_index=True, right_index=True, suffixes=("_vus", "_rps"))

# Gráfico scatter throughput vs VUs
fig4, ax4 = plt.subplots(figsize=(6, 6))
sns.scatterplot(data=merged, x="metric_value_vus", y="metric_value_rps", ax=ax4)
ax4.set_title("Throughput vs VUs")
ax4.set_xlabel("VUs")
ax4.set_ylabel("Requests/s")
fig4.savefig(os.path.join(output_dir, "throughput_vs_vus.png"))
