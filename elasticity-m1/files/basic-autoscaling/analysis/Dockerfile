# ------------------------------------------------------------------------------
# ARCHIVO: Dockerfile
# DESCRIPCIÓN: Imagen Docker para ejecutar el análisis del experimento
#              `exp1_basic-autoscaling`, incluyendo visualizaciones y estimaciones.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 29 de marzo de 2025
# CONTEXTO:
#   - Este contenedor ejecuta automáticamente:
#       - filter_scaling_events.py
#       - plot_cpu_usage.py
#       - plot_pod_count.py
#       - plot_pod_count_with_events.py
#       - plot_elasticity_curve.py
#       - plot_elasticity_curve_with_events.py
#   - Requiere los volúmenes 'output/', 'analysis/images/' y 'analysis/files/' montados.
# ------------------------------------------------------------------------------

# Imagen base ligera con Python 3
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar scripts de análisis
COPY filter_scaling_events.py .
COPY plot_cpu_usage.py .
COPY plot_elasticity_curve_with_events.py .
COPY plot_elasticity_curve.py .
COPY plot_pod_count_with_events.py .
COPY plot_pod_count.py .
COPY plot_cpu_usage_with_events.py .
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpetas necesarias (aunque serán sobrescritas por los volúmenes)
RUN mkdir -p output images files

# Comando por defecto: ejecutar todo el flujo de análisis
CMD ["sh", "-c", "\
    python filter_scaling_events.py && \
    python plot_cpu_usage.py && \
    python plot_cpu_usage_with_events.py && \
    python plot_pod_count.py && \
    python plot_pod_count_with_events.py && \
    python plot_elasticity_curve.py && \
    python plot_elasticity_curve_with_events.py"]
