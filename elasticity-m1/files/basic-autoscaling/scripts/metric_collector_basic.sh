#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: metric_collector_basic.sh
# DESCRIPCIÓN: Script específico para recolectar métricas de CPU y memoria de los pods
#              durante la ejecución del experimento básico de elasticidad.
#              Guarda los resultados en un archivo CSV fijo como referencia para
#              comparar demanda estimada vs recursos ofrecidos.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Diseñado para ser usado exclusivamente con el experimento exp1_basic-autoscaling.
#   - Guarda las métricas en la ruta fija: basic-autoscaling/output/basic_metrics.csv
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
OUTPUT_DIR="basic-autoscaling/output"                  # Carpeta donde se guardará el CSV
OUTPUT_FILE="$OUTPUT_DIR/basic_metrics.csv"            # Archivo de salida fijo

NAMESPACE="default"                                    # Namespace a monitorear
DEPLOYMENT_NAME="nginx-basic"                          # Deployment objetivo
INTERVAL=10                                            # Intervalo de recolección (segundos)

# ---------------------------------------------------------------
# PREPARACIÓN DEL DIRECTORIO DE SALIDA
# ---------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"                                 # Crear carpeta si no existe

# Encabezado del archivo CSV
echo "timestamp,pod,cpu(millicores),memory(bytes),%cpu,num_pods" > "$OUTPUT_FILE"

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN PERIÓDICA DE MÉTRICAS
# ------------------------------------------------------------------------------
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")             # Obtener timestamp actual

    # Obtener el número de pods activos en el namespace (sin encabezados)
    NUM_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers | wc -l)

    # --------------------------------------------------------------------------
    # Recolectar métricas de cada pod usando 'kubectl top'
    # La salida tiene el formato: <pod-name> <cpu> <memory>
    # Para cada línea, se extraen los valores y se procesan:
    #   - cpu: en millicores (ej. 125m → 125)
    #   - memory: se mantiene en bytes (ej. 64Mi)
    #   - %cpu: calculado en relación con el recurso solicitado por el contenedor
    # --------------------------------------------------------------------------
    kubectl top pod -n "$NAMESPACE" --no-headers | while read -r POD CPU MEM; do
        CPU_VAL=${CPU%m}  # Eliminar la 'm' (millicores)

        # Obtener el CPU solicitado en el deployment (resources.requests.cpu)
        REQUESTS_CPU=$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath="{.spec.containers[0].resources.requests.cpu}" 2>/dev/null)
        REQUESTS_CPU_VAL=$(echo "$REQUESTS_CPU" | sed 's/m//')

        # Si no hay valor definido, asumir 1000m (1 core)
        [[ -z "$REQUESTS_CPU_VAL" ]] && REQUESTS_CPU_VAL=1000

        # Calcular el porcentaje de uso respecto al CPU solicitado
        CPU_PERC=$(echo "scale=2; ($CPU_VAL / $REQUESTS_CPU_VAL) * 100" | bc)

        # Escribir una línea en el archivo CSV con todos los datos
        echo "$TIMESTAMP,$POD,$CPU_VAL,$MEM,$CPU_PERC,$NUM_PODS" >> "$OUTPUT_FILE"
    done

    # Esperar antes de la siguiente recolección
    sleep "$INTERVAL"
done
