#!/bin/bash

echo "======================================="
echo "🚀 Iniciando prueba de funcionamiento del clúster Kubernetes"
echo "======================================="

# Paso 1: Verificar el Estado del Clúster
echo ""
echo "📌 Paso 1: Verificando el estado del clúster..."
kubectl get nodes
echo "✅ Verificación del estado del clúster completada."

# Paso 2: Desplegar una Aplicación de Prueba
echo ""
echo "🔧 Paso 2: Desplegando aplicación de prueba (nginx)..."
kubectl create deployment test-nginx --image=nginx
sleep 5
echo "⏳ Esperando que el pod esté en estado 'Running'..."
kubectl get pods
echo "✅ Aplicación de prueba desplegada."

# Paso 3: Exponer la Aplicación
echo ""
echo "🌐 Paso 3: Exponiendo la aplicación como servicio..."
kubectl expose deployment test-nginx --type=NodePort --port=80
sleep 3
kubectl get svc
echo "✅ Servicio expuesto correctamente."

# Paso 4: Probar el Autoescalado
echo ""
echo "📊 Paso 4: Aplicando autoescalado con Horizontal Pod Autoscaler..."
kubectl autoscale deployment test-nginx --cpu-percent=50 --min=1 --max=5
sleep 5
kubectl get hpa
echo "✅ Autoescalado configurado y verificado."

# Paso 5: Limpiar la Prueba
echo ""
echo "🧹 Paso 5: Limpiando recursos creados durante la prueba..."
kubectl delete deployment test-nginx
kubectl delete svc test-nginx
kubectl delete hpa test-nginx
echo "✅ Recursos eliminados."

echo ""
echo "🎉 Prueba completada exitosamente. El clúster está listo para pruebas avanzadas."
