#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: capture_deployment_events.sh
# DESCRIPCIÓN: Script para recolectar eventos de escalamiento del Deployment
#              en Kubernetes, registrando únicamente los eventos "Scaled up"
#              o "Scaled down". Se guarda un log estructurado con timestamp real.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 29 de marzo de 2025
# CONTEXTO:
#   - Este script captura eventos generados por el HPA durante la ejecución
#     de una prueba de elasticidad.
#   - Se ejecuta en segundo plano y se sincroniza con la recolección de métricas.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------
OUTPUT_DIR="basic-autoscaling/output"                  # Carpeta donde se guardará el archivo
OUTPUT_FILE="$OUTPUT_DIR/scaling_events.csv"           # Archivo de salida con los eventos

NAMESPACE="default"                                    # Namespace donde se encuentra el deployment
DEPLOYMENT_NAME="nginx-basic"                          # Nombre del deployment objetivo
INTERVAL=10                                            # Intervalo de muestreo en segundos

# ---------------------------------------------------------------
# PREPARACIÓN DEL DIRECTORIO DE SALIDA
# ---------------------------------------------------------------
mkdir -p "$OUTPUT_DIR"                                 # Asegurar que exista la carpeta de salida

# Encabezado del archivo CSV
echo "timestamp,scaling_direction,message" > "$OUTPUT_FILE"

# ---------------------------------------------------------------
# BUCLE DE RECOLECCIÓN DE EVENTOS
# ---------------------------------------------------------------
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")             # Timestamp real del sistema

    # Obtener eventos recientes del deployment, ordenados por fecha de creación
    EVENTS=$(kubectl get events -n "$NAMESPACE" --sort-by=.metadata.creationTimestamp | grep "deployment/$DEPLOYMENT_NAME" | grep -E "Scaled up|Scaled down")

    # Si hay eventos, procesarlos línea por línea
    if [[ ! -z "$EVENTS" ]]; then
        while IFS= read -r LINE; do

            # Determinar tipo de evento (escalado hacia arriba o hacia abajo)
            if echo "$LINE" | grep -q "Scaled up"; then
                DIRECTION="scaleup"
            else
                DIRECTION="scaledown"
            fi

            # Escapar comillas internas para que el CSV no se rompa
            MESSAGE=$(echo "$LINE" | sed 's/"/""/g')

            # Escribir línea estructurada en el CSV
            echo "\"$TIMESTAMP\",\"$DIRECTION\",\"$MESSAGE\"" >> "$OUTPUT_FILE"
        done <<< "$EVENTS"
    fi

    # Esperar antes del siguiente ciclo
    sleep "$INTERVAL"
done
