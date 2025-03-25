# ------------------------------------------------------------------------------
# ARCHIVO: Dockerfile
# DESCRIPCIÓN: Imagen Docker para análisis de resultados de pruebas de carga.
#              Ejecuta automáticamente scripts en Python que generan visualizaciones
#              a partir del archivo de métricas generado durante la prueba.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   - Este contenedor se usa exclusivamente para ejecutar los scripts:
#       - plot_cpu_usage.py
#       - plot_pod_count.py
#   - Requiere que los volúmenes 'output/' y 'images/' estén montados al ejecutarlo.
#   - Debe ser ejecutado desde la raíz de 'files/load_test/'.
# ------------------------------------------------------------------------------

# Imagen base con Python 3 ligero
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los scripts de análisis al contenedor
COPY plot_cpu_usage.py .
COPY plot_pod_count.py .
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Crea las carpetas para entrada/salida (montadas como volúmenes en tiempo de ejecución)
RUN mkdir -p images output

# Comando por defecto al ejecutar el contenedor: correr ambos scripts de análisis
CMD ["sh", "-c", "python plot_cpu_usage.py && python plot_pod_count.py"]
