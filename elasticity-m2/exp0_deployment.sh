#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp0_deployment.sh
# DESCRIPCIÓN: Script de despliegue automático del microservicio NGINX+Flask.
#              - Construye imagen de Flask
#              - Aplica todos los manifiestos de Kubernetes
#              - Verifica funcionamiento de la aplicación
# AUTOR: Alejandro Castro
# FECHA: 2025-04-27
# CONTEXTO: Proyecto de evaluación de elasticidad de microservicios.
# ------------------------------------------------------------------------------

# Variables
FLASK_IMAGE_NAME="flask-fib-app:latest"
FLASK_DIR="./deployment/flask"
MANIFESTS_DIR="./deployment/manifests"
NODE_IP="10.195.20.20"

echo "========================================="
echo " INICIO DEL DESPLIEGUE AUTOMATICO"
echo " Microservicios: NGINX + Flask"
echo "========================================="

# Fase 1: Construcción de imagen Flask
echo ""
echo "-----------------------------------------"
echo " FASE 1: Construyendo imagen de Flask"
echo "-----------------------------------------"

cd "$FLASK_DIR" || { echo "ERROR: No se encontró la carpeta $FLASK_DIR"; exit 1; }
docker build -t "$FLASK_IMAGE_NAME" .
cd - > /dev/null

echo "Imagen $FLASK_IMAGE_NAME construida correctamente."

# Fase 2: Aplicación de Manifests de Kubernetes
echo ""
echo "-----------------------------------------"
echo " FASE 2: Aplicando manifiestos de Kubernetes"
echo "-----------------------------------------"

kubectl apply -f "$MANIFESTS_DIR"

echo "Manifiestos aplicados correctamente."

# Fase 3: Verificación de servicios
echo ""
echo "-----------------------------------------"
echo " FASE 3: Verificando servicios desplegados"
echo "-----------------------------------------"

kubectl get svc

echo ""
echo "Servicios esperados:"
echo " - NGINX expuesto en: http://$NODE_IP:30080/compute?n=20"
echo " - Flask expuesto en: http://$NODE_IP:30007/compute?n=20"

# Fase 4: Prueba de la aplicación
echo ""
echo "-----------------------------------------"
echo " FASE 4: Probando la aplicación completa"
echo "-----------------------------------------"

sleep 5  # Espera breve para que los pods terminen de iniciar

RESPONSE=$(curl -s "http://$NODE_IP:30080/compute?n=20")

if [ -z "$RESPONSE" ]; then
    echo "ERROR: No se pudo obtener respuesta de la aplicación."
    exit 1
else
    echo "Respuesta recibida correctamente:"
    echo "$RESPONSE"
fi

echo ""
echo "========================================="
echo " DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "========================================="
