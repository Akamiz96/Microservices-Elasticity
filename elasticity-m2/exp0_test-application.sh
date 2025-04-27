#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: test.sh
# DESCRIPCIÓN: Ejecuta despliegue, prueba la aplicación, y luego limpia.
# AUTOR: Alejandro Castro
# FECHA: 2025-04-27
# CONTEXTO: Proyecto Elasticity M2
# ------------------------------------------------------------------------------

set -euo pipefail

# Variables
NODE_IP="10.195.20.20"

echo "========================================="
echo " TEST AUTOMATICO DE LA APLICACION"
echo "========================================="

# 1. Desplegar la aplicación
echo "Desplegando la aplicación..."
./deployment/deploy.sh

# 2. Esperar que los pods estén listos
echo "Esperando rollout de los deployments..."
kubectl rollout status deployment/flask-app
kubectl rollout status deployment/nginx-app

# 3. Probar la aplicación
echo "Probando acceso a través de NGINX..."

sleep 5  # Espera breve para que nginx esté levantado

RESPONSE=$(curl -s "http://$NODE_IP:30080/compute?n=20")

if [ -z "$RESPONSE" ]; then
    echo "ERROR: No se pudo obtener respuesta de la aplicación."
    ./deployment/cleanup.sh
    exit 1
else
    echo "Respuesta recibida correctamente:"
    echo "$RESPONSE"
fi

# 4. Limpiar todo
echo "Limpiando recursos desplegados..."
./deployment/cleanup.sh

echo "========================================="
echo " TEST COMPLETADO EXITOSAMENTE"
echo "========================================="
