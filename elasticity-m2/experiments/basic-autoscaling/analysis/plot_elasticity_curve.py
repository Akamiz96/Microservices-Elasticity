# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve.py
# DESCRIPCIÓN: Genera gráficas de elasticidad para cada microservicio,
#              comparando demanda estimada (por VU y por request) vs oferta real.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para experiments/basic-autoscaling.
#   - Entrada:
#       - output/basic_metrics_<deployment>.csv
#       - output/scaling_events_clean_<deployment>.csv
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime, timedelta
import os
from matplotlib.patches import Patch
import glob

# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================
input_dir = "experiments/basic-autoscaling/output"
output_dir_base = "experiments/basic-autoscaling/images"
os.makedirs(output_dir_base, exist_ok=True)

# Definiciones específicas por deployment
microservices = {
    "flask-app": {
        "cpu_per_vu": 24.80,    # millicores
        "cpu_per_request": 0.82
    },
    "nginx-app": {
        "cpu_per_vu": 1.80,
        "cpu_per_request": 0.06
    }
}

requests_per_vu_per_second = 1
sampling_interval = 10

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def parse_duration(d):
    unit = d[-1]
    value = int(d[:-1])
    return value * 60 if unit == "m" else value

def plot_elasticity_curve(df, demand_col, output_file, title, subtitle):
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

# ==============================================================================
# ETAPA 1: Cargar el tiempo de inicio y los stages
# ==============================================================================
with open(os.path.join(input_dir, "k6_start_time.txt")) as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

with open(os.path.join(input_dir, "stages.json")) as f:
    stages = json.load(f)

# Generar la serie de VUs y requests a lo largo del tiempo
vus_series = []
current_time = k6_start_time
prev_target = 0

for stage in stages:
    duration_s = parse_duration(stage["duration"])
    target = stage["target"]
    for t in range(0, duration_s, sampling_interval):
        progress = t / duration_s
        vus = int(prev_target + (target - prev_target) * progress)
        vus_series.append({
            "timestamp": current_time + timedelta(seconds=t),
            "vus": vus,
            "requests": vus * requests_per_vu_per_second * sampling_interval
        })
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_series)

# ==============================================================================
# ETAPA 2: Procesar cada microservicio
# ==============================================================================
for deployment_name, params in microservices.items():
    print(f"[INFO] Procesando curvas de elasticidad para: {deployment_name}")

    metrics_file = os.path.join(input_dir, f"basic_metrics_{deployment_name}.csv")

    if not os.path.exists(metrics_file):
        print(f"[Warning] No se encontró {metrics_file}. Se omite {deployment_name}.")
        continue

    # ---------------------------------------------------------------
    # ETAPA 2.1: Cargar oferta observada (supply)
    # ---------------------------------------------------------------
    df = pd.read_csv(metrics_file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["cpu(millicores)"] = pd.to_numeric(df["cpu(millicores)"], errors="coerce")
    df_supply = df.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
    df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

    # ---------------------------------------------------------------
    # ETAPA 2.2: Calcular demanda basada en VUs y Requests
    # ---------------------------------------------------------------
    df_vus_copy = df_vus.copy()
    df_vus_copy["demand_vu"] = df_vus_copy["vus"] * params["cpu_per_vu"]
    df_vus_copy["demand_req"] = df_vus_copy["requests"] * params["cpu_per_request"]

    # ---------------------------------------------------------------
    # ETAPA 2.3: Combinar demanda y oferta
    # ---------------------------------------------------------------
    df_combined = pd.merge_asof(
        df_vus_copy.sort_values("timestamp"),
        df_supply.sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(seconds=sampling_interval)
    )
    df_combined.dropna(subset=["supply", "demand_vu", "demand_req"], inplace=True)

    # ---------------------------------------------------------------
    # ETAPA 2.4: Crear carpeta de salida para el deployment
    # ---------------------------------------------------------------
    elasticity_dir = os.path.join(output_dir_base, deployment_name, "elasticity")
    os.makedirs(elasticity_dir, exist_ok=True)

    # ---------------------------------------------------------------
    # ETAPA 2.5: Graficar curvas
    # ---------------------------------------------------------------
    plot_elasticity_curve(
        df_combined,
        demand_col="demand_vu",
        output_file=os.path.join(elasticity_dir, "elasticity_curve_vu.png"),
        title="Curva de Elasticidad (Basada en VUs)",
        subtitle=f"Deployment: {deployment_name}"
    )

    plot_elasticity_curve(
        df_combined,
        demand_col="demand_req",
        output_file=os.path.join(elasticity_dir, "elasticity_curve_req.png"),
        title="Curva de Elasticidad (Basada en Requests)",
        subtitle=f"Deployment: {deployment_name}"
    )
