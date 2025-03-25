#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: metric_collector.sh
# DESCRIPCIÓN: Script para recolectar métricas de CPU y memoria de los pods en un
#              namespace de Kubernetes, y guardarlas en un archivo CSV estructurado.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   - Adaptado para almacenar la salida en 'output/metrics.csv' según la nueva estructura del proyecto.
#   - Se recomienda ejecutarlo en paralelo a la prueba de carga con k6.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
OUTPUT_DIR="load_test/output"          # Carpeta donde se guardará el CSV
OUTPUT_FILE="$OUTPUT_DIR/metrics.csv"  # Ruta completa al archivo de salida

NAMESPACE="default"                    # Namespace a monitorear
DEPLOYMENT_NAME="nginx-test"           # Deployment objetivo (referencial)
INTERVAL=10                            # Intervalo de recolección (segundos)

# ---------------------------------------------------------------
# PREPARACIÓN DEL DIRECTORIO DE SALIDA
# ---------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"  # Crear carpeta output si no existe

# Encabezado del archivo CSV
echo "timestamp,pod,cpu(millicores),memory(bytes),%cpu,num_pods" > "$OUTPUT_FILE"

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN PERIÓDICA DE MÉTRICAS
# ---------------------------------------------------------------
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")  # Registrar momento actual

    # Contar el número actual de pods activos en el namespace
    NUM_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers | wc -l)

    # Recolectar métricas de cada pod usando 'kubectl top'
    kubectl top pod -n "$NAMESPACE" --no-headers | while read -r POD CPU MEM; do
        CPU_VAL=${CPU%m}  # Eliminar la 'm' (millicores)

        # Obtener CPU solicitada en recursos
        REQUESTS_CPU=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath="{.spec.containers[0].resources.requests.cpu}" 2>/dev/null)
        REQUESTS_CPU_VAL=$(echo "$REQUESTS_CPU" | sed 's/m//')

        # Si no se define requests.cpu, asumir 1000m (1 core)
        [[ -z "$REQUESTS_CPU_VAL" ]] && REQUESTS_CPU_VAL=1000

        # Calcular el porcentaje de uso de CPU
        CPU_PERC=$(echo "scale=2; ($CPU_VAL / $REQUESTS_CPU_VAL) * 100" | bc)

        # Escribir datos en el archivo CSV
        echo "$TIMESTAMP,$POD,$CPU_VAL,$MEM,$CPU_PERC,$NUM_PODS" >> "$OUTPUT_FILE"
    done

    sleep "$INTERVAL"
done
