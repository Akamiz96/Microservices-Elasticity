#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp1_basic_autoscaling_m2.sh
# DESCRIPCIÓN: Automatiza el flujo completo del experimento básico de elasticidad M2:
#              - Despliegue de Flask + NGINX + HPAs en Kubernetes
#              - Recolección de métricas de CPU por microservicio
#              - Captura de eventos de escalamiento por microservicio
#              - Ejecución de prueba escalonada con k6
#              - Análisis y visualización de elasticidad
#              - Limpieza completa del entorno
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de abril de 2025
# CONTEXTO:
#   - Basado en experiments/basic-autoscaling.
#   - Estudia elasticidad para dos microservicios simultáneamente.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS RELATIVAS
# ---------------------------------------------------------------
DEPLOY_DIR="deployment"
EXPERIMENT_DIR="experiments/basic-autoscaling"
MANIFESTS_DEPLOY="$DEPLOY_DIR/manifests"
MANIFESTS_EXPERIMENT="$EXPERIMENT_DIR/manifests"
OUTPUT_DIR="$EXPERIMENT_DIR/output"
IMAGES_DIR="$EXPERIMENT_DIR/analysis/images"
FILES_DIR="$EXPERIMENT_DIR/files"
SCRIPTS_DIR="$EXPERIMENT_DIR/scripts"
COLLECTOR_SCRIPT="$SCRIPTS_DIR/metric_collector_basic.sh"
EVENTS_SCRIPT="$SCRIPTS_DIR/capture_deployment_events.sh"
LOAD_SCRIPT="$SCRIPTS_DIR/basic_load_test.js"
ANALYSIS_DIR="$EXPERIMENT_DIR/analysis"

# ---------------------------------------------------------------
# PASO 1: Desplegar microservicios base (Flask + NGINX)
# ---------------------------------------------------------------
echo "[Paso 1] Aplicando despliegue base..."
bash "$DEPLOY_DIR/deploy.sh"

# ---------------------------------------------------------------
# PASO 2: Aplicar HPAs para Flask y NGINX
# ---------------------------------------------------------------
echo "[Paso 2] Aplicando HPA para Flask y NGINX..."
kubectl apply -f "$MANIFESTS_EXPERIMENT/hpa-flask.yaml"
kubectl apply -f "$MANIFESTS_EXPERIMENT/hpa-nginx.yaml"

echo "[Info] Esperando 20 segundos para inicializar pods y HPAs..."
sleep 20

# ---------------------------------------------------------------
# PASO 3: Mostrar IP de nodos para edición manual
# ---------------------------------------------------------------
echo "[Paso 3] Obteniendo IP de los nodos:"
kubectl get nodes -o wide
echo ""
echo "Edita el archivo:"
echo "    $LOAD_SCRIPT"
echo "y actualiza la IP externa del nodo."
read -p "Presiona ENTER una vez hayas actualizado la IP correcta en el script de carga..."

# ---------------------------------------------------------------
# PASO 4: Iniciar recolección de métricas y captura de eventos
# ---------------------------------------------------------------
echo "[Paso 4] Iniciando recolección de métricas y eventos..."

mkdir -p "$OUTPUT_DIR"

# Recolector de métricas por microservicio
bash "$COLLECTOR_SCRIPT" flask-app &
PID_FLASK=$!

bash "$COLLECTOR_SCRIPT" nginx-app &
PID_NGINX=$!

# Captura de eventos por microservicio
bash "$EVENTS_SCRIPT" flask-app &
PID_EVENTS_FLASK=$!

bash "$EVENTS_SCRIPT" nginx-app &
PID_EVENTS_NGINX=$!

echo "[Info] Recolectores de métricas iniciados: Flask PID=$PID_FLASK, NGINX PID=$PID_NGINX"
echo "[Info] Captura de eventos iniciada: Flask PID=$PID_EVENTS_FLASK, NGINX PID=$PID_EVENTS_NGINX"
sleep 5

# ---------------------------------------------------------------
# PASO 5: Ejecutar prueba de carga controlada con k6
# ---------------------------------------------------------------
echo "[Paso 5] Ejecutando prueba de carga con k6..."
K6_START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "$K6_START_TIME" > "$OUTPUT_DIR/k6_start_time.txt"

k6 run --out csv="$OUTPUT_DIR/k6_results.csv" --summary-export "$OUTPUT_DIR/k6_summary.json" "$LOAD_SCRIPT"

# ---------------------------------------------------------------
# PASO 6: Esperar estabilización
# ---------------------------------------------------------------
echo "[Paso 6] Esperando 30 segundos para capturar fase post-carga..."
sleep 30

# ---------------------------------------------------------------
# PASO 7: Finalizar recolección
# ---------------------------------------------------------------
echo "[Paso 7] Deteniendo procesos de recolección..."
kill "$PID_FLASK"
kill "$PID_NGINX"
kill "$PID_EVENTS_FLASK"
kill "$PID_EVENTS_NGINX"

# ---------------------------------------------------------------
# PASO 8: Ejecutar análisis completo en Docker
# ---------------------------------------------------------------
echo "[Paso 8] Ejecutando análisis automático en contenedor Docker..."

docker build -t basic-autoscaling-analysis-m2 "$ANALYSIS_DIR"
docker run --rm \
  -v "$(pwd)/$OUTPUT_DIR:/app/output" \
  -v "$(pwd)/$ANALYSIS_DIR/images:/app/images" \
  basic-autoscaling-analysis-m2

# ---------------------------------------------------------------
# PASO 9: Eliminar recursos de Kubernetes
# ---------------------------------------------------------------
echo "[Paso 9] Eliminando despliegue y HPA de los microservicios..."

bash "$DEPLOY_DIR/cleanup.sh"
kubectl delete -f "$MANIFESTS_EXPERIMENT/hpa-flask.yaml"
kubectl delete -f "$MANIFESTS_EXPERIMENT/hpa-nginx.yaml"

# ---------------------------------------------------------------
# FINALIZACIÓN
# ---------------------------------------------------------------
echo ""
echo "[Completado] El experimento de elasticidad M2 ha finalizado exitosamente."
echo ""
echo "Resultados disponibles en:"
echo "  - Métricas capturadas:           $OUTPUT_DIR/"
echo "  - Datos de carga k6:             $OUTPUT_DIR/k6_summary.json"
echo "  - Imágenes y análisis:           $IMAGES_DIR/<deployment>/"
echo ""
