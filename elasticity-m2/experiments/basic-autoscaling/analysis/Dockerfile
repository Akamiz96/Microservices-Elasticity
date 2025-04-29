# ------------------------------------------------------------------------------
# ARCHIVO: Dockerfile
# DESCRIPCIÓN: Imagen Docker para análisis de elasticidad en exp1_basic-autoscaling
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Ejecuta automáticamente todos los scripts de análisis del experimento.
# ------------------------------------------------------------------------------

FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar todos los scripts Python y el archivo de requerimientos
COPY *.py .
COPY requirements.txt .

# Instalar dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpetas internas de entrada/salida por defecto (en caso de no montar volúmenes)
RUN mkdir -p experiments/basic-autoscaling/output experiments/basic-autoscaling/images experiments/basic-autoscaling/files

# Comando por defecto: ejecutar todo el flujo de análisis
CMD ["sh", "-c", "\
    python filter_scaling_events.py && \
    python plot_cpu_usage.py && \
    python plot_cpu_usage_with_events.py && \
    python plot_pod_count.py && \
    python plot_pod_count_with_events.py && \
    python plot_elasticity_curve.py && \
    python plot_elasticity_curve_with_events.py && \
    python plot_indirect_elasticity_metrics.py && \
    python calculate_elasticity_metrics.py"]
    