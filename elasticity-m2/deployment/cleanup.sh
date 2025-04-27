#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: cleanup.sh
# DESCRIPCIÓN: Limpia todos los recursos desplegados en Kubernetes.
# AUTOR: Alejandro Castro
# FECHA: 2025-04-27
# CONTEXTO: Proyecto Elasticity M2
# ------------------------------------------------------------------------------

set -euo pipefail

# Variables
MANIFESTS_DIR="./deployment/manifests"

echo "========================================="
echo " INICIO DE LA LIMPIEZA DE RECURSOS"
echo "========================================="

# 1. Eliminar deployments, services, configmaps
echo "Eliminando manifiestos de Kubernetes..."
kubectl delete -f "$MANIFESTS_DIR/" --ignore-not-found

# 2. Esperar unos segundos
sleep 3

# 3. Forzar eliminación de pods que queden en Terminating
echo "Forzando eliminación de pods restantes..."
kubectl get pods --no-headers=true | awk '/Terminating/ {print $1}' | while read pod; do
    echo "Forzando eliminación de pod $pod..."
    kubectl delete pod "$pod" --grace-period=0 --force
done

echo "========================================="
echo " LIMPIEZA COMPLETADA"
echo "========================================="

