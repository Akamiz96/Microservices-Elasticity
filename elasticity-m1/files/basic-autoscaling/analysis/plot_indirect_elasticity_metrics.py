import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar archivo CSV
df_k6 = pd.read_csv("k6_results.csv")

# Convertir timestamps a datetime
df_k6["timestamp"] = pd.to_datetime(df_k6["timestamp"], unit="s")

# Agrupar por timestamp y métrica
grouped = df_k6.groupby(["timestamp", "metric_name"]).agg({"metric_value": "mean"}).reset_index()
pivoted = grouped.pivot(index="timestamp", columns="metric_name", values="metric_value").fillna(0)

# 1. Latencia promedio a lo largo del tiempo
fig1, ax1 = plt.subplots(figsize=(10, 4))
pivoted["http_req_duration"].plot(ax=ax1)
ax1.set_title("Latencia Promedio a lo largo del tiempo")
ax1.set_ylabel("Duración (s)")
ax1.set_xlabel("Tiempo")

# 2. Errores HTTP por segundo (con escala de tiempo aunque no haya errores)
full_time_index = pivoted.index
errors_series = pd.Series(0, index=full_time_index, name="Errores")

fig2, ax2 = plt.subplots(figsize=(10, 4))
errors_series.plot(ax=ax2)
ax2.set_title("Errores HTTP por segundo")
ax2.set_ylabel("Errores")
ax2.set_xlabel("Tiempo")

# 3. Throughput (requests por segundo)
fig3, ax3 = plt.subplots(figsize=(10, 4))
pivoted["http_reqs"].plot(ax=ax3)
ax3.set_title("Requests por segundo (Throughput)")
ax3.set_ylabel("Requests/s")
ax3.set_xlabel("Tiempo")

# 4. Throughput vs VUs
vus_df = df_k6[df_k6["metric_name"] == "vus"].groupby("timestamp").agg({"metric_value": "mean"})
rps_df = df_k6[df_k6["metric_name"] == "http_reqs"].groupby("timestamp").agg({"metric_value": "mean"})
merged = pd.merge(vus_df, rps_df, left_index=True, right_index=True, suffixes=("_vus", "_rps"))

fig4, ax4 = plt.subplots(figsize=(6, 6))
sns.scatterplot(data=merged, x="metric_value_vus", y="metric_value_rps", ax=ax4)
ax4.set_title("Throughput vs VUs")
ax4.set_xlabel("VUs")
ax4.set_ylabel("Requests/s")

plt.tight_layout()
plt.show()
