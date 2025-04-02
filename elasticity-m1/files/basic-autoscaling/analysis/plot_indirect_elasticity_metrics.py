# ------------------------------------------------------------------------------
# ARCHIVO: plot_indirect_elasticity_metrics.py
# DESCRIPCIÓN: Calcula y grafica métricas indirectas relacionadas con elasticidad
#              usando los datos exportados desde k6 (modo --out csv=).
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 2 de abril de 2025
# CONTEXTO:
#   - Usa los datos de tipo http_req_duration desde el archivo `k6_results.csv`.
#   - Genera 4 gráficas:
#       1. Latencia promedio en el tiempo
#       2. Latencia máxima en el tiempo
#       3. Cantidad de errores en el tiempo
#       4. Número de requests por segundo
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------------------------------------------------------
# CARGAR Y FILTRAR DATOS DE http_req_duration
# ---------------------------------------------------------------
df = pd.read_csv("output/k6_results.csv", on_bad_lines="skip")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")

# Filtrar solo las métricas de latencia
lat_df = df[df["metric_name"] == "http_req_duration"].copy()

# Agrupar por intervalo de 10 segundos
lat_df.set_index("timestamp", inplace=True)
grouped = lat_df.resample("10s")

# Calcular métricas
summary = grouped.agg(
    avg_latency=("metric_value", "mean"),
    max_latency=("metric_value", "max"),
    req_count=("metric_value", "count"),
)

# ---------------------------------------------------------------
# CONTAR ERRORES POR INTERVALO
# ---------------------------------------------------------------
error_df = df[(df["metric_name"] == "http_reqs") & (df["status"] != "200")].copy()
error_df.set_index("timestamp", inplace=True)
error_summary = error_df.resample("10s").size().rename("errors")

# Unir con resumen principal
summary = summary.join(error_summary, how="left")
summary["errors"].fillna(0, inplace=True)

# ---------------------------------------------------------------
# CREAR CARPETA DE IMÁGENES
# ---------------------------------------------------------------
os.makedirs("images", exist_ok=True)

# ---------------------------------------------------------------
# GRAFICAS INDIVIDUALES
# ---------------------------------------------------------------
sns.set(style="whitegrid")
figsize = (12, 5)

# 1. Latencia promedio
plt.figure(figsize=figsize)
plt.plot(summary.index, summary["avg_latency"], marker="o", label="Latencia promedio (ms)")
plt.title("Latencia Promedio en el Tiempo")
plt.xlabel("Tiempo")
plt.ylabel("ms")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid()
plt.savefig("images/avg_latency_over_time.png")
plt.close()

# 2. Latencia máxima
plt.figure(figsize=figsize)
plt.plot(summary.index, summary["max_latency"], marker="o", color="orange", label="Latencia máxima (ms)")
plt.title("Latencia Máxima en el Tiempo")
plt.xlabel("Tiempo")
plt.ylabel("ms")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid()
plt.savefig("images/max_latency_over_time.png")
plt.close()

# 3. Errores por intervalo
plt.figure(figsize=figsize)
plt.plot(summary.index, summary["errors"], marker="o", color="red", label="Errores por intervalo")
plt.title("Errores por Segundo")
plt.xlabel("Tiempo")
plt.ylabel("Cantidad de errores")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid()
plt.savefig("images/errors_per_interval.png")
plt.close()

# 4. Requests por segundo
plt.figure(figsize=figsize)
plt.plot(summary.index, summary["req_count"], marker="o", color="green", label="Requests por segundo")
plt.title("Requests por Segundo")
plt.xlabel("Tiempo")
plt.ylabel("Cantidad")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid()
plt.savefig("images/requests_per_second.png")
plt.close()
