#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: capture_deployment_events.sh
# DESCRIPCIÓN: Captura eventos de escalamiento (up/down) del Deployment en
#              Kubernetes y los guarda en un archivo CSV para graficación.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de marzo de 2025
# CONTEXTO:
#   - Se utiliza para visualizar cuándo Kubernetes decide escalar un Deployment
#     hacia arriba o hacia abajo, y marcarlo sobre la curva de elasticidad.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN
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
echo "timestamp,scaling_direction,message" > "$OUTPUT_FILE"

# ---------------------------------------------------------------
# OBTENER EVENTOS Y FILTRAR ESCALAMIENTO
# ---------------------------------------------------------------
kubectl get events -n "$NAMESPACE" --field-selector involvedObject.name=$DEPLOYMENT_NAME \
  --sort-by='.lastTimestamp' --no-headers | while read -r line; do

    # Extraer timestamp y mensaje
    TIMESTAMP=$(echo "$line" | awk '{print $1"T"$2}')
    MESSAGE=$(echo "$line" | cut -d' ' -f5-)

    # Verificar si es un evento de escalamiento
    if echo "$MESSAGE" | grep -qi "Scaled up replica set"; then
        echo "$TIMESTAMP,up,\"$MESSAGE\"" >> "$OUTPUT_FILE"
    elif echo "$MESSAGE" | grep -qi "Scaled down replica set"; then
        echo "$TIMESTAMP,down,\"$MESSAGE\"" >> "$OUTPUT_FILE"
    fi
done