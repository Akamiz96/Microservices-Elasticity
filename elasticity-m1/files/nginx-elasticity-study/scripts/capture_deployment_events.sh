#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: capture_deployment_events.sh
# DESCRIPCIÓN: Script para recolectar periódicamente todos los eventos del tipo
#              Deployment en Kubernetes, registrándolos con timestamp real del sistema.
#              Adaptado para nombrar el archivo de salida dinámicamente según experimento.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 08 de abril de 2025
# CONTEXTO:
#   - Parte del estudio `nginx-elasticity-study`.
#   - El procesamiento posterior del log permite extraer eventos de escalamiento.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# VALIDACIÓN DE PARÁMETROS
# ---------------------------------------------------------------
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "❌ Error: Debes proporcionar dos identificadores:"
  echo "     1) ID de configuración del HPA (ej. C5)"
  echo "     2) ID de configuración de carga (ej. L02)"
  echo "Uso: ./capture_deployment_events.sh C5 L02"
  exit 1
fi

HPA_ID="$1"
LOAD_ID="$2"

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
OUTPUT_DIR="nginx-elasticity-study/output"
OUTPUT_FILE="$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_events.log"

NAMESPACE="default"
DEPLOYMENT_NAME="nginx-basic"
INTERVAL=10

mkdir -p "$OUTPUT_DIR"

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN DE EVENTOS
# ---------------------------------------------------------------
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")  # Timestamp del sistema en tiempo real
    
    # Obtener eventos del tipo Deployment, ordenados por su creación
    EVENTS=$(kubectl get events --sort-by=.metadata.creationTimestamp -n $NAMESPACE | grep $DEPLOYMENT_NAME)

    # Si se encontraron eventos, procesarlos uno por uno
    if [[ ! -z "$EVENTS" ]]; then
        while IFS= read -r LINE; do
            echo "[$TIMESTAMP] $LINE" >> "$OUTPUT_FILE"
        done <<< "$EVENTS"
    fi

    sleep $INTERVAL
done
