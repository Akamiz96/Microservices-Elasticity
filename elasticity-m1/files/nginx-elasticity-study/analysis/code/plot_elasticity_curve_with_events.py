# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve_with_events.py
# DESCRIPCIÓN: Genera gráficas de elasticidad comparando demanda estimada
#              (por VU y por request) vs oferta observada, con eventos HPA.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 31 de marzo de 2025
# CONTEXTO:
#   - Entrada:
#       - output/basic_metrics.csv
#       - output/k6_start_time.txt
#       - output/scaling_events_clean.csv
#   - Variables:
#       - cpu_per_vu: obtenido del microbenchmark
#       - cpu_per_req: también estimado previamente
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from matplotlib.patches import Patch
import os
import json

individual_dir = "images/elasticity"
os.makedirs(individual_dir, exist_ok=True)

# ==============================================================================
# PARÁMETROS DEL MICROBENCHMARK (modificar si cambian los valores)
# ==============================================================================
cpu_per_vu = 1.50    # millicores por VU
cpu_per_req = 0.05   # millicores por request
requests_per_vu_per_second = 1  # Asumido por diseño del benchmark (1 request/seg por VU)
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
# ETAPA 2: CARGAR TIMESTAMP DE INICIO DE PRUEBA Y EVENTS HPA
# ---------------------------------------------------------------
with open("output/k6_start_time.txt", "r") as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

df_events = pd.read_csv("output/scaling_events_clean.csv")
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

# ---------------------------------------------------------------
# ETAPA 3: CARGAR STAGES DE CARGA DESDE ARCHIVO
# ---------------------------------------------------------------
with open("output/stages.json", "r") as f:
    stages = json.load(f)

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
    for t in range(0, duration_s, 10):
        progress = t / duration_s
        vus = int(prev_target + (target - prev_target) * progress)
        vus_time_series.append({
            "timestamp": current_time + timedelta(seconds=t),
            "vus": vus,
            "reqs": vus * requests_per_vu_per_second * 10  # 10s de intervalo
        })
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_time_series)

# ---------------------------------------------------------------
# ETAPA 4: Obtener nombre del deployment desde el primer pod
# ---------------------------------------------------------------
primer_pod = df["pod"].iloc[0]
deployment_name = "-".join(primer_pod.split("-")[:-2])
subtitle = f"Deployment: {deployment_name}"

# ---------------------------------------------------------------
# FUNCIÓN PARA GRAFICAR UNA CURVA DE ELASTICIDAD
# ---------------------------------------------------------------
def plot_elasticity(df_combined, metric_label, output_file):
    plt.figure(figsize=(14, 7))
    plt.plot(df_combined["timestamp"], df_combined["demand"], label="Demanda estimada (millicores)", color="red", linewidth=2)
    plt.plot(df_combined["timestamp"], df_combined["supply"], label="Oferta observada (millicores)", color="blue", linewidth=2)

    # Sombrear áreas de over/underprovisioning
    for i in range(len(df_combined) - 1):
        t0, t1 = df_combined["timestamp"].iloc[i], df_combined["timestamp"].iloc[i+1]
        d0, d1 = df_combined["demand"].iloc[i], df_combined["demand"].iloc[i+1]
        s0, s1 = df_combined["supply"].iloc[i], df_combined["supply"].iloc[i+1]
        if d0 > s0:
            plt.fill_between([t0, t1], [s0, s1], [d0, d1], color="orange", alpha=0.3, label="Underprovisioning" if i == 0 else "")
        elif s0 > d0:
            plt.fill_between([t0, t1], [d0, d1], [s0, s1], color="skyblue", alpha=0.3, label="Overprovisioning" if i == 0 else "")

    # Líneas verticales para eventos
    for _, event in df_events.iterrows():
        color = "green" if event["scale_action"] == "scaleup" else "red"
        plt.axvline(event["timestamp"], color=color, linestyle="--", alpha=0.7)

    # Estética y leyenda
    plt.xlabel("Tiempo")
    plt.ylabel("CPU (millicores)")
    plt.suptitle(subtitle, fontsize=10)
    plt.title(f"Curva de Elasticidad con Eventos ({metric_label})")
    plt.xticks(rotation=45)
    plt.grid()

    handles, labels = plt.gca().get_legend_handles_labels()
    if "Underprovisioning" not in labels:
        handles.append(Patch(color="orange", alpha=0.3, label="Underprovisioning"))
    if "Overprovisioning" not in labels:
        handles.append(Patch(color="skyblue", alpha=0.3, label="Overprovisioning"))

    plt.legend(handles=handles)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# ---------------------------------------------------------------
# ETAPA 5: GENERAR Y GUARDAR LAS DOS GRÁFICAS
# ---------------------------------------------------------------
# Demanda basada en VUs
df_vus["demand"] = df_vus["vus"] * cpu_per_vu
df_comb_vu = pd.merge_asof(df_vus.sort_values("timestamp"), df_supply, on="timestamp", direction="nearest", tolerance=pd.Timedelta("10s"))
df_comb_vu.dropna(inplace=True)
plot_elasticity(df_comb_vu, "Basada en VUs", "images/elasticity/elasticity_curve_vus_with_events.png")

# Demanda basada en requests
df_vus["demand"] = df_vus["reqs"] * cpu_per_req
df_comb_req = pd.merge_asof(df_vus.sort_values("timestamp"), df_supply, on="timestamp", direction="nearest", tolerance=pd.Timedelta("10s"))
df_comb_req.dropna(inplace=True)
plot_elasticity(df_comb_req, "Basada en Requests", "images/elasticity/elasticity_curve_reqs_with_events.png")
