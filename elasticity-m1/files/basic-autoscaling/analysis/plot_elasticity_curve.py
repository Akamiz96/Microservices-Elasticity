# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve.py
# DESCRIPCIÓN: Genera una gráfica de elasticidad comparando demanda estimada
#              (basada en VUs simulados y microbenchmark) contra la oferta real
#              de CPU recolectada por Kubernetes durante el experimento.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Utiliza como entrada:
#       - output/basic_metrics.csv (recolección real de CPU por pod)
#       - output/k6_start_time.txt (inicio real del test)
#   - La demanda se calcula a partir de los stages de k6 + cpu_per_vu del benchmark
#   - La gráfica se guarda en analysis/images/elasticity_curve.png
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from matplotlib.patches import Patch

# ==============================================================================
# IMPORTANTE: MODIFICAR SEGÚN MICROBENCHMARK
# ==============================================================================
cpu_per_vu = 1.50  # millicores por VU (valor obtenido del microbenchmark)
# ==============================================================================

# ---------------------------------------------------------------
# ETAPA 1: Leer métricas observadas desde Kubernetes
# ---------------------------------------------------------------
df = pd.read_csv("output/basic_metrics.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["cpu(millicores)"] = pd.to_numeric(df["cpu(millicores)"], errors="coerce")

# Agrupar por timestamp (suma de CPU por momento)
df_supply = df.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

# ---------------------------------------------------------------
# ETAPA 2: Leer el timestamp real de inicio del test
# ---------------------------------------------------------------
with open("output/k6_start_time.txt", "r") as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------
# ETAPA 3: Simular los VUs esperados por timestamp a partir de los stages
# ---------------------------------------------------------------
# Stages manuales desde basic_load_test.js
# ==============================================================================
# IMPORTANTE: MODIFICAR SEGÚN basic_load_test.js
# ==============================================================================
stages = [
    {"duration": "1m", "target": 50},
    {"duration": "3m", "target": 150},
    {"duration": "2m", "target": 50},
    {"duration": "1m", "target": 0},
]

# Convertir duraciones a segundos
def parse_duration(d):
    unit = d[-1]
    value = int(d[:-1])
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    return 0

vus_time_series = []
current_time = k6_start_time
prev_target = 0

for stage in stages:
    duration_s = parse_duration(stage["duration"])
    target = stage["target"]
    for t in range(0, duration_s, 10):  # cada 10 segundos
        progress = t / duration_s
        vus = int(prev_target + (target - prev_target) * progress)
        vus_time_series.append({"timestamp": current_time + timedelta(seconds=t), "vus": vus})
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_time_series)

# ---------------------------------------------------------------
# ETAPA 4: Calcular demanda estimada a partir de VUs
# ---------------------------------------------------------------
df_vus["demand"] = df_vus["vus"] * cpu_per_vu

# ---------------------------------------------------------------
# ETAPA 5: Unir demanda y oferta por timestamp
# ---------------------------------------------------------------
df_combined = pd.merge_asof(
    df_vus.sort_values("timestamp"),
    df_supply.sort_values("timestamp"),
    on="timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("10s")
)


# ✅ Eliminar filas incompletas para evitar cortes en la gráfica
df_combined.dropna(subset=["demand", "supply"], inplace=True)

# ---------------------------------------------------------------
# ETAPA 6: Graficar curva de elasticidad
# ---------------------------------------------------------------
plt.figure(figsize=(14, 7))
plt.plot(df_combined["timestamp"], df_combined["demand"], label="Demanda estimada (millicores)", color="red", linewidth=2)
plt.plot(df_combined["timestamp"], df_combined["supply"], label="Oferta observada (millicores)", color="blue", linewidth=2)

# Sombrear zonas de over/underprovisioning
for i in range(len(df_combined) - 1):
    t0, t1 = df_combined["timestamp"].iloc[i], df_combined["timestamp"].iloc[i+1]
    d0, d1 = df_combined["demand"].iloc[i], df_combined["demand"].iloc[i+1]
    s0, s1 = df_combined["supply"].iloc[i], df_combined["supply"].iloc[i+1]
    if d0 > s0:
        plt.fill_between([t0, t1], [s0, s1], [d0, d1], color="orange", alpha=0.3, label="Underprovisioning" if i == 0 else "")
    elif s0 > d0:
        plt.fill_between([t0, t1], [d0, d1], [s0, s1], color="skyblue", alpha=0.3, label="Overprovisioning" if i == 0 else "")


# Crear parches personalizados si alguna categoría no apareció primero
handles, labels = plt.gca().get_legend_handles_labels()

if "Underprovisioning" not in labels:
    handles.append(Patch(color="orange", alpha=0.3, label="Underprovisioning"))

if "Overprovisioning" not in labels:
    handles.append(Patch(color="skyblue", alpha=0.3, label="Overprovisioning"))

# ---------------------------------------------------------------
# SUBTÍTULO: Nombre del deployment a partir del nombre del pod
# ---------------------------------------------------------------
primer_pod = df["pod"].iloc[0]
deployment_name = "-".join(primer_pod.split("-")[:-2])  # Elimina sufijos de replicaset
subtitle = f"Deployment: {deployment_name}"

plt.xlabel("Tiempo")
plt.ylabel("CPU (millicores)")
plt.title("Curva de Elasticidad: Demanda vs Oferta", fontsize=16)
plt.suptitle(subtitle, fontsize=10)
plt.xticks(rotation=45)
plt.grid()
plt.legend(handles=handles)
plt.tight_layout()

# ---------------------------------------------------------------
# GUARDAR LA GRÁFICA
# ---------------------------------------------------------------
os.makedirs("images", exist_ok=True)
plt.savefig("images/elasticity_curve.png")
plt.show()
