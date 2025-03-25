#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: 03_load_test.sh
# DESCRIPCIÓN: Automatiza el flujo completo de una prueba de carga dentro del
#              entorno de prueba ubicado en 'files/load_test/', incluyendo:
#              - Despliegue de recursos en Kubernetes (Deployment + HPA)
#              - Recolección periódica de métricas de recursos
#              - Ejecución de carga con k6
#              - Generación de visualizaciones con Docker
#              - Limpieza de recursos del clúster
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 25 de marzo de 2025
# CONTEXTO:
#   Este script forma parte de un experimento de escalabilidad horizontal en Kubernetes.
#   Ejecuta una carga progresiva sobre un servicio NGINX y observa la reacción del
#   Horizontal Pod Autoscaler (HPA) mediante la recolección de métricas.
#
#   Debe ejecutarse directamente desde la misma ubicación en la que se encuentra,
#   es decir, dentro del directorio 'files/' (donde se encuentra la carpeta 'load_test/').
#
#   El análisis final se realiza mediante scripts Python ejecutados en un contenedor Docker.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS RELATIVAS
# ---------------------------------------------------------------
BASE_DIR="load_test"
MANIFESTS_DIR="$BASE_DIR/manifests"
SCRIPTS_DIR="$BASE_DIR/scripts"
OUTPUT_DIR="$BASE_DIR/output"
METRIC_SCRIPT="$SCRIPTS_DIR/metric_collector.sh"
TEST_SCRIPT="$SCRIPTS_DIR/test.js"
ANALYSIS_DIR="$BASE_DIR/analysis"

# ---------------------------------------------------------------
# PASO 1: Desplegar manifiestos en Kubernetes
# ---------------------------------------------------------------
echo "[Paso 1] Aplicando manifiestos de Kubernetes..."
kubectl apply -f "$MANIFESTS_DIR/nginx-deployment.yaml"
kubectl apply -f "$MANIFESTS_DIR/hpa.yaml"

echo "[Info] Esperando 20 segundos para que los pods se inicialicen correctamente..."
sleep 20

# ---------------------------------------------------------------
# PASO 2: Mostrar IP de nodos y actualizar test.js
# ---------------------------------------------------------------
echo ""
echo "[Paso 2] Obteniendo IP de los nodos del clúster:"
kubectl get nodes -o wide
echo ""
echo "Edita el archivo:"
echo "    $TEST_SCRIPT"
echo "y reemplaza la dirección '<IP_DEL_CLUSTER>' por la IP externa de uno de los nodos"
echo "que aparece en la columna 'EXTERNAL-IP' o 'INTERNAL-IP' del resultado anterior."
echo ""
read -p "Presiona ENTER para continuar una vez que hayas actualizado la IP..."

# ---------------------------------------------------------------
# PASO 3: Iniciar recolección de métricas en segundo plano
# ---------------------------------------------------------------
echo "[Paso 3] Iniciando recolección de métricas..."
bash "$METRIC_SCRIPT" &
METRIC_PID=$!

echo "[Info] Recolector de métricas iniciado con PID $METRIC_PID"
sleep 5

# ---------------------------------------------------------------
# PASO 4: Ejecutar prueba de carga
# ---------------------------------------------------------------
echo "[Paso 4] Ejecutando prueba de carga con k6..."
k6 run "$TEST_SCRIPT"

# ---------------------------------------------------------------
# PASO 5: Esperar desescalado y mostrar progreso
# ---------------------------------------------------------------
echo "[Paso 5] Esperando 5 minutos adicionales para monitorear el desescalado de recursos..."

WAIT_TIME=300  # 5 minutos en segundos
for ((i=WAIT_TIME; i>0; i--)); do
    printf "\r[Info] Tiempo restante para finalizar monitoreo: %3d segundos..." "$i"
    sleep 1
done
echo -e "\n[Info] Monitoreo completado. Procediendo con la finalización."

# ---------------------------------------------------------------
# PASO 6: Finalizar recolección de métricas
# ---------------------------------------------------------------
echo "[Paso 6] Deteniendo recolección de métricas..."
kill "$METRIC_PID"

# ---------------------------------------------------------------
# PASO 7: Generar visualizaciones con Docker
# ---------------------------------------------------------------
echo "[Paso 7] Generando gráficos a partir de las métricas..."

docker build -t loadtest-analysis "$ANALYSIS_DIR"
docker run --rm \
  -v "$(pwd)/$OUTPUT_DIR:/app/output" \
  -v "$(pwd)/$ANALYSIS_DIR/images:/app/images" \
  loadtest-analysis

# ---------------------------------------------------------------
# PASO 8: Eliminar recursos del clúster
# ---------------------------------------------------------------
echo "[Paso 8] Eliminando recursos de Kubernetes..."
kubectl delete -f "$MANIFESTS_DIR/nginx-deployment.yaml"
kubectl delete -f "$MANIFESTS_DIR/hpa.yaml"

# ---------------------------------------------------------------
# FINALIZACIÓN
# ---------------------------------------------------------------
echo ""
echo "[Completado] La prueba de carga ha finalizado exitosamente."
echo "             - Métricas almacenadas en: $OUTPUT_DIR/metrics.csv"
echo "             - Imágenes generadas en:   $ANALYSIS_DIR/images/"
