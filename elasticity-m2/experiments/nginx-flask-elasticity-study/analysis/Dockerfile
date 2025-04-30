# ------------------------------------------------------------------------------
# ARCHIVO: Dockerfile
# DESCRIPCIÓN: Imagen Docker para ejecutar el análisis del experimento
#              `exp2_nginx-elasticity-study`, incluyendo visualizaciones,
#              métricas de elasticidad y curvas de comportamiento.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - El contenedor ejecuta automáticamente los scripts ubicados en `code/`.
#   - Requiere dos variables de entorno: HPA_ID (C1-C9) y LOAD_ID (L01-L06).
#   - Los scripts pueden acceder a estos valores mediante os.environ[].
#   - Requiere los volúmenes `output/`, `analysis/images/` y `analysis/files/` montados.
# ------------------------------------------------------------------------------

    FROM python:3.10-slim

    WORKDIR /app
    
    # Copiar scripts y dependencias
    COPY code/ .
    COPY requirements.txt .
    
    # Instalar paquetes necesarios
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Crear carpetas necesarias (pueden ser montadas por volumen)
    RUN mkdir -p output images files
    
    # Comando por defecto al ejecutar el contenedor
    CMD ["sh", "-c", "\
        export HPA_ID=${HPA_ID} && \
        export LOAD_ID=${LOAD_ID} && \
        python filter_scaling_events.py && \
        python plot_cpu_usage.py && \
        python plot_cpu_usage_with_events.py && \
        python plot_pod_count.py && \
        python plot_pod_count_with_events.py && \
        python plot_elasticity_curve.py && \
        python plot_elasticity_curve_with_events.py && \
        python plot_indirect_elasticity_metrics.py && \
        python calculate_elasticity_metrics.py"]
    