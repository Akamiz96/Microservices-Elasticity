#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: run_all_experiments.sh
# DESCRIPCIÓN: Ejecuta de forma automatizada todos los experimentos combinando
#              configuraciones de HPA para NGINX y Flask con diferentes cargas.
#              Para cada combinación:
#                - Despliega servicios y HPAs
#                - Ejecuta prueba de carga
#                - Captura métricas y eventos
#                - Procesa análisis en Docker
#                - Mueve resultados a carpeta limpia
#                - Espera antes del siguiente experimento
# AUTOR: Alejandro Castro Martínez
# FECHA: 30 de abril de 2025
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN DE RUTAS Y VARIABLES GLOBALES
# ---------------------------------------------------------------
PROJECT_DIR="nginx-flask-elasticity-study"
DEPLOY_DIR="$PROJECT_DIR/deployment"
MANIFESTS_DIR="$PROJECT_DIR/manifests"
K6_CONFIG_DIR="$PROJECT_DIR/scripts/k6_configs"
ANALYSIS_DIR="$PROJECT_DIR/analysis"
OUTPUT_DIR="$PROJECT_DIR/output"
FILES_DIR="$PROJECT_DIR/files"
IMAGES_DIR="$ANALYSIS_DIR/images"

RESULTS_DIR="$PROJECT_DIR/results"
LOG_DIR="exp_logs/nginx-flask-elasticity-study"
mkdir -p "$RESULTS_DIR"
mkdir -p "$LOG_DIR"
LOG_CENTRAL="$LOG_DIR/experiment_log.txt"
echo "Inicio del experimento: $(date)" | tee -a "$LOG_CENTRAL"

# ---------------------------------------------------------------
# LISTA DE CONFIGURACIONES A PROBAR
# ---------------------------------------------------------------
HPAS_NGINX=(C1 C2 C3 C4 C5 C6 C7 C8 C9)
HPAS_FLASK=(C1 C2 C3 C4 C5 C6 C7 C8 C9)
LOADS=(L01 L02 L03 L04 L05 L06)

# ---------------------------------------------------------------
# BUCLE PRINCIPAL SOBRE TODAS LAS COMBINACIONES
# ---------------------------------------------------------------
for HPA_NGINX in "${HPAS_NGINX[@]}"; do
  for HPA_FLASK in "${HPAS_FLASK[@]}"; do
    for LOAD_ID in "${LOADS[@]}"; do

      START_TIME=$(date)
      EXP_ID="N-${HPA_NGINX}-F-${HPA_FLASK}-L-${LOAD_ID}"
      LOG_FILE="$LOG_DIR/${EXP_ID}.txt"

      echo "==============================================================" | tee -a "$LOG_CENTRAL"
      echo "[$START_TIME] Inicio del experimento $EXP_ID" | tee -a "$LOG_CENTRAL"
      echo "Inicio: $START_TIME" | tee -a "$LOG_FILE"

      echo "[Paso 1] Aplicando manifiestos..." | tee -a "$LOG_FILE"
      kubectl apply -f "$MANIFESTS_DIR/nginx-deployment.yaml" 2>&1 | tee -a "$LOG_FILE"
      kubectl apply -f "$MANIFESTS_DIR/flask-deployment.yaml" 2>&1 | tee -a "$LOG_FILE"
      kubectl apply -f "$MANIFESTS_DIR/generated/${HPA_NGINX}_nginx_hpa.yaml" 2>&1 | tee -a "$LOG_FILE"
      kubectl apply -f "$MANIFESTS_DIR/generated/${HPA_FLASK}_flask_hpa.yaml" 2>&1 | tee -a "$LOG_FILE"

      echo "[Paso 2] Esperando 20 segundos para inicializar..." | tee -a "$LOG_FILE"
      sleep 20

      echo "[Paso 3] Iniciando recolección de métricas y eventos..." | tee -a "$LOG_FILE"
      bash "$PROJECT_DIR/scripts/metric_collector_microbenchmark.sh" flask-app &
      PID_FLASK=$!
      bash "$PROJECT_DIR/scripts/metric_collector_microbenchmark.sh" nginx-app &
      PID_NGINX=$!
      bash "$PROJECT_DIR/scripts/capture_deployment_events.sh" flask-app &
      PID_EVENTS_FLASK=$!
      bash "$PROJECT_DIR/scripts/capture_deployment_events.sh" nginx-app &
      PID_EVENTS_NGINX=$!

      echo "[Paso 4] Ejecutando prueba de carga con k6 ($LOAD_ID)..." | tee -a "$LOG_FILE"
      K6_START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
      echo "$K6_START_TIME" > "$OUTPUT_DIR/k6_start_time.txt"
      K6_CONF="$K6_CONFIG_DIR/${LOAD_ID}_config.json" \
      LOAD_ID="$LOAD_ID" \
      k6 run --out csv="$OUTPUT_DIR/k6_results.csv" \
             --summary-export "$OUTPUT_DIR/k6_summary.json" \
             "$PROJECT_DIR/scripts/load_test_runner.js" 2>&1 | tee -a "$LOG_FILE"

      echo "[Paso 5] Esperando 10 minutos post-carga..." | tee -a "$LOG_FILE"
      sleep 600

      echo "[Paso 6] Finalizando procesos de recolección..." | tee -a "$LOG_FILE"
      kill "$PID_FLASK" "$PID_NGINX" "$PID_EVENTS_FLASK" "$PID_EVENTS_NGINX"

      echo "[Paso 7] Ejecutando análisis en Docker..." | tee -a "$LOG_FILE"
      docker build -t elasticity-analysis "$ANALYSIS_DIR" 2>&1 | tee -a "$LOG_FILE"
      docker run --rm \
        -v "$(pwd)/$OUTPUT_DIR:/app/output" \
        -v "$(pwd)/$IMAGES_DIR:/app/images" \
        -v "$(pwd)/$FILES_DIR:/app/files" \
        -v "$(pwd)/$K6_CONFIG_DIR:/app/k6_configs" \
        -e LOAD_ID="$LOAD_ID" \
        elasticity-analysis 2>&1 | tee -a "$LOG_FILE"

      echo "[Paso 8] Moviendo resultados a carpeta de almacenamiento final..." | tee -a "$LOG_FILE"
      DEST_DIR="$RESULTS_DIR/$EXP_ID"
      mkdir -p "$DEST_DIR/images" "$DEST_DIR/output" "$DEST_DIR/files"
      mv "$IMAGES_DIR"/* "$DEST_DIR/images/" 2>/dev/null
      mv "$OUTPUT_DIR"/* "$DEST_DIR/output/" 2>/dev/null
      mv "$FILES_DIR"/* "$DEST_DIR/files/" 2>/dev/null

      echo "[Paso 9] Limpiando entorno de Kubernetes..." | tee -a "$LOG_FILE"
      bash "$DEPLOY_DIR/cleanup.sh" 2>&1 | tee -a "$LOG_FILE"
      kubectl delete -f "$MANIFESTS_DIR/generated/${HPA_NGINX}_nginx_hpa.yaml" 2>&1 | tee -a "$LOG_FILE"
      kubectl delete -f "$MANIFESTS_DIR/generated/${HPA_FLASK}_flask_hpa.yaml" 2>&1 | tee -a "$LOG_FILE"

      END_TIME=$(date)
      echo "[$END_TIME] Fin del experimento $EXP_ID" | tee -a "$LOG_CENTRAL"

      echo "Esperando 5 minutos antes del siguiente experimento..." | tee -a "$LOG_FILE"
      sleep 5m
    done
  done
done

# ---------------------------------------------------------------
# FINALIZACIÓN GENERAL
# ---------------------------------------------------------------
echo "==============================================================" | tee -a "$LOG_CENTRAL"
echo "Fin del experimento: $(date)" | tee -a "$LOG_CENTRAL"
echo "Todos los experimentos han sido ejecutados satisfactoriamente." | tee -a "$LOG_CENTRAL"
echo "==============================================================" | tee -a "$LOG_CENTRAL"
