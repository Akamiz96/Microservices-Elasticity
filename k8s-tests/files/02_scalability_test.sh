#!/bin/bash

# Script para desplegar una aplicación nginx, configurar HPA y ejecutar pruebas de carga con k6
# Asume que los archivos nginx-deployment.yaml, hpa.yaml y test.js ya existen en el mismo directorio

set -e

# ================================================
# 1. Desplegar la aplicación nginx
# ================================================
echo "[FASE 1] Desplegando la aplicación nginx..."
kubectl apply -f scalability_test/nginx-deployment.yaml
sleep 5

# ================================================
# 2. Aplicar configuración del HPA
# ================================================
echo "[FASE 2] Configurando el Horizontal Pod Autoscaler (HPA)..."
kubectl apply -f scalability_test/hpa.yaml
sleep 5

# ================================================
# 3. Verificar el estado del HPA
# ================================================
echo "[FASE 3] Verificando estado del HPA..."
kubectl get hpa
sleep 2

# ================================================
# 4. Mostrar IPs de los nodos
# ================================================
echo "[INFO] Listando IPs de los nodos para test.js..."
kubectl get nodes -o wide

echo "Reemplaza <IP_DEL_CLUSTER> en el archivo scalability_test/test.js antes de continuar."
echo "Presiona [ENTER] cuando hayas actualizado el archivo."
read

# ================================================
# 5. Verificar e instalar k6 si es necesario
# ================================================
echo "[FASE 4] Verificando si k6 está instalado..."
if ! command -v k6 &> /dev/null; then
  echo "k6 no está instalado. Instalando..."
  sudo apt update && sudo apt install -y gnupg software-properties-common
  curl -s https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
  sudo apt update && sudo apt install -y k6
else
  echo "k6 ya está instalado."
fi
sleep 2

# ================================================
# 6. Iniciar monitoreo en segundo plano
# ================================================
echo "[FASE 5] Iniciando monitoreo en segundo plano (kubectl get hpa -w)..."
MONITOR_LOG="/tmp/hpa_monitor_$(date +%s).log"
kubectl get hpa -w > "$MONITOR_LOG" 2>&1 &
HPA_MONITOR_PID=$!
sleep 2

# ================================================
# 7. Ejecutar prueba de carga
# ================================================
echo "[FASE 6] Ejecutando prueba de carga con k6..."
k6 run scalability_test/test.js

# ================================================
# 8. Finalizar monitoreo y mostrar resultados
# ================================================
echo "[FASE 7] Finalizando monitoreo..."
kill $HPA_MONITOR_PID
sleep 1

echo "[RESULTADO] Resumen del monitoreo del HPA durante la prueba de carga:"
cat "$MONITOR_LOG"
rm "$MONITOR_LOG"

# ================================================
# 9. Nota sobre métricas (en caso de error)
# ================================================
echo "[NOTA] Si no se visualizan correctamente las métricas, asegúrate de tener instalado el Metrics Server."
echo "Puedes instalarlo ejecutando:"
echo "kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
echo "y luego habilitar el flag --kubelet-insecure-tls si es necesario."

# ================================================
# 8. Limpieza opcional de recursos
# ================================================
echo "[FASE 8] ¿Deseas eliminar los recursos creados durante la prueba? (y/n)"
read -r CLEANUP
if [[ "$CLEANUP" == "y" || "$CLEANUP" == "Y" ]]; then
  echo "Eliminando deployment, servicio y HPA..."
  kubectl delete deployment nginx-test
  kubectl delete service nginx-service
  kubectl delete hpa nginx-hpa
  echo "Recursos eliminados correctamente."
else
  echo "Limpieza omitida. Los recursos siguen activos en el clúster."
fi

# ================================================
# 10. Fin del script
# ================================================
