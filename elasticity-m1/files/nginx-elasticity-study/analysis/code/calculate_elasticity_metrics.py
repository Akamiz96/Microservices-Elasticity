# ------------------------------------------------------------------------------
# ARCHIVO: calculate_elasticity_metrics.py
# DESCRIPCIÓN: Cálculo de métricas de elasticidad a partir de la demanda y la
#              oferta de CPU en un experimento de escalamiento automático.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Este script estima métricas de elasticidad basadas en datos recolectados
#     durante experimentos con cargas definidas en stages.json y eventos de HPA.
#   - Utiliza variables de entorno para identificar el experimento actual.
# ------------------------------------------------------------------------------

import os
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

# ============================================================================
# CONFIGURACIÓN DEL EXPERIMENTO Y PARÁMETROS
# ============================================================================

# Cargar IDs desde variables de entorno
HPA_ID = os.getenv("HPA_ID", "C1")
LOAD_ID = os.getenv("LOAD_ID", "L01")

# Parámetros del microbenchmark y del experimento
cpu_per_vu = 1.50    # millicores por VU (estimado en microbenchmark)
cpu_per_req = 0.05   # millicores por request (estimado en microbenchmark)
requests_per_vu_per_second = 1  # tasa asumida de requests por VU por segundo
sampling_interval = 10          # intervalo de muestreo en segundos
reconfig_threshold = 30         # umbral para agrupar eventos de escalamiento

# Rutas de archivos de entrada/salida
metrics_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_metrics.csv"
events_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_events_clean.csv"
k6_start_file = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_k6_start_time.txt"
stages_file = f"k6_configs/{LOAD_ID}_config.json"
output_metrics_vu = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_elasticity_metrics_vus.txt"
output_metrics_req = f"output/HPA_{HPA_ID}_LOAD_{LOAD_ID}_elasticity_metrics_requests.txt"

# ============================================================================
# FUNCIÓN AUXILIAR: calcular tiempo de reconfiguración (agrupado por tipo)
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

# ============================================================================
# FUNCIÓN PRINCIPAL DE CÁLCULO DE MÉTRICAS Y GUARDADO DE RESULTADOS
# ============================================================================

def calcular_metricas(df_demand, label, output_path, θ_up, θ_down, df_bloques):
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
        f.write("1. Duración del período de evaluación (T):\n")
        f.write(f"   - Desde: {df_comb['timestamp'].min()}\n")
        f.write(f"   - Hasta: {df_comb['timestamp'].max()}\n")
        f.write(f"   - Total: {T} ({T_seconds:.2f} s, {T_minutes:.2f} min)\n\n")

        f.write("2. Recursos acumulados:\n")
        f.write(f"   - ΣU (subaprovisionamiento): {ΣU:.2f} millicore-s\n")
        f.write(f"   - ΣO (sobreaprovisionamiento): {ΣO:.2f} millicore-s\n\n")

        f.write("3. Tiempo en reconfiguración (θ):\n")
        f.write(f"   - Total: {θ:.2f} s ({θ/60:.2f} min)\n")
        f.write(f"   -   ScaleUp: {θ_up:.2f} s\n")
        f.write(f"   -   ScaleDown: {θ_down:.2f} s\n\n")

        f.write("4. Tiempos en estados de (sub/sobre)aprovisionamiento:\n")
        f.write(f"   - ΣA (sub): {ΣA:.2f} s |  A̅: {A_bar:.2f} | Ū: {U_bar:.2f} millicores\n")
        f.write(f"   - ΣB (sobre): {ΣB:.2f} s |  B̅: {B_bar:.2f} | Ō: {O_bar:.2f} millicores\n\n")

        f.write("5. Métricas derivadas:\n")
        f.write(f"   - Precisión de escalado hacia arriba (Pᵤ): {P_u:.4f} millicore/s\n")
        f.write(f"   - Precisión de escalado hacia abajo (P𝑑): {P_d:.4f} millicore/s\n")
        f.write(f"   - Elasticidad de escalado hacia arriba (Eᵤ): {E_u:.4f}\n")
        f.write(f"   - Elasticidad de escalado hacia abajo (E𝑑): {E_d:.4f}\n")
        f.write(f"   - Elasticidad total (Eₗ): {E_l:.4f}\n\n")

        f.write("6. Bloques de reconfiguración detectados:\n")
        for _, row in df_bloques.iterrows():
            f.write(f"   - [{row['tipo']}] {row['start']} → {row['end']} | {row['duracion']:.1f} s, {row['eventos']} eventos\n")

        f.write("7. Métricas complementarias:\n")
        f.write(f"   - Elasticidad total (E): {E_global:.4f}\n")
        f.write(f"   - Subaprovisionamiento relativo (R_U): {R_U:.4f} millicore/s\n")
        f.write(f"   - Sobreaprovisionamiento relativo (R_O): {R_O:.4f} millicore/s\n")
        f.write(f"   - Porcentaje de tiempo en reconfiguración (θ%%): {theta_pct:.2f} %\n")
        f.write(f"       - ScaleUp: {theta_up_pct:.2f} %\n")
        f.write(f"       - ScaleDown: {theta_down_pct:.2f} %\n")
        f.write(f"   - Porcentaje de tiempo útil: {tiempo_util:.2f} %\n\n")

# ============================================================================
# ETAPA 1: Cargar métricas observadas (oferta)
# ============================================================================
df_metrics = pd.read_csv(metrics_file)
df_metrics["timestamp"] = pd.to_datetime(df_metrics["timestamp"])
df_metrics["cpu(millicores)"] = pd.to_numeric(df_metrics["cpu(millicores)"], errors="coerce")
df_supply = df_metrics.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

# ============================================================================
# ETAPA 2: Leer tiempo de inicio de carga y los stages
# ============================================================================
with open(k6_start_file) as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

with open(stages_file) as f:
    stages = json.load(f)["stages"]

# ============================================================================
# ETAPA 3: Generar demanda estimada a partir de los stages
# ============================================================================
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

# ============================================================================
# ETAPA 4: Calcular reconfiguraciones detectadas
# ============================================================================
θ_up, θ_down, df_bloques = calcular_tiempo_reconfiguracion(events_file, reconfig_threshold)

# ============================================================================
# ETAPA 5: Calcular métricas por VUs y por Requests
# ============================================================================
df_vus_vu = df_vus.copy()
df_vus_vu["demand"] = df_vus_vu["vus"] * cpu_per_vu
calcular_metricas(df_vus_vu, "Basado en VUs", output_metrics_vu, θ_up, θ_down, df_bloques)

df_vus_req = df_vus.copy()
df_vus_req["demand"] = df_vus_req["reqs"] * cpu_per_req
calcular_metricas(df_vus_req, "Basado en Requests", output_metrics_req, θ_up, θ_down, df_bloques)
