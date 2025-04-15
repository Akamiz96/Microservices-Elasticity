#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: capture_deployment_events.sh
# DESCRIPCIÓN: Script para recolectar periódicamente todos los eventos del tipo
#              Deployment en Kubernetes, registrándolos con timestamp real del sistema.
#              Esta versión no filtra eventos de escalamiento, sino que los deja
#              todos en un log plano que luego puede ser procesado por un script externo.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 30 de marzo de 2025
# CONTEXTO:
#   - Se ejecuta en segundo plano durante la prueba de carga.
#   - El procesamiento posterior del log permite extraer los eventos de escalamiento.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
OUTPUT_DIR="basic-autoscaling/output"                  # Carpeta donde se guardará el archivo
OUTPUT_FILE="$OUTPUT_DIR/scaling_events.csv"           # Archivo de salida con los eventos

NAMESPACE="default"                                    # Namespace donde se encuentra el deployment
DEPLOYMENT_NAME="nginx-basic"                          # Nombre del deployment objetivo
INTERVAL=10                                            # Intervalo de muestreo en segundos


mkdir -p "$OUTPUT_DIR"                      # Crear el directorio de salida si no existe
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
            echo "[$TIMESTAMP] $LINE" >> $OUTPUT_FILE
        done <<< "$EVENTS"
    fi

    sleep $INTERVAL
done
