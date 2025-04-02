# ------------------------------------------------------------------------------
# ARCHIVO: plot_indirect_elasticity_metrics.py
# DESCRIPCIÓN: Genera cuatro gráficos que permiten inferir el comportamiento
#              de la elasticidad del sistema desde el punto de vista del usuario.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 2 de abril de 2025
# CONTEXTO:
#   - Usa el archivo 'output/k6_results.csv' generado por k6 con --log-output.
#   - Calcula:
#       1. Tasa de errores por intervalo
#       2. Latencia promedio
#       3. Total de requests por intervalo
#       4. Tasa de éxito
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Crear carpeta de salida si no existe
os.makedirs("images", exist_ok=True)

# Leer resultados de k6
df = pd.read_csv("output/k6_results.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Filtrar solo requests válidas
df = df[df["status"].notna()]
df["status"] = df["status"].astype(int)

# Agrupar por intervalo de 10 segundos
df["time_bucket"] = df["timestamp"].dt.floor("10s")
grouped = df.groupby("time_bucket")

# Calcular métricas agregadas
summary = grouped.agg(
    total_requests=("status", "count"),
    failed_requests=("status", lambda x: (x != 200).sum()),
    success_requests=("status", lambda x: (x == 200).sum()),
    avg_duration=("http_req_duration", "mean")
).reset_index()

summary["error_rate"] = summary["failed_requests"] / summary["total_requests"]
summary["success_rate"] = summary["success_requests"] / summary["total_requests"]

# ---------------------------------------------------------------
# 1. Error Rate
# ---------------------------------------------------------------
plt.figure(figsize=(10, 4))
sns.lineplot(data=summary, x="time_bucket", y="error_rate", marker="o", color="red")
plt.title("Error Rate vs Time")
plt.ylabel("Error Rate")
plt.xlabel("Time")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.savefig("images/indirect_error_rate.png")
plt.close()

# ---------------------------------------------------------------
# 2. Avg Request Duration
# ---------------------------------------------------------------
plt.figure(figsize=(10, 4))
sns.lineplot(data=summary, x="time_bucket", y="avg_duration", marker="o", color="blue")
plt.title("Avg Request Duration vs Time")
plt.ylabel("Avg Duration (ms)")
plt.xlabel("Time")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.savefig("images/indirect_avg_duration.png")
plt.close()

# ---------------------------------------------------------------
# 3. Total Requests per Interval
# ---------------------------------------------------------------
plt.figure(figsize=(10, 4))
sns.lineplot(data=summary, x="time_bucket", y="total_requests", marker="o", color="green")
plt.title("Requests per 10s Interval")
plt.ylabel("Requests")
plt.xlabel("Time")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.savefig("images/indirect_requests_per_interval.png")
plt.close()

# ---------------------------------------------------------------
# 4. Success Rate
# ---------------------------------------------------------------
plt.figure(figsize=(10, 4))
sns.lineplot(data=summary, x="time_bucket", y="success_rate", marker="o", color="purple")
plt.title("Success Rate vs Time")
plt.ylabel("Success Rate")
plt.xlabel("Time")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.savefig("images/indirect_success_rate.png")
plt.close()
