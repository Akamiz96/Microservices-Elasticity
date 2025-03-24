#!/bin/bash

# Script para validar el funcionamiento básico de un clúster Kubernetes
# Despliega una aplicación de prueba, la expone, aplica autoescalado y luego limpia los recursos

set -e

# ================================================
# 1. Verificar el estado del clúster
# ================================================
echo "[FASE 1] Verificando el estado del clúster..."
kubectl get nodes
sleep 2

# ================================================
# 2. Desplegar aplicación de prueba
# ================================================
echo "[FASE 2] Desplegando aplicación nginx de prueba..."
kubectl create deployment test-nginx --image=nginx
sleep 5

echo "[INFO] Mostrando estado de los pods desplegados:"
kubectl get pods
sleep 2

# ================================================
# 3. Exponer la aplicación como servicio
# ================================================
echo "[FASE 3] Exponiendo el deployment como servicio NodePort..."
kubectl expose deployment test-nginx --type=NodePort --port=80
sleep 3

kubectl get svc
sleep 2

# ================================================
# 4. Aplicar autoescalado con HPA
# ================================================
echo "[FASE 4] Configurando autoescalado con Horizontal Pod Autoscaler..."
kubectl autoscale deployment test-nginx --cpu-percent=50 --min=1 --max=5
sleep 5

kubectl get hpa
sleep 2

# ================================================
# 5. Limpiar recursos creados
# ================================================
echo "[FASE 5] Eliminando recursos creados durante la prueba..."
kubectl delete deployment test-nginx
kubectl delete svc test-nginx
kubectl delete hpa test-nginx
sleep 2

# ================================================
# Resultado Final
# ================================================
echo "[RESULTADO] Prueba completada exitosamente. El clúster está listo para pruebas avanzadas."

# Fin del script
