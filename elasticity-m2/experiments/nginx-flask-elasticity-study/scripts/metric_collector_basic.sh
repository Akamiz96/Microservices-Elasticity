#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: metric_collector_microbenchmark.sh
# DESCRIPCIÓN: Script genérico para recolectar métricas de CPU y memoria de los pods
#              durante la ejecución del microbenchmark. Guarda resultados separados
#              para cada deployment que se monitoriza.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de abril de 2025
# CONTEXTO:
#   - Diseñado para ser usado en estudios de elasticidad de microservicios.
#   - Permite recolectar métricas de múltiples deployments ejecutándose en paralelo.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# PARÁMETROS DE ENTRADA
# ---------------------------------------------------------------
if [ $# -lt 1 ]; then
    echo "Uso: $0 <nombre-del-deployment>"
    exit 1
fi

DEPLOYMENT_NAME="$1"   # Nombre del deployment a monitorear

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
NAMESPACE="default"                                         # Namespace a monitorear
OUTPUT_DIR="experiments/nginx-flask-elasticity-study/output"              # Carpeta donde se guardarán los CSV
OUTPUT_FILE="$OUTPUT_DIR/basic_metrics_${DEPLOYMENT_NAME}.csv"  # Archivo de salida por deployment
INTERVAL=10                                                 # Intervalo de recolección (segundos)

# ---------------------------------------------------------------
# PREPARACIÓN DEL DIRECTORIO DE SALIDA
# ---------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"                                      # Crear carpeta output si no existe

# Encabezado del archivo CSV
echo "timestamp,pod,cpu(millicores),memory(bytes),%cpu,num_pods" > "$OUTPUT_FILE"

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN PERIÓDICA DE MÉTRICAS
# ---------------------------------------------------------------
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")                  # Obtener timestamp actual

    # --------------------------------------------------------------------------
    # Obtener lista de pods activos asociados al deployment
    # Se filtra por etiqueta app=<deployment> para evitar interferencias
    # --------------------------------------------------------------------------
    POD_LIST=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep "$DEPLOYMENT_NAME" | awk '{print $1}')
    
    # --------------------------------------------------------------------------
    # Verificar si hay pods activos disponibles
    # Si no hay, registrar información y esperar al siguiente ciclo
    # --------------------------------------------------------------------------
    if [ -z "$POD_LIST" ]; then
        echo "[Info] [$TIMESTAMP] No pods disponibles para '$DEPLOYMENT_NAME'."
        sleep "$INTERVAL"
        continue
    fi

    NUM_PODS=$(echo "$POD_LIST" | wc -l)  # Contar número de pods activos

    # --------------------------------------------------------------------------
    # Recolectar métricas de cada pod usando 'kubectl top'
    # La salida tiene el formato: <pod-name> <cpu> <memory>
    # Para cada pod:
    #   - cpu: en millicores (ej. 125m → 125)
    #   - memory: tal como lo reporta Kubernetes
    #   - %cpu: calculado en relación con el recurso solicitado
    # --------------------------------------------------------------------------
    for POD in $POD_LIST; do
        METRICS=$(kubectl top pod "$POD" -n "$NAMESPACE" --no-headers 2>/dev/null)

        if [ -z "$METRICS" ]; then
            echo "[Warning] [$TIMESTAMP] No se pudo obtener métricas para pod '$POD'."
            continue
        fi

        CPU=$(echo "$METRICS" | awk '{print $2}')
        MEM=$(echo "$METRICS" | awk '{print $3}')

        CPU_VAL=${CPU%m}  # Eliminar la 'm' de millicores

        # Obtener el CPU solicitado en el pod (resources.requests.cpu)
        REQUESTS_CPU=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath="{.spec.containers[0].resources.requests.cpu}" 2>/dev/null)
        REQUESTS_CPU_VAL=$(echo "$REQUESTS_CPU" | sed 's/m//')

        # Si no hay valor definido, asumir 1000m (equivalente a 1 core)
        [[ -z "$REQUESTS_CPU_VAL" ]] && REQUESTS_CPU_VAL=1000

        # Calcular el porcentaje de uso respecto al CPU solicitado
        CPU_PERC=$(echo "scale=2; ($CPU_VAL / $REQUESTS_CPU_VAL) * 100" | bc)

        # Escribir una línea en el archivo CSV con todos los datos recolectados
        echo "$TIMESTAMP,$POD,$CPU_VAL,$MEM,$CPU_PERC,$NUM_PODS" >> "$OUTPUT_FILE"
    done

    # Esperar antes de la siguiente recolección
    sleep "$INTERVAL"
done
