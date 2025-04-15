# ------------------------------------------------------------------------------
# ARCHIVO: calculate_elasticity_metrics.py
# DESCRIPCIÓN: Cálculo de métricas de elasticidad a partir de la demanda y la
#              oferta de CPU en un experimento de escalamiento automático.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 5 de abril de 2025
# CONTEXTO:
#   - El script estima elasticidades y métricas relacionadas para dos tipos de demanda:
#       (1) en función de los VUs (usuarios virtuales)
#       (2) en función del número de requests.
#   - Utiliza los resultados del microbenchmark para convertir demanda en CPU.
#   - Guarda los resultados en archivos de texto para cada tipo de demanda.
# ------------------------------------------------------------------------------

import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

# ============================================================================
# CONFIGURACIÓN DEL EXPERIMENTO Y PARÁMETROS
# ============================================================================

cpu_per_vu = 1.50    # millicores por VU (estimado en microbenchmark)
cpu_per_req = 0.05   # millicores por request (estimado en microbenchmark)
requests_per_vu_per_second = 1  # tasa asumida de requests por VU por segundo
sampling_interval = 10          # intervalo de muestreo en segundos
reconfig_threshold = 30         # umbral para agrupar eventos de escalamiento

# ============================================================================
# FUNCIÓN AUXILIAR: calcular tiempo de reconfiguración (agrupado por tipo)
# ============================================================================

def calcular_tiempo_reconfiguracion(events_csv, threshold_seconds=30):
    """
    Agrupa eventos de escalamiento cercanos en el tiempo y calcula la duración
    total de los bloques de reconfiguración por tipo.

    Parámetros:
    - events_csv (str): Ruta al CSV con eventos de escalamiento.
    - threshold_seconds (int): Umbral máximo de separación para agrupar eventos.

    Retorna:
    - θ_up (float): Tiempo total en segundos en bloques de escalamiento hacia arriba.
    - θ_down (float): Tiempo total en segundos en bloques de escalamiento hacia abajo.
    - df_bloques (pd.DataFrame): Información detallada de cada bloque agrupado.
    """
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
    """
    Calcula todas las métricas de elasticidad a partir de la oferta y la demanda.

    Parámetros:
    - df_demand (pd.DataFrame): Serie temporal con la demanda (millicores).
    - label (str): Etiqueta para identificar el tipo de demanda en los resultados.
    - output_path (str): Ruta al archivo de salida de texto.
    - θ_up (float): Tiempo total en bloques de escalamiento hacia arriba.
    - θ_down (float): Tiempo total en bloques de escalamiento hacia abajo.
    - df_bloques (pd.DataFrame): Detalles de bloques de reconfiguración.

    Retorna:
    - None. Escribe resultados en el archivo especificado.
    """
    df_comb = pd.merge_asof(
        df_demand.sort_values("timestamp"),
        df_supply,
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(seconds=sampling_interval)
    )
    df_comb.dropna(inplace=True)

    # Duración total del experimento
    T = df_comb["timestamp"].max() - df_comb["timestamp"].min()
    T_seconds = T.total_seconds()
    T_minutes = T_seconds / 60

    # ------------------------
    # SUB/SOBREAPROVISIONAMIENTO
    # ------------------------

    # Subaprovisionamiento: cuando la demanda supera la oferta
    df_comb["under"] = df_comb["demand"] - df_comb["supply"]
    df_comb["under"] = df_comb["under"].apply(lambda x: x if x > 0 else 0)

    # Sobreaprovisionamiento: cuando la oferta supera la demanda
    df_comb["over"] = df_comb["supply"] - df_comb["demand"]
    df_comb["over"] = df_comb["over"].apply(lambda x: x if x > 0 else 0)

    # ΣU y ΣO son las áreas acumuladas de sub/sobreaprovisionamiento (millicores * segundos)
    ΣU = df_comb["under"].sum() * sampling_interval
    ΣO = df_comb["over"].sum() * sampling_interval

    # ------------------------
    # TIEMPOS Y PROMEDIOS
    # ------------------------

    under_periods = df_comb[df_comb["under"] > 0]
    over_periods = df_comb[df_comb["over"] > 0]

    # ΣA y ΣB son los tiempos totales en los que hubo sub/sobreaprovisionamiento
    ΣA = len(under_periods) * sampling_interval
    ΣB = len(over_periods) * sampling_interval

    # A̅ y B̅: proporción del tiempo total que se pasó en cada estado
    A_bar = ΣA / T_seconds if T_seconds > 0 else 0
    B_bar = ΣB / T_seconds if T_seconds > 0 else 0

    # Ū y Ō: intensidad media de sub/sobreaprovisionamiento durante sus períodos
    U_bar = ΣU / ΣA if ΣA > 0 else 0
    O_bar = ΣO / ΣB if ΣB > 0 else 0

    # ------------------------
    # PRECISIÓN
    # ------------------------

    # Pᵤ y P𝑑: precisión del sistema para evitar sub/sobreaprovisionamiento
    # Mientras menores sean, mejor se está ajustando la oferta a la demanda
    P_u = ΣU / T_seconds if T_seconds > 0 else 0
    P_d = ΣO / T_seconds if T_seconds > 0 else 0

    # ------------------------
    # ELASTICIDADES PARCIALES
    # ------------------------

    # Eᵤ = 1 / (A̅ × Ū)
    E_u = 1 / (A_bar * U_bar) if A_bar * U_bar > 0 else 0

    # E𝑑 = 1 / (B̅ × Ō)
    E_d = 1 / (B_bar * O_bar) if B_bar * O_bar > 0 else 0

    # ------------------------
    # ELASTICIDAD TOTAL
    # ------------------------

    θ = θ_up + θ_down  # tiempo total de reconfiguración

    # μ: intensidad media de desajuste respecto al total de muestras
    μ = (ΣU + ΣO) / (T_seconds * len(df_comb)) if len(df_comb) > 0 else 0

    # Eₗ: mide la capacidad global del sistema para ajustarse de manera eficiente
    E_l = 1 / (θ * μ) if θ * μ > 0 else 0

    # -------------------------------------------------------------------------------
    # MÉTRICAS COMPLEMENTARIAS
    # -------------------------------------------------------------------------------

    # E_global: elasticidad complementaria basada en penalización simple
    # Mide qué tan bien se evita tanto sub como sobreaprovisionamiento.
    # Valor ideal cercano a 1. Disminuye si hay mucho desajuste.
    E_global = 1 - ((ΣU + ΣO) / T_seconds) if T_seconds > 0 else 0

    # R_U: tasa promedio de subaprovisionamiento por segundo
    # Útil para comparar la intensidad del desajuste en relación al tiempo.
    R_U = ΣU / T_seconds if T_seconds > 0 else 0

    # R_O: tasa promedio de sobreaprovisionamiento por segundo
    R_O = ΣO / T_seconds if T_seconds > 0 else 0

    # theta_pct: porcentaje del tiempo total dedicado a reconfiguraciones
    # Muestra cuánto del experimento se usó activamente en escalar.
    theta_pct = (θ / T_seconds) * 100 if T_seconds > 0 else 0

    # theta_up_pct y theta_down_pct: porcentaje de tiempo en escalamiento hacia arriba y hacia abajo
    theta_up_pct = (θ_up / T_seconds) * 100 if T_seconds > 0 else 0
    theta_down_pct = (θ_down / T_seconds) * 100 if T_seconds > 0 else 0

    # tiempo_util: porcentaje de tiempo útil del sistema (sin reconfigurar)
    tiempo_util = 100 - theta_pct


    # ------------------------
    # SALIDA DE RESULTADOS
    # ------------------------

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
# ETAPA 1: Cargar métricas de Kubernetes (oferta de CPU)
# ============================================================================

df_metrics = pd.read_csv("output/basic_metrics.csv")
df_metrics["timestamp"] = pd.to_datetime(df_metrics["timestamp"])
df_metrics["cpu(millicores)"] = pd.to_numeric(df_metrics["cpu(millicores)"], errors="coerce")
df_supply = df_metrics.groupby("timestamp")["cpu(millicores)"].sum().reset_index()
df_supply.rename(columns={"cpu(millicores)": "supply"}, inplace=True)

# ============================================================================
# ETAPA 2: Leer tiempo de inicio de k6 y etapas definidas
# ============================================================================

with open("output/k6_start_time.txt") as f:
    k6_start_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")

with open("output/stages.json") as f:
    stages = json.load(f)

# ============================================================================
# ETAPA 3: Generar serie de demanda en función de VUs y Requests
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
# ETAPA 4: Calcular bloques de reconfiguración a partir de eventos
# ============================================================================

θ_up, θ_down, df_bloques = calcular_tiempo_reconfiguracion(
    "output/scaling_events_clean.csv",
    threshold_seconds=reconfig_threshold
)

# ============================================================================
# ETAPA 5: Calcular métricas usando ambas formas de demanda
# ============================================================================

# Por VUs
df_vus_vu = df_vus.copy()
df_vus_vu["demand"] = df_vus_vu["vus"] * cpu_per_vu
calcular_metricas(df_vus_vu, "Basado en VUs", "output/elasticity_metrics_vus.txt", θ_up, θ_down, df_bloques)

# Por requests
df_vus_req = df_vus.copy()
df_vus_req["demand"] = df_vus_req["reqs"] * cpu_per_req
calcular_metricas(df_vus_req, "Basado en Requests", "output/elasticity_metrics_requests.txt", θ_up, θ_down, df_bloques)
