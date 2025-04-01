# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve_with_events.py
# DESCRIPCIÓN: Genera una gráfica de elasticidad comparando la demanda estimada
#              con la oferta observada, incorporando líneas verticales que
#              indican los eventos de escalamiento (scaleup/scaledown).
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 29 de marzo de 2025
# CONTEXTO:
#   - Utiliza como entrada:
#       - output/basic_metrics.csv → oferta observada (CPU real).
#       - output/k6_start_time.txt → timestamp inicial del experimento.
#       - output/scaling_events_clean.csv → eventos reales del HPA.
#   - La demanda se simula desde los stages de k6 y el CPU por VU
#     obtenido del microbenchmark.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# ==============================================================================
# IMPORTANTE: AJUSTAR SEGÚN MICROBENCHMARK
# ==============================================================================
cpu_per_vu = 1.50  # millicores por VU (valor estimado a partir del microbenchmark)
# ==============================================================================

# ---------------------------------------------------------------
# ETAPA 1: CARGAR MÉTRICAS OBSERVADAS DE KUBERNETES
# ---------------------------------------------------------------
df = pd.read_csv("output/basic_metrics.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["cpu(millicores)"] = pd.to_numeric(df["cpu(millicores)"], errors="coerce")

df_supply = df.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

# ---------------------------------------------------------------
# ETAPA 2: LEER TIMESTAMP REAL DE INICIO DEL TEST
# ---------------------------------------------------------------
with open("output/k6_start_time.txt", "r") as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------
# ETAPA 3: CONSTRUIR LA CURVA DE DEMANDA SIMULADA
# ---------------------------------------------------------------
stages = [
    {"duration": "1m", "target": 50},
    {"duration": "3m", "target": 150},
    {"duration": "2m", "target": 50},
    {"duration": "1m", "target": 0},
]

def parse_duration(duration_str):
    unit = duration_str[-1]
    value = int(duration_str[:-1])
    return value * 60 if unit == "m" else int(value)

vus_time_series = []
current_time = k6_start_time
prev_target = 0

for stage in stages:
    duration_s = parse_duration(stage["duration"])
    target = stage["target"]
    for t in range(0, duration_s, 10):  # Paso de 10 segundos
        progress = t / duration_s
        vus = int(prev_target + (target - prev_target) * progress)
        timestamp = current_time + timedelta(seconds=t)
        vus_time_series.append({"timestamp": timestamp, "vus": vus})
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_time_series)
df_vus["demand"] = df_vus["vus"] * cpu_per_vu

# ---------------------------------------------------------------
# ETAPA 4: UNIR DEMANDA Y OFERTA EN UNA SOLA SERIE TEMPORAL
# ---------------------------------------------------------------
df_combined = pd.merge_asof(
    df_vus.sort_values("timestamp"),
    df_supply.sort_values("timestamp"),
    on="timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("10s")
)

# ---------------------------------------------------------------
# ETAPA 5: CARGA DE EVENTOS DE ESCALAMIENTO
# ---------------------------------------------------------------
df_events = pd.read_csv("output/scaling_events_clean.csv")
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

# ---------------------------------------------------------------
# ETAPA 6: GRAFICAR CURVA DE ELASTICIDAD + EVENTOS
# ---------------------------------------------------------------
plt.figure(figsize=(14, 7))
plt.plot(df_combined["timestamp"], df_combined["demand"], label="Demanda estimada (millicores)", color="red", linewidth=2)
plt.plot(df_combined["timestamp"], df_combined["supply"], label="Oferta observada (millicores)", color="blue", linewidth=2)

# Zonas de over/underprovisioning
for i in range(len(df_combined) - 1):
    t0, t1 = df_combined["timestamp"].iloc[i], df_combined["timestamp"].iloc[i+1]
    d0, d1 = df_combined["demand"].iloc[i], df_combined["demand"].iloc[i+1]
    s0, s1 = df_combined["supply"].iloc[i], df_combined["supply"].iloc[i+1]
    if d0 > s0:
        plt.fill_between([t0, t1], [s0, s1], [d0, d1], color="orange", alpha=0.3, label="Underprovisioning" if i == 0 else "")
    elif s0 > d0:
        plt.fill_between([t0, t1], [d0, d1], [s0, s1], color="skyblue", alpha=0.3, label="Overprovisioning" if i == 0 else "")

# Eventos HPA: líneas verticales
for _, event in df_events.iterrows():
    color = "green" if event["scaling_direction"] == "scaleup" else "red"
    plt.axvline(event["timestamp"], color=color, linestyle="--", alpha=0.7, linewidth=1.2)

plt.xlabel("Tiempo")
plt.ylabel("CPU (millicores)")
plt.title("Curva de Elasticidad con Eventos de Escalamiento")
plt.xticks(rotation=45)
plt.grid()
plt.legend()
plt.tight_layout()

# ---------------------------------------------------------------
# GUARDAR LA IMAGEN
# ---------------------------------------------------------------
os.makedirs("images", exist_ok=True)
plt.savefig("images/elasticity_curve_with_events.png")
plt.show()
