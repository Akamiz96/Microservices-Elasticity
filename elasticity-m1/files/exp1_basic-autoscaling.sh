#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp1_basic-autoscaling.sh
# DESCRIPCIÓN: Automatiza el flujo completo del experimento básico de elasticidad:
#              - Despliegue de recursos NGINX + HPA en Kubernetes
#              - Recolección de métricas de CPU y pods
#              - Captura de eventos del Deployment (escalado)
#              - Ejecución de prueba escalonada con k6
#              - Análisis completo de elasticidad (gráficos y métricas)
#              - Limpieza de recursos
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 29 de marzo de 2025
# CONTEXTO:
#   - Utilizado para calcular y visualizar la elasticidad de un microservicio
#     usando la métrica de oferta vs demanda en función del tiempo.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS RELATIVAS
# ---------------------------------------------------------------
BASE_DIR="basic-autoscaling"
MANIFESTS_DIR="$BASE_DIR/manifests"
SCRIPTS_DIR="$BASE_DIR/scripts"
OUTPUT_DIR="$BASE_DIR/output"
METRIC_SCRIPT="$SCRIPTS_DIR/metric_collector_basic.sh"
EVENTS_SCRIPT="$SCRIPTS_DIR/capture_deployment_events.sh"
LOAD_SCRIPT="$SCRIPTS_DIR/basic_load_test.js"
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
# PASO 2: Mostrar IP de nodos y actualizar basic_load_test.js
# ---------------------------------------------------------------
echo ""
echo "[Paso 2] Obteniendo IP de los nodos del clúster:"
kubectl get nodes -o wide
echo ""
echo "Edita el archivo:"
echo "    $LOAD_SCRIPT"
echo "y reemplaza la dirección '<IP_DEL_CLUSTER>' por la IP externa de uno de los nodos"
echo "que aparece en la columna 'EXTERNAL-IP' o 'INTERNAL-IP' del resultado anterior."
echo ""
read -p "Presiona ENTER para continuar una vez que hayas actualizado la IP..."

# ---------------------------------------------------------------
# PASO 3: Iniciar recolección de métricas y eventos en segundo plano
# ---------------------------------------------------------------
echo "[Paso 3] Iniciando recolección de métricas y eventos del deployment..."

# Recolector de métricas
bash "$METRIC_SCRIPT" &
METRIC_PID=$!

# Captura de eventos
bash "$EVENTS_SCRIPT" &
EVENTS_PID=$!

echo "[Info] Recolector de métricas iniciado con PID $METRIC_PID"
echo "[Info] Captura de eventos iniciada con PID $EVENTS_PID"
sleep 5

# ---------------------------------------------------------------
# PASO 4: Ejecutar prueba de carga con k6
# ---------------------------------------------------------------
echo "[Paso 4] Ejecutando prueba de carga con k6..."
K6_START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "$K6_START_TIME" > "$OUTPUT_DIR/k6_start_time.txt"

k6 run --summary-export "$OUTPUT_DIR/k6_summary.json" "$LOAD_SCRIPT"

# ---------------------------------------------------------------
# PASO 5: Esperar breve periodo para capturar post-carga
# ---------------------------------------------------------------
echo "[Paso 5] Esperando 30 segundos adicionales para observar estabilización..."
sleep 30

# ---------------------------------------------------------------
# PASO 6: Detener procesos de recolección
# ---------------------------------------------------------------
echo "[Paso 6] Deteniendo recolección de métricas y eventos..."
kill "$METRIC_PID"
kill "$EVENTS_PID"

# ---------------------------------------------------------------
# PASO 7: Ejecutar análisis y visualizaciones
# ---------------------------------------------------------------
echo "[Paso 7] Ejecutando análisis automático con Docker..."

docker build -t basic-autoscaling-analysis "$ANALYSIS_DIR"
docker run --rm \
  -v "$(pwd)/$OUTPUT_DIR:/app/output" \
  -v "$(pwd)/$ANALYSIS_DIR/images:/app/images" \
  basic-autoscaling-analysis

# ---------------------------------------------------------------
# PASO 8: Eliminar recursos de Kubernetes
# ---------------------------------------------------------------
echo "[Paso 8] Eliminando recursos de Kubernetes..."
kubectl delete -f "$MANIFESTS_DIR/nginx-deployment.yaml"
kubectl delete -f "$MANIFESTS_DIR/hpa.yaml"

# ---------------------------------------------------------------
# FINALIZACIÓN
# ---------------------------------------------------------------
echo ""
echo "[Completado] El experimento básico de elasticidad ha finalizado exitosamente."
echo ""
echo "Archivos generados:"
echo "  - Métricas del sistema:           $OUTPUT_DIR/basic_metrics.csv"
echo "  - Resumen de carga (k6):          $OUTPUT_DIR/k6_summary.json"
echo "  - Timestamp de inicio k6:         $OUTPUT_DIR/k6_start_time.txt"
echo "  - Eventos del deployment:         $OUTPUT_DIR/scaling_events.csv"
echo ""
echo "Imágenes generadas en:"
echo "  - CPU por pod:                    $ANALYSIS_DIR/images/cpu_usage_per_pod.png"
echo "  - CPU por pod + eventos:          $ANALYSIS_DIR/images/cpu_usage_per_pod_with_events.png"
echo "  - Evolución de pods:              $ANALYSIS_DIR/images/pod_count_over_time.png"
echo "  - Pods + eventos:                 $ANALYSIS_DIR/images/pod_count_over_time_with_events.png"
echo "  - Elasticidad:                    $ANALYSIS_DIR/images/elasticity_curve.png"
echo "  - Elasticidad + eventos:          $ANALYSIS_DIR/images/elasticity_curve_with_events.png"
