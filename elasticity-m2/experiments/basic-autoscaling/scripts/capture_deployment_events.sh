#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: capture_deployment_events.sh
# DESCRIPCIÓN: Script genérico para recolectar eventos de Deployment en Kubernetes,
#              registrándolos periódicamente con timestamp real del sistema.
#              Genera un log separado para cada deployment monitoreado.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Adaptado para soportar múltiples microservicios (Flask, NGINX, etc.).
#   - El procesamiento posterior del log permite extraer eventos de escalamiento.
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
NAMESPACE="default"                                           # Namespace donde se encuentra el deployment
OUTPUT_DIR="experiments/basic-autoscaling/output"                # Carpeta donde se guardarán los logs
OUTPUT_FILE="$OUTPUT_DIR/scaling_events_${DEPLOYMENT_NAME}.csv"  # Archivo de salida específico por deployment
INTERVAL=10                                                   # Intervalo de muestreo en segundos

mkdir -p "$OUTPUT_DIR"                                        # Crear carpeta de salida si no existe

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN DE EVENTOS
# ---------------------------------------------------------------
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")                    # Timestamp actual del sistema

    # Obtener eventos relacionados al Deployment ordenados por creación
    EVENTS=$(kubectl get events --sort-by=.metadata.creationTimestamp -n $NAMESPACE | grep $DEPLOYMENT_NAME)

    # Si se encontraron eventos, procesarlos uno por uno
    if [[ ! -z "$EVENTS" ]]; then
        while IFS= read -r LINE; do
            # Guardar el timestamp del sistema + el evento crudo en el archivo CSV
            echo "\"$TIMESTAMP\",\"$LINE\"" >> "$OUTPUT_FILE"
        done <<< "$EVENTS"
    fi

    sleep "$INTERVAL"
done
