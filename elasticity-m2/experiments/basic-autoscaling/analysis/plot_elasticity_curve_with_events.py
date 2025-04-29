# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve_with_events.py
# DESCRIPCIÓN: Genera gráficas de elasticidad con eventos de escalamiento
#              para cada microservicio, comparando demanda y oferta de CPU.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para experiments/basic-autoscaling
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import os
from matplotlib.patches import Patch

# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================
input_dir = "experiments/basic-autoscaling/output"
output_dir_base = "experiments/basic-autoscaling/images"

# Definiciones específicas por deployment
microservices = {
    "flask-app": {
        "cpu_per_vu": 24.80,
        "cpu_per_req": 0.82
    },
    "nginx-app": {
        "cpu_per_vu": 1.80,
        "cpu_per_req": 0.06
    }
}

requests_per_vu_per_second = 1
sampling_interval = 10

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def parse_duration(duration_str):
    unit = duration_str[-1]
    value = int(duration_str[:-1])
    return value * 60 if unit == "m" else int(value)

def plot_elasticity(df_combined, df_events, metric_label, output_file, subtitle):
    plt.figure(figsize=(14, 7))
    plt.plot(df_combined["timestamp"], df_combined["demand"], label="Demanda estimada (millicores)", color="red", linewidth=2)
    plt.plot(df_combined["timestamp"], df_combined["supply"], label="Oferta observada (millicores)", color="blue", linewidth=2)

    for i in range(len(df_combined) - 1):
        t0, t1 = df_combined["timestamp"].iloc[i], df_combined["timestamp"].iloc[i+1]
        d0, d1 = df_combined["demand"].iloc[i], df_combined["demand"].iloc[i+1]
        s0, s1 = df_combined["supply"].iloc[i], df_combined["supply"].iloc[i+1]
        if d0 > s0:
            plt.fill_between([t0, t1], [s0, s1], [d0, d1], color="orange", alpha=0.3, label="Underprovisioning" if i == 0 else "")
        elif s0 > d0:
            plt.fill_between([t0, t1], [d0, d1], [s0, s1], color="skyblue", alpha=0.3, label="Overprovisioning" if i == 0 else "")

    for _, event in df_events.iterrows():
        color = "green" if event["scale_action"] == "scaleup" else "red"
        plt.axvline(event["timestamp"], color=color, linestyle="--", alpha=0.7)

    handles, labels = plt.gca().get_legend_handles_labels()
    if "Underprovisioning" not in labels:
        handles.append(Patch(color="orange", alpha=0.3, label="Underprovisioning"))
    if "Overprovisioning" not in labels:
        handles.append(Patch(color="skyblue", alpha=0.3, label="Overprovisioning"))

    plt.xlabel("Tiempo")
    plt.ylabel("CPU (millicores)")
    plt.title(f"Curva de Elasticidad con Eventos ({metric_label})", fontsize=16)
    plt.suptitle(subtitle, fontsize=10)
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(handles=handles)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# ==============================================================================
# ETAPA 1: Cargar tiempos de inicio de k6 y stages
# ==============================================================================
with open(os.path.join(input_dir, "k6_start_time.txt")) as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

with open(os.path.join(input_dir, "stages.json")) as f:
    stages = json.load(f)

# Generar la serie de VUs y requests
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
            "reqs": vus * requests_per_vu_per_second * sampling_interval
        })
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_series)

# ==============================================================================
# ETAPA 2: Procesar cada microservicio
# ==============================================================================
for deployment_name, params in microservices.items():
    print(f"[INFO] Generando elasticidad con eventos para: {deployment_name}")

    metrics_file = os.path.join(input_dir, f"basic_metrics_{deployment_name}.csv")
    events_file = os.path.join(input_dir, f"scaling_events_clean_{deployment_name}.csv")

    if not os.path.exists(metrics_file) or not os.path.exists(events_file):
        print(f"[Warning] Faltan archivos para {deployment_name}, se omite.")
        continue

    # Cargar métricas
    df_metrics = pd.read_csv(metrics_file)
    df_metrics["timestamp"] = pd.to_datetime(df_metrics["timestamp"])
    df_metrics["cpu(millicores)"] = pd.to_numeric(df_metrics["cpu(millicores)"], errors="coerce")
    df_supply = df_metrics.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
    df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

    df_events = pd.read_csv(events_file)
    df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

    elasticity_dir = os.path.join(output_dir_base, deployment_name, "elasticity")
    os.makedirs(elasticity_dir, exist_ok=True)

    # Demanda basada en VUs
    df_vus_vu = df_vus.copy()
    df_vus_vu["demand"] = df_vus_vu["vus"] * params["cpu_per_vu"]
    df_comb_vu = pd.merge_asof(df_vus_vu.sort_values("timestamp"), df_supply, on="timestamp", direction="nearest", tolerance=pd.Timedelta(seconds=sampling_interval))
    df_comb_vu.dropna(inplace=True)
    plot_elasticity(
        df_combined=df_comb_vu,
        df_events=df_events,
        metric_label="Basada en VUs",
        output_file=os.path.join(elasticity_dir, "elasticity_curve_vus_with_events.png"),
        subtitle=f"Deployment: {deployment_name}"
    )

    # Demanda basada en Requests
    df_vus_req = df_vus.copy()
    df_vus_req["demand"] = df_vus_req["reqs"] * params["cpu_per_req"]
    df_comb_req = pd.merge_asof(df_vus_req.sort_values("timestamp"), df_supply, on="timestamp", direction="nearest", tolerance=pd.Timedelta(seconds=sampling_interval))
    df_comb_req.dropna(inplace=True)
    plot_elasticity(
        df_combined=df_comb_req,
        df_events=df_events,
        metric_label="Basada en Requests",
        output_file=os.path.join(elasticity_dir, "elasticity_curve_req_with_events.png"),
        subtitle=f"Deployment: {deployment_name}"
    )
