# ------------------------------------------------------------------------------
# ARCHIVO: Dockerfile
# DESCRIPCIÓN: Imagen Docker para análisis de resultados del microbenchmark.
#              Ejecuta scripts en Python para generar visualizaciones y métricas
#              estimadas a partir del archivo de carga y consumo generado.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Este contenedor ejecuta:
#       - plot_cpu_usage.py
#       - plot_pod_count.py
#       - analyze_microbenchmark.py
#   - Requiere que los volúmenes 'output/', 'images/' y 'files/' estén montados.
# ------------------------------------------------------------------------------

    FROM python:3.10-slim

    # Establece el directorio de trabajo dentro del contenedor
    WORKDIR /app
    
    # Copia los scripts de análisis
    COPY plot_cpu_usage.py .
    COPY plot_pod_count.py .
    COPY analyze_microbenchmark.py .
    COPY requirements.txt .
    
    # Instala las dependencias necesarias
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Crea carpetas de entrada/salida (si no existen por volumen)
    RUN mkdir -p images output files
    
    # Comando por defecto: ejecutar los 3 scripts secuencialmente
    CMD ["sh", "-c", "python plot_cpu_usage.py && python plot_pod_count.py && python analyze_microbenchmark.py"]
    