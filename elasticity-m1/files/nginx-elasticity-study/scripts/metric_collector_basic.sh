#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: metric_collector_basic.sh
# DESCRIPCIÓN: Script genérico para recolectar métricas de CPU y memoria de los pods
#              durante la ejecución de experimentos de elasticidad con NGINX.
#              El archivo de salida se nombra dinámicamente con base en los parámetros.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 08 de abril de 2025
# CONTEXTO:
#   - Utilizado dentro del estudio `nginx-elasticity-study`.
#   - Requiere dos parámetros: ID del HPA (C1-C9) y ID del patrón de carga (L01-L06).
#   - Guarda métricas en: nginx-elasticity-study/output/CX_LYY_metrics.csv
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# VALIDACIÓN DE PARÁMETROS
# ---------------------------------------------------------------
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "❌ Error: Debes proporcionar dos identificadores:"
  echo "     1) ID de configuración del HPA (ej. C4)"
  echo "     2) ID de configuración de carga (ej. L03)"
  echo "Uso: ./metric_collector_basic.sh C4 L03"
  exit 1
fi

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
HPA_ID="$1"
LOAD_ID="$2"
OUTPUT_DIR="nginx-elasticity-study/output"
OUTPUT_FILE="$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_metrics.csv"

NAMESPACE="default"
DEPLOYMENT_NAME="nginx-basic"
INTERVAL=10

# ---------------------------------------------------------------
# PREPARACIÓN DEL DIRECTORIO DE SALIDA
# ---------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"

# Encabezado del archivo CSV
echo "timestamp,pod,cpu(millicores),memory(bytes),%cpu,num_pods" > "$OUTPUT_FILE"

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN PERIÓDICA DE MÉTRICAS
# ---------------------------------------------------------------
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
        CPU_VAL=${CPU%m}    # Eliminar la 'm' (millicores)

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
