#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp0_deployment.sh
# DESCRIPCIÓN: Construye, importa e implementa automáticamente la aplicación NGINX + Flask.
# AUTOR: Alejandro Castro
# FECHA: 2025-04-27
# CONTEXTO: Proyecto Elasticity M2
# ------------------------------------------------------------------------------

set -euo pipefail

# Variables
IMAGE="flask-fib-app:latest"
FLASK_DIR="deployment/flask"
MANIFESTS_DIR="deployment/manifests"
NODE_IP="10.195.20.20"
NAMESPACE="default"  # De momento usamos "default", luego podrías cambiarlo si quieres

echo "========================================="
echo " INICIO DEL DESPLIEGUE AUTOMATICO"
echo " Microservicios: NGINX + Flask"
echo "========================================="

# Fase 1: Construir imagen Flask
echo ""
echo "-----------------------------------------"
echo " FASE 1: Construyendo imagen de Flask"
echo "-----------------------------------------"

cd "$FLASK_DIR" || { echo "ERROR: No se encontró la carpeta $FLASK_DIR"; exit 1; }
docker build -t "$IMAGE" .
cd - > /dev/null
echo "Imagen $IMAGE construida correctamente."

# Fase 2: Importar imagen en containerd
echo ""
echo "-----------------------------------------"
echo " FASE 2: Importando imagen en containerd"
echo "-----------------------------------------"

docker save "$IMAGE" | sudo ctr -n k8s.io images import -
echo "Imagen importada en containerd correctamente."

# Fase 3: Aplicar manifiestos
echo ""
echo "-----------------------------------------"
echo " FASE 3: Aplicando manifiestos de Kubernetes"
echo "-----------------------------------------"

kubectl apply -f "$MANIFESTS_DIR"
echo "Manifiestos aplicados correctamente."

# Fase 4: Esperar rollout de los deployments
echo ""
echo "-----------------------------------------"
echo " FASE 4: Esperando rollout de los deployments"
echo "-----------------------------------------"

kubectl rollout status deployment/flask-app -n "$NAMESPACE"
kubectl rollout status deployment/nginx-app -n "$NAMESPACE"

# Fase 5: Verificar servicios y pods
echo ""
echo "-----------------------------------------"
echo " FASE 5: Verificando servicios desplegados"
echo "-----------------------------------------"

kubectl get pods -o wide -n "$NAMESPACE"
kubectl get svc -n "$NAMESPACE"

echo ""
echo "Servicios esperados:"
echo " - NGINX expuesto en: http://$NODE_IP:30080/compute?n=20"
echo " - Flask expuesto en: http://$NODE_IP:30007/compute?n=20"

# Fase 6: Probar la aplicación
echo ""
echo "-----------------------------------------"
echo " FASE 6: Probando la aplicación completa"
echo "-----------------------------------------"

sleep 5  # Esperar a que NGINX esté listo

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
