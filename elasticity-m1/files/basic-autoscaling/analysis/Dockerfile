# ------------------------------------------------------------------------------
# ARCHIVO: Dockerfile
# DESCRIPCIÓN: Imagen Docker para ejecutar el análisis del experimento
#              `exp1_basic-autoscaling`, incluyendo visualizaciones y estimaciones.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Este contenedor se usa exclusivamente para ejecutar los scripts:
#       - plot_cpu_usage.py
#       - plot_pod_count.py
#       - analyze_basic_load.py
#   - Requiere que los volúmenes 'output/', 'analysis/images/' y 'analysis/files/' estén montados.
#   - Debe ser ejecutado desde la raíz de 'files/basic-autoscaling/'.
# ------------------------------------------------------------------------------

# Imagen base con Python 3 ligero
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar scripts de análisis y dependencias
COPY plot_cpu_usage.py .
COPY plot_pod_count.py .
COPY plot_elasticity_curve.py .
COPY requirements.txt .

# Instalar dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpetas para entrada/salida (montadas como volúmenes en tiempo de ejecución)
RUN mkdir -p output analysis/images analysis/files

# Comando por defecto al ejecutar el contenedor: correr los scripts de análisis
CMD ["sh", "-c", "python plot_cpu_usage.py && python plot_pod_count.py && python plot_elasticity_curve.py"]