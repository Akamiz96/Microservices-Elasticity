#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: deploy.sh
# DESCRIPCIÓN: Construye la imagen de Flask, importa en containerd y despliega.
# AUTOR: Alejandro Castro
# FECHA: 2025-04-27
# CONTEXTO: Proyecto Elasticity M2
# ------------------------------------------------------------------------------

set -euo pipefail

# Variables
IMAGE="flask-fib-app:latest"
FLASK_DIR="deployment/flask"
MANIFESTS_DIR="deployment/manifests"

echo "========================================="
echo " INICIO DEL DESPLIEGUE AUTOMATICO"
echo "========================================="

# # 1. Construir imagen Flask
# echo "Construyendo imagen de Flask..."
# cd "$FLASK_DIR"
# docker build -t "$IMAGE" .
# cd - > /dev/null
# echo "Imagen $IMAGE construida correctamente."

# # 2. Importar imagen a containerd
# echo "Importando imagen en containerd..."
# docker save "$IMAGE" | sudo ctr -n k8s.io images import -
# echo "Imagen importada en containerd."

# 3. Aplicar ConfigMap primero
echo "Aplicando ConfigMap de NGINX..."
kubectl apply -f "$MANIFESTS_DIR/nginx-configmap.yaml"

# 4. Aplicar todos los demás manifests
echo "Aplicando manifiestos de Kubernetes..."
kubectl apply -f "$MANIFESTS_DIR/"

echo "========================================="
echo " DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "========================================="
