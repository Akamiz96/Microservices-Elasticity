# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve.py
# DESCRIPCIÓN: Genera dos gráficas de elasticidad comparando demanda estimada
#              (basada en VUs y Requests) contra la oferta real de CPU observada.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 2 de abril de 2025
# CONTEXTO:
#   - Utiliza los valores de CPU por VU y CPU por request obtenidos en el microbenchmark.
#   - Permite representar visualmente zonas de over/underprovisioning.
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime, timedelta
import os
from matplotlib.patches import Patch


individual_dir = "images/elasticity"
os.makedirs(individual_dir, exist_ok=True)

# ==============================================================================
# PARÁMETROS MANUALES (CAMBIAR SEGÚN EL MICROBENCHMARK)
# ==============================================================================
cpu_per_vu = 1.50       # millicores por VU
cpu_per_request = 0.05  # millicores por request
requests_per_vu_per_second = 1  # Asumido por diseño del benchmark (1 request/seg por VU)
# ==============================================================================

# ---------------------------------------------------------------
# ETAPA 1: Leer métricas reales de Kubernetes (oferta)
# ---------------------------------------------------------------
df = pd.read_csv("output/basic_metrics.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["cpu(millicores)"] = pd.to_numeric(df["cpu(millicores)"], errors="coerce")
df_supply = df.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

# ---------------------------------------------------------------
# ETAPA 2: Leer el timestamp real de inicio del test
# ---------------------------------------------------------------
with open("output/k6_start_time.txt", "r") as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------
# ETAPA 3: Leer los stages desde archivo externo
# ---------------------------------------------------------------
with open("output/stages.json", "r") as f:
    stages = json.load(f)

# Función auxiliar para convertir "1m", "30s", etc. a segundos
def parse_duration(d):
    unit = d[-1]
    value = int(d[:-1])
    return value * 60 if unit == "m" else value

# Generar VUs y Requests por timestamp
vus_time_series = []
current_time = k6_start_time
prev_target = 0

for stage in stages:
    duration_s = parse_duration(stage["duration"])
    target = stage["target"]
    for t in range(0, duration_s, 10):  # Cada 10 segundos
        progress = t / duration_s
        vus = int(prev_target + (target - prev_target) * progress)
        vus_time_series.append({
            "timestamp": current_time + timedelta(seconds=t),
            "vus": vus,
            "requests": vus * requests_per_vu_per_second * 10  # 10s de intervalo
        })
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_time_series)

# ---------------------------------------------------------------
# ETAPA 4: Calcular demanda estimada (por VU y por Request)
# ---------------------------------------------------------------
df_vus["demand_vu"] = df_vus["vus"] * cpu_per_vu
df_vus["demand_req"] = df_vus["requests"] * cpu_per_request

# ---------------------------------------------------------------
# ETAPA 5: Unir con la oferta observada
# ---------------------------------------------------------------
df_combined = pd.merge_asof(
    df_vus.sort_values("timestamp"),
    df_supply.sort_values("timestamp"),
    on="timestamp",
    direction="nearest",
    tolerance=pd.Timedelta("10s")
)

df_combined.dropna(subset=["supply", "demand_vu", "demand_req"], inplace=True)

# ---------------------------------------------------------------
# ETAPA 6: Obtener nombre del deployment desde el primer pod
# ---------------------------------------------------------------
primer_pod = df["pod"].iloc[0]
deployment_name = "-".join(primer_pod.split("-")[:-2])
subtitle = f"Deployment: {deployment_name}"

# ---------------------------------------------------------------
# ETAPA 7: Función para graficar curva de elasticidad
# ---------------------------------------------------------------
def plot_elasticity_curve(df, demand_col, output_file, title):
    plt.figure(figsize=(14, 7))
    plt.plot(df["timestamp"], df[demand_col], label="Demanda estimada (millicores)", color="red", linewidth=2)
    plt.plot(df["timestamp"], df["supply"], label="Oferta observada (millicores)", color="blue", linewidth=2)

    for i in range(len(df) - 1):
        t0, t1 = df["timestamp"].iloc[i], df["timestamp"].iloc[i+1]
        d0, d1 = df[demand_col].iloc[i], df[demand_col].iloc[i+1]
        s0, s1 = df["supply"].iloc[i], df["supply"].iloc[i+1]
        if d0 > s0:
            plt.fill_between([t0, t1], [s0, s1], [d0, d1], color="orange", alpha=0.3,
                             label="Underprovisioning" if i == 0 else "")
        elif s0 > d0:
            plt.fill_between([t0, t1], [d0, d1], [s0, s1], color="skyblue", alpha=0.3,
                             label="Overprovisioning" if i == 0 else "")

    # Asegurar leyenda completa
    handles, labels = plt.gca().get_legend_handles_labels()
    if "Underprovisioning" not in labels:
        handles.append(Patch(color="orange", alpha=0.3, label="Underprovisioning"))
    if "Overprovisioning" not in labels:
        handles.append(Patch(color="skyblue", alpha=0.3, label="Overprovisioning"))

    plt.xlabel("Tiempo")
    plt.ylabel("CPU (millicores)")
    plt.title(title, fontsize=16)
    plt.suptitle(subtitle, fontsize=10)
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(handles=handles)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# ---------------------------------------------------------------
# ETAPA 8: Generar ambas gráficas
# ---------------------------------------------------------------
os.makedirs("images", exist_ok=True)

plot_elasticity_curve(
    df_combined,
    demand_col="demand_vu",
    output_file="images/elasticity/elasticity_curve_vu.png",
    title="Curva de Elasticidad (Basada en VUs)"
)

plot_elasticity_curve(
    df_combined,
    demand_col="demand_req",
    output_file="images/elasticity/elasticity_curve_req.png",
    title="Curva de Elasticidad (Basada en Requests)"
)
