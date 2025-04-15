# ------------------------------------------------------------------------------
# ARCHIVO: plot_elasticity_curve_with_events.py
# DESCRIPCIÓN: Genera gráficas de elasticidad comparando demanda estimada
#              (por VU y por request) vs oferta observada, con eventos HPA.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Parte del estudio `exp2_nginx-elasticity-study`.
#   - Entradas (personalizadas por experimento):
#       - output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_metrics.csv
#       - output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_events_clean.csv
#       - output/HPA_<HPA_ID>_LOAD_<LOAD_ID>_k6_start_time.txt
#       - k6_configs/<LOAD_ID>_config.json
#   - Salidas:
#       - images/HPA_<HPA_ID>_LOAD_<LOAD_ID>/elasticity/*.png
# ------------------------------------------------------------------------------

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.patches import Patch

# ==============================================================================
# ETAPA 1: LECTURA DE VARIABLES Y CONFIGURACIÓN
# ==============================================================================
HPA_ID = os.getenv("HPA_ID", "C1")
LOAD_ID = os.getenv("LOAD_ID", "L01")

# ==============================================================================
# PARÁMETROS DEL MICROBENCHMARK (modificar si cambian los valores)
# ==============================================================================
cpu_per_vu = 1.50    # millicores por VU
cpu_per_req = 0.05   # millicores por request
requests_per_vu_per_second = 1  # Asumido por diseño del benchmark (1 request/seg por VU)
# ==============================================================================

# Definición de rutas de entrada y salida
metrics_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_metrics.csv"
events_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_events_clean.csv"
k6_start_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_k6_start_time.txt"
config_file = f"k6_configs/{LOAD_ID}_config.json"
output_dir = f"images/HPA_{HPA_ID}_LOAD_{LOAD_ID}/elasticity"
os.makedirs(output_dir, exist_ok=True)

# ==============================================================================
# ETAPA 2: CARGA DE MÉTRICAS DE CPU OBSERVADA (oferta real)
# ==============================================================================
df = pd.read_csv(metrics_file)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["cpu(millicores)"] = pd.to_numeric(df["cpu(millicores)"], errors="coerce")
df_supply = df.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

# ==============================================================================
# ETAPA 3: CARGA DE EVENTOS DE ESCALAMIENTO Y TIMESTAMP DE INICIO
# ==============================================================================
with open(k6_start_file, "r") as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

df_events = pd.read_csv(events_file)
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

# ==============================================================================
# ETAPA 4: GENERACIÓN DE LA SERIE TEMPORAL DE DEMANDA
# ==============================================================================
with open(config_file, "r") as f:
    config = json.load(f)
stages = config["stages"]

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
            "reqs": vus * requests_per_vu_per_second * 10
        })
    prev_target = target
    current_time += timedelta(seconds=duration_s)

df_vus = pd.DataFrame(vus_time_series)

# ==============================================================================
# ETAPA 5: IDENTIFICAR NOMBRE DEL DEPLOYMENT (para título de gráficas)
# ==============================================================================
primer_pod = df["pod"].iloc[0]
deployment_name = "-".join(primer_pod.split("-")[:-2])
subtitle = f"Deployment: {deployment_name}"

# ==============================================================================
# ETAPA 6: FUNCIÓN PARA GRAFICAR CURVAS CON EVENTOS DE ESCALAMIENTO
# ==============================================================================
def plot_elasticity(df_combined, metric_label, output_file):
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

    # Dibujar líneas de eventos
    for _, event in df_events.iterrows():
        color = "green" if event["scale_action"] == "scaleup" else "red"
        plt.axvline(event["timestamp"], color=color, linestyle="--", alpha=0.7)

    plt.xlabel("Tiempo")
    plt.ylabel("CPU (millicores)")
    plt.title(f"Curva de Elasticidad con Eventos ({metric_label})")
    plt.suptitle(subtitle, fontsize=10)
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

# ==============================================================================
# ETAPA 7: GENERAR GRÁFICAS (VUs y Requests)
# ==============================================================================
df_vus["demand"] = df_vus["vus"] * cpu_per_vu
df_comb_vu = pd.merge_asof(df_vus.sort_values("timestamp"), df_supply, on="timestamp", direction="nearest", tolerance=pd.Timedelta("10s"))
df_comb_vu.dropna(inplace=True)
plot_elasticity(df_comb_vu, "Basada en VUs", os.path.join(output_dir, "elasticity_curve_vus_with_events.png"))

df_vus["demand"] = df_vus["reqs"] * cpu_per_req
df_comb_req = pd.merge_asof(df_vus.sort_values("timestamp"), df_supply, on="timestamp", direction="nearest", tolerance=pd.Timedelta("10s"))
df_comb_req.dropna(inplace=True)
plot_elasticity(df_comb_req, "Basada en Requests", os.path.join(output_dir, "elasticity_curve_reqs_with_events.png"))
