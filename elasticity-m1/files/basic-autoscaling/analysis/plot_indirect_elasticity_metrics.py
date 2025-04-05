
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =============================
# CONFIGURACIÓN INICIAL
# =============================

INPUT_CSV = "output/k6_results.csv"
EVENTS_CSV = "output/scaling_events_clean.csv"
OUTPUT_DIR = "images/indirect_metrics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================
# CARGA Y PROCESAMIENTO DE DATOS
# =============================

df_k6 = pd.read_csv(INPUT_CSV)
df_k6["timestamp"] = pd.to_datetime(df_k6["timestamp"], unit="s")

grouped = df_k6.groupby(["timestamp", "metric_name"]).agg({"metric_value": "mean"}).reset_index()
pivoted = grouped.pivot(index="timestamp", columns="metric_name", values="metric_value").fillna(0)

df_events = pd.read_csv(EVENTS_CSV)
df_events["timestamp"] = pd.to_datetime(df_events["timestamp"], errors="coerce")

def add_scaling_event_lines(ax, df_events):
    for _, event in df_events.iterrows():
        color = "green" if event["scale_action"] == "scaleup" else "red"
        ax.axvline(x=event["timestamp"], color=color, linestyle="--", alpha=0.7)

# =============================
# 1. LATENCIA PROMEDIO
# =============================
fig1, ax1 = plt.subplots(figsize=(10, 4))
pivoted["http_req_duration"].plot(ax=ax1)
ax1.set_title("Latencia Promedio a lo largo del tiempo")
ax1.set_ylabel("Duración (s)")
ax1.set_xlabel("Tiempo")
fig1.savefig(f"{OUTPUT_DIR}/latency_avg.png")

fig1e, ax1e = plt.subplots(figsize=(10, 4))
pivoted["http_req_duration"].plot(ax=ax1e)
add_scaling_event_lines(ax1e, df_events)
ax1e.set_title("Latencia Promedio con eventos de escalamiento")
ax1e.set_ylabel("Duración (s)")
ax1e.set_xlabel("Tiempo")
fig1e.savefig(f"{OUTPUT_DIR}/latency_avg_events.png")

# =============================
# 2. ERRORES HTTP POR SEGUNDO
# =============================
full_time_index = pivoted.index
errors_series = pd.Series(0, index=full_time_index, name="Errores")

fig2, ax2 = plt.subplots(figsize=(10, 4))
errors_series.plot(ax=ax2)
ax2.set_title("Errores HTTP por segundo")
ax2.set_ylabel("Errores")
ax2.set_xlabel("Tiempo")
fig2.savefig(f"{OUTPUT_DIR}/http_errors.png")

fig2e, ax2e = plt.subplots(figsize=(10, 4))
errors_series.plot(ax=ax2e)
add_scaling_event_lines(ax2e, df_events)
ax2e.set_title("Errores HTTP con eventos de escalamiento")
ax2e.set_ylabel("Errores")
ax2e.set_xlabel("Tiempo")
fig2e.savefig(f"{OUTPUT_DIR}/http_errors_events.png")

# =============================
# 3. REQUESTS POR SEGUNDO (THROUGHPUT)
# =============================
fig3, ax3 = plt.subplots(figsize=(10, 4))
pivoted["http_reqs"].plot(ax=ax3)
ax3.set_title("Requests por segundo (Throughput)")
ax3.set_ylabel("Requests/s")
ax3.set_xlabel("Tiempo")
fig3.savefig(f"{OUTPUT_DIR}/throughput.png")

fig3e, ax3e = plt.subplots(figsize=(10, 4))
pivoted["http_reqs"].plot(ax=ax3e)
add_scaling_event_lines(ax3e, df_events)
ax3e.set_title("Throughput con eventos de escalamiento")
ax3e.set_ylabel("Requests/s")
ax3e.set_xlabel("Tiempo")
fig3e.savefig(f"{OUTPUT_DIR}/throughput_events.png")

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

print("✅ Gráficas generadas con y sin eventos de escalamiento.")
