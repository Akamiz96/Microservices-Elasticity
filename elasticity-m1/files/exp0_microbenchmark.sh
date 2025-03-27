#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp0_microbenchmark.sh
# DESCRIPCIÓN: Automatiza el flujo completo del microbenchmark, incluyendo:
#              - Despliegue de recursos NGINX + HPA en Kubernetes
#              - Recolección de métricas de uso de CPU
#              - Ejecución de prueba controlada con k6
#              - Análisis de métricas y estimación de demanda con Docker
#              - Limpieza del entorno
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de marzo de 2025
# CONTEXTO:
#   - Este script forma parte del experimento base para estimar la elasticidad.
#   - Permite calcular cuántos millicores consume cada VU o cada request.
#   - Debe ejecutarse desde la raíz del proyecto.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS RELATIVAS
# ---------------------------------------------------------------
BASE_DIR="microbenchmark"
MANIFESTS_DIR="$BASE_DIR/manifests"
SCRIPTS_DIR="$BASE_DIR/scripts"
OUTPUT_DIR="$BASE_DIR/output"
METRIC_SCRIPT="$SCRIPTS_DIR/metric_collector_microbenchmark.sh"
BENCHMARK_SCRIPT="$SCRIPTS_DIR/benchmark_test.js"
ANALYSIS_DIR="$BASE_DIR/analysis"
FILES_DIR="$ANALYSIS_DIR/files"

# ---------------------------------------------------------------
# PASO 1: Desplegar manifiestos en Kubernetes
# ---------------------------------------------------------------
echo "[Paso 1] Aplicando manifiestos de Kubernetes..."
kubectl apply -f "$MANIFESTS_DIR/nginx-deployment.yaml"
kubectl apply -f "$MANIFESTS_DIR/hpa.yaml"

echo "[Info] Esperando 20 segundos para que los pods se inicialicen correctamente..."
sleep 20

# ---------------------------------------------------------------
# PASO 2: Mostrar IP de nodos y actualizar benchmark_test.js
# ---------------------------------------------------------------
echo ""
echo "[Paso 2] Obteniendo IP de los nodos del clúster:"
kubectl get nodes -o wide
echo ""
echo "Edita el archivo:"
echo "    $BENCHMARK_SCRIPT"
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
# PASO 4: Ejecutar microbenchmark con k6
# ---------------------------------------------------------------
echo "[Paso 4] Ejecutando prueba de carga con k6..."
k6 run --summary-export "$OUTPUT_DIR/k6_summary.json" "$BENCHMARK_SCRIPT"

# ---------------------------------------------------------------
# PASO 5: Esperar breve periodo para capturar post-carga
# ---------------------------------------------------------------
echo "[Paso 5] Esperando 30 segundos adicionales para observar estabilización..."
sleep 30

# ---------------------------------------------------------------
# PASO 6: Finalizar recolección de métricas
# ---------------------------------------------------------------
echo "[Paso 6] Deteniendo recolección de métricas..."
kill "$METRIC_PID"

# ---------------------------------------------------------------
# PASO 7: Generar visualizaciones y métricas con Docker
# ---------------------------------------------------------------
echo "[Paso 7] Ejecutando análisis automático con Docker..."

docker build -t microbenchmark-analysis "$ANALYSIS_DIR"
docker run --rm \
  -v "$(pwd)/$OUTPUT_DIR:/app/output" \
  -v "$(pwd)/$FILES_DIR:/app/files" \
  -v "$(pwd)/$ANALYSIS_DIR/images:/app/images" \
  microbenchmark-analysis

# ---------------------------------------------------------------
# PASO 8: Eliminar recursos del clúster
# ---------------------------------------------------------------
echo "[Paso 8] Eliminando recursos de Kubernetes..."
kubectl delete -f "$MANIFESTS_DIR/deployment.yaml"
kubectl delete -f "$MANIFESTS_DIR/hpa.yaml"

# ---------------------------------------------------------------
# FINALIZACIÓN
# ---------------------------------------------------------------
echo ""
echo "[Completado] El microbenchmark ha finalizado exitosamente."
echo "             - Métricas almacenadas en: $OUTPUT_DIR/microbenchmark_metrics.csv"
echo "             - Datos de carga:           $OUTPUT_DIR/k6_summary.json"
echo "             - Estimaciones en:          $FILES_DIR/microbenchmark_summary.txt"
echo "             - Estimaciones en csv:      $FILES_DIR/microbenchmark_summary.csv"
echo "             - Imágenes generadas en:    $ANALYSIS_DIR/images/"
