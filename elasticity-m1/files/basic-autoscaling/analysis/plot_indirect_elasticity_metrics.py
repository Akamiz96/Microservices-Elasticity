import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =============================
# CONFIGURACIÓN INICIAL
# =============================

# Ruta del archivo CSV exportado por k6
INPUT_CSV = "output/k6_results.csv"

# Carpeta de salida para los gráficos
OUTPUT_DIR = "indirect_metrics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================
# CARGA Y PROCESAMIENTO DE DATOS
# =============================

# Cargar archivo CSV
df_k6 = pd.read_csv(INPUT_CSV)

# Convertir timestamp a formato datetime
df_k6["timestamp"] = pd.to_datetime(df_k6["timestamp"], unit="s")

# Agrupar por tiempo y métrica, y hacer pivot para acceder fácil por nombre
grouped = df_k6.groupby(["timestamp", "metric_name"]).agg({"metric_value": "mean"}).reset_index()
pivoted = grouped.pivot(index="timestamp", columns="metric_name", values="metric_value").fillna(0)

# =============================
# 1. LATENCIA PROMEDIO
# =============================
fig1, ax1 = plt.subplots(figsize=(10, 4))
pivoted["http_req_duration"].plot(ax=ax1)
ax1.set_title("Latencia Promedio a lo largo del tiempo")
ax1.set_ylabel("Duración (s)")
ax1.set_xlabel("Tiempo")
fig1.savefig(f"{OUTPUT_DIR}/latencia_promedio.png")

# =============================
# 2. ERRORES HTTP POR SEGUNDO
# =============================
# Si no hay errores, igual creamos una serie en 0
full_time_index = pivoted.index
errors_series = pd.Series(0, index=full_time_index, name="Errores")

fig2, ax2 = plt.subplots(figsize=(10, 4))
errors_series.plot(ax=ax2)
ax2.set_title("Errores HTTP por segundo")
ax2.set_ylabel("Errores")
ax2.set_xlabel("Tiempo")
fig2.savefig(f"{OUTPUT_DIR}/errores_http.png")

# =============================
# 3. REQUESTS POR SEGUNDO (THROUGHPUT)
# =============================
fig3, ax3 = plt.subplots(figsize=(10, 4))
pivoted["http_reqs"].plot(ax=ax3)
ax3.set_title("Requests por segundo (Throughput)")
ax3.set_ylabel("Requests/s")
ax3.set_xlabel("Tiempo")
fig3.savefig(f"{OUTPUT_DIR}/throughput_tiempo.png")

# =============================
# 4. THROUGHPUT VS VUs
# =============================
vus_df = df_k6[df_k6["metric_name"] == "vus"].groupby("timestamp").agg({"metric_value": "mean"})
rps_df = df_k6[df_k6["metric_name"] == "http_reqs"].groupby("timestamp").agg({"metric_value": "mean"})
merged = pd.merge(vus_df, rps_df, left_index=True, right_index=True, suffixes=("_vus", "_rps"))

fig4, ax4 = plt.subplots(figsize=(6, 6))
sns.scatterplot(data=merged, x="metric_value_vus", y="metric_value_rps", ax=ax4)
ax4.set_title("Throughput vs VUs")
ax4.set_xlabel("VUs")
ax4.set_ylabel("Requests/s")
fig4.savefig(f"{OUTPUT_DIR}/throughput_vs_vus.png")
