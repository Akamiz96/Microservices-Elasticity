# ------------------------------------------------------------------------------
# ARCHIVO: calculate_elasticity_metrics.py
# DESCRIPCIÓN: Cálculo de métricas de elasticidad específicas para cada
#              microservicio desplegado en Kubernetes.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para experiments/basic-autoscaling.
#   - Entrada:
#       - output/basic_metrics_<deployment>.csv
#       - output/scaling_events_clean_<deployment>.csv
#       - output/stages.json
# ------------------------------------------------------------------------------

import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
import os

# ============================================================================
# CONFIGURACIÓN GENERAL
# ============================================================================

input_dir = "output"
output_dir = "files"

LOAD_ID = os.getenv("LOAD_ID", "L01")
config_file = f"k6_configs/{LOAD_ID}_config.json"

# Verificar si el directorio de salida existe, si no, crearlo
os.makedirs(output_dir, exist_ok=True)

# Parámetros generales
requests_per_vu_per_second = 1
sampling_interval = 10
reconfig_threshold = 30

# Parámetros específicos por deployment
microservices = {
    "flask-app": {
        "cpu_per_request": 0.82,   # millicores
        "cpu_per_vu": 24.80         # millicores
    },
    "nginx-app": {
        "cpu_per_request": 0.06,
        "cpu_per_vu": 1.80
    }
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def calcular_tiempo_reconfiguracion(events_csv, threshold_seconds=30):
    df = pd.read_csv(events_csv, parse_dates=["timestamp"])
    df = df.sort_values("timestamp")
    resultados = []

    for tipo in ["scaleup", "scaledown"]:
        sub = df[df["scale_action"] == tipo].copy()
        sub["delta"] = sub["timestamp"].diff().dt.total_seconds().fillna(threshold_seconds + 1)
        grupo_id = 0
        grupo_ids = []

        for delta in sub["delta"]:
            if delta > threshold_seconds:
                grupo_id += 1
            grupo_ids.append(grupo_id)

        sub["grupo"] = grupo_ids
        for grupo, grupo_df in sub.groupby("grupo"):
            start = grupo_df["timestamp"].min()
            end = grupo_df["timestamp"].max()
            duracion = (end - start).total_seconds()
            resultados.append({
                "tipo": tipo,
                "grupo": grupo,
                "start": start,
                "end": end,
                "duracion": duracion,
                "eventos": len(grupo_df)
            })

    df_bloques = pd.DataFrame(resultados)
    θ_up = df_bloques[df_bloques["tipo"] == "scaleup"]["duracion"].sum()
    θ_down = df_bloques[df_bloques["tipo"] == "scaledown"]["duracion"].sum()
    return θ_up, θ_down, df_bloques

def calcular_metricas(df_demand, label, output_path, df_supply, θ_up, θ_down, df_bloques):
    df_comb = pd.merge_asof(
        df_demand.sort_values("timestamp"),
        df_supply,
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(seconds=sampling_interval)
    )
    df_comb.dropna(inplace=True)

    T = df_comb["timestamp"].max() - df_comb["timestamp"].min()
    T_seconds = T.total_seconds()
    T_minutes = T_seconds / 60

    df_comb["under"] = df_comb["demand"] - df_comb["supply"]
    df_comb["under"] = df_comb["under"].apply(lambda x: x if x > 0 else 0)

    df_comb["over"] = df_comb["supply"] - df_comb["demand"]
    df_comb["over"] = df_comb["over"].apply(lambda x: x if x > 0 else 0)

    ΣU = df_comb["under"].sum() * sampling_interval
    ΣO = df_comb["over"].sum() * sampling_interval

    under_periods = df_comb[df_comb["under"] > 0]
    over_periods = df_comb[df_comb["over"] > 0]

    ΣA = len(under_periods) * sampling_interval
    ΣB = len(over_periods) * sampling_interval

    A_bar = ΣA / T_seconds if T_seconds > 0 else 0
    B_bar = ΣB / T_seconds if T_seconds > 0 else 0
    U_bar = ΣU / ΣA if ΣA > 0 else 0
    O_bar = ΣO / ΣB if ΣB > 0 else 0

    P_u = ΣU / T_seconds if T_seconds > 0 else 0
    P_d = ΣO / T_seconds if T_seconds > 0 else 0

    E_u = 1 / (A_bar * U_bar) if A_bar * U_bar > 0 else 0
    E_d = 1 / (B_bar * O_bar) if B_bar * O_bar > 0 else 0

    θ = θ_up + θ_down
    μ = (ΣU + ΣO) / (T_seconds * len(df_comb)) if len(df_comb) > 0 else 0
    E_l = 1 / (θ * μ) if θ * μ > 0 else 0

    E_global = 1 - ((ΣU + ΣO) / T_seconds) if T_seconds > 0 else 0
    R_U = ΣU / T_seconds if T_seconds > 0 else 0
    R_O = ΣO / T_seconds if T_seconds > 0 else 0
    theta_pct = (θ / T_seconds) * 100 if T_seconds > 0 else 0
    theta_up_pct = (θ_up / T_seconds) * 100 if T_seconds > 0 else 0
    theta_down_pct = (θ_down / T_seconds) * 100 if T_seconds > 0 else 0
    tiempo_util = 100 - theta_pct

    with open(output_path, "w") as f:
        f.write(f"=== MÉTRICAS DE ELASTICIDAD ({label}) ===\n\n")
        f.write(f"Duración total: {T} ({T_seconds:.2f} s, {T_minutes:.2f} min)\n\n")
        f.write(f"ΣU: {ΣU:.2f} millicore-s\nΣO: {ΣO:.2f} millicore-s\n\n")
        f.write(f"Tiempo en reconfiguración (θ): {θ:.2f} s\n")
        f.write(f"  - ScaleUp: {θ_up:.2f} s\n  - ScaleDown: {θ_down:.2f} s\n\n")
        f.write(f"Tiempos de sub/sobreaprovisionamiento:\n")
        f.write(f"  - ΣA: {ΣA:.2f} s | A̅: {A_bar:.2f} | Ū: {U_bar:.2f}\n")
        f.write(f"  - ΣB: {ΣB:.2f} s | B̅: {B_bar:.2f} | Ō: {O_bar:.2f}\n\n")
        f.write(f"Precisión:\n")
        f.write(f"  - Pᵤ: {P_u:.4f} | P𝑑: {P_d:.4f}\n\n")
        f.write(f"Elasticidades parciales:\n")
        f.write(f"  - Eᵤ: {E_u:.4f} | E𝑑: {E_d:.4f}\n\n")
        f.write(f"Elasticidad total (Eₗ): {E_l:.4f}\n\n")
        f.write(f"Elasticidad Global (E): {E_global:.4f}\n")
        f.write(f"R_U: {R_U:.4f} | R_O: {R_O:.4f}\n")
        f.write(f"Porcentaje reconfiguración (θ%%): {theta_pct:.2f}% (Up: {theta_up_pct:.2f}% / Down: {theta_down_pct:.2f}%)\n")
        f.write(f"Tiempo útil del sistema: {tiempo_util:.2f}%\n\n")
        f.write("Bloques de reconfiguración detectados:\n")
        for _, row in df_bloques.iterrows():
            f.write(f"  - [{row['tipo']}] {row['start']} → {row['end']} ({row['duracion']:.1f}s, {row['eventos']} eventos)\n")

# ============================================================================
# ETAPA PRINCIPAL: Calcular para cada microservicio
# ============================================================================

# Leer inicio de k6 y etapas
with open(os.path.join(input_dir, "k6_start_time.txt")) as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

with open(config_file) as f:
    stages = json.load(f)

def parse_duration(d): return int(d[:-1]) * (60 if d.endswith("m") else 1)

vus_series = []
current_time = k6_start_time
prev_target = 0

for stage in stages:
    duration = parse_duration(stage["duration"])
    target = stage["target"]
    for t in range(0, duration, sampling_interval):
        progress = t / duration
        vus = int(prev_target + (target - prev_target) * progress)
        vus_series.append({
            "timestamp": current_time + timedelta(seconds=t),
            "vus": vus,
            "reqs": vus * requests_per_vu_per_second * sampling_interval
        })
    prev_target = target
    current_time += timedelta(seconds=duration)

df_vus = pd.DataFrame(vus_series)

for deployment, params in microservices.items():
    print(f"[INFO] Procesando métricas para: {deployment}")

    metrics_file = os.path.join(input_dir, f"basic_metrics_{deployment}.csv")
    events_file = os.path.join(input_dir, f"scaling_events_clean_{deployment}.csv")

    if not os.path.exists(metrics_file) or not os.path.exists(events_file):
        print(f"[Warning] Faltan archivos para {deployment}, se omite.")
        continue

    df_metrics = pd.read_csv(metrics_file)
    df_metrics["timestamp"] = pd.to_datetime(df_metrics["timestamp"])
    df_metrics["cpu(millicores)"] = pd.to_numeric(df_metrics["cpu(millicores)"], errors="coerce")
    df_supply = df_metrics.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
    df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

    θ_up, θ_down, df_bloques = calcular_tiempo_reconfiguracion(events_file, threshold_seconds=reconfig_threshold)

    # Por VUs
    df_vus_vu = df_vus.copy()
    df_vus_vu["demand"] = df_vus_vu["vus"] * params["cpu_per_vu"]
    output_path_vus = os.path.join(output_dir, f"elasticity_metrics_vus_{deployment}.txt")
    calcular_metricas(df_vus_vu, f"Basado en VUs – {deployment}", output_path_vus, df_supply, θ_up, θ_down, df_bloques)

    # Por requests
    df_vus_req = df_vus.copy()
    df_vus_req["demand"] = df_vus_req["reqs"] * params["cpu_per_request"]
    output_path_req = os.path.join(output_dir, f"elasticity_metrics_requests_{deployment}.txt")
    calcular_metricas(df_vus_req, f"Basado en Requests – {deployment}", output_path_req, df_supply, θ_up, θ_down, df_bloques)
