#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp1_microbenchmark_m2.sh
# DESCRIPCIÓN: Automatiza el flujo completo del microbenchmark, incluyendo:
#              - Despliegue de Flask + NGINX + HPAs en Kubernetes
#              - Recolección de métricas de CPU por microservicio
#              - Ejecución de prueba controlada con k6
#              - Análisis de métricas y generación de visualizaciones en Docker
#              - Limpieza completa del entorno
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 27 de abril de 2025
# CONTEXTO:
#   - Este script forma parte del experimento Elasticity M2.
#   - Calcula demanda de CPU por VU/request para dos microservicios separados.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS RELATIVAS
# ---------------------------------------------------------------
DEPLOY_DIR="deployment"
EXPERIMENT_DIR="experiments/microbenchmark"
MANIFESTS_DEPLOY="$DEPLOY_DIR/manifests"
MANIFESTS_EXPERIMENT="$EXPERIMENT_DIR/manifests"
OUTPUT_DIR="$EXPERIMENT_DIR/output"
FILES_DIR="$EXPERIMENT_DIR/files"
IMAGES_DIR="$EXPERIMENT_DIR/analysis/images"
SCRIPTS_DIR="$EXPERIMENT_DIR/scripts"
COLLECTOR_SCRIPT="$SCRIPTS_DIR/metric_collector_microbenchmark.sh"
BENCHMARK_SCRIPT="$SCRIPTS_DIR/benchmark_test.js"
ANALYSIS_DIR="$EXPERIMENT_DIR/analysis"

# ---------------------------------------------------------------
# PASO 1: Desplegar recursos base
# ---------------------------------------------------------------
echo "[Paso 1] Aplicando despliegue base..."
bash "$DEPLOY_DIR/deploy.sh"

# ---------------------------------------------------------------
# PASO 2: Aplicar escaladores HPA
# ---------------------------------------------------------------
echo "[Paso 2] Aplicando HPA para Flask y NGINX..."
kubectl apply -f "$MANIFESTS_EXPERIMENT/hpa-flask.yaml"
kubectl apply -f "$MANIFESTS_EXPERIMENT/hpa-nginx.yaml"

echo "[Info] Esperando 20 segundos para que los pods e HPA se inicialicen..."
sleep 20

# ---------------------------------------------------------------
# PASO 3: Iniciar recolección de métricas en paralelo
# ---------------------------------------------------------------
echo "[Paso 3] Iniciando recolección de métricas para Flask y NGINX..."

mkdir -p "$OUTPUT_DIR"

bash "$COLLECTOR_SCRIPT" flask-app &
PID_FLASK=$!

bash "$COLLECTOR_SCRIPT" nginx-app &
PID_NGINX=$!

echo "[Info] Recolectores iniciados: Flask PID=$PID_FLASK, NGINX PID=$PID_NGINX"
sleep 5

# ---------------------------------------------------------------
# PASO 4: Ejecutar prueba de carga con k6
# ---------------------------------------------------------------
echo "[Paso 4] Ejecutando carga de prueba con k6..."
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
kill "$PID_FLASK"
kill "$PID_NGINX"

# ---------------------------------------------------------------
# PASO 7: Ejecutar análisis automático con Docker
# ---------------------------------------------------------------
echo "[Paso 7] Ejecutando análisis automático en contenedor Docker..."

docker build -t microbenchmark-analysis-2m "$ANALYSIS_DIR"
docker run --rm \
  -v "$(pwd)/$OUTPUT_DIR:/app/output" \
  -v "$(pwd)/$FILES_DIR:/app/files" \
  -v "$(pwd)/$IMAGES_DIR:/app/images" \
  microbenchmark-analysis-2m

# ---------------------------------------------------------------
# PASO 8: Eliminar recursos del clúster
# ---------------------------------------------------------------
echo "[Paso 8] Eliminando despliegue base y HPA..."

bash "$DEPLOY_DIR/cleanup.sh"
kubectl delete -f "$MANIFESTS_EXPERIMENT/hpa-flask.yaml"
kubectl delete -f "$MANIFESTS_EXPERIMENT/hpa-nginx.yaml"

# ---------------------------------------------------------------
# FINALIZACIÓN
# ---------------------------------------------------------------
echo ""
echo "[Completado] El microbenchmark ha finalizado exitosamente."
echo "             - Métricas capturadas en: $OUTPUT_DIR/"
echo "             - Datos de carga:         $OUTPUT_DIR/k6_summary.json"
echo "             - Análisis y estimaciones en: $FILES_DIR/<deployment>/"
echo "             - Imágenes generadas en:  $IMAGES_DIR/<deployment>/"
