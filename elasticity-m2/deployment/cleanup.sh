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

# Borrar deployments, services, configmaps
echo "Eliminando manifiestos de Kubernetes..."
kubectl delete -f "$MANIFESTS_DIR/" --ignore-not-found

echo "========================================="
echo " LIMPIEZA COMPLETADA"
echo "========================================="
