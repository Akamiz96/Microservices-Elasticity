#!/bin/bash

# ------------------------------------------------------------------------------
# ARCHIVO: exp2_nginx-elasticity-study.sh
# DESCRIPCIÓN: Automatiza la ejecución de todos los experimentos combinando
#              configuraciones de HPA (C1-C9) y patrones de carga (L01-L06).
#              Se despliegan recursos, se recolectan métricas, se lanza la carga,
#              se analiza el experimento y se organizan resultados por combinación.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# PARÁMETRO OPCIONAL: Modo verbose (mostrar output en consola)
# ---------------------------------------------------------------
VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
  VERBOSE=true
fi

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE RUTAS
# ---------------------------------------------------------------
BASE_DIR="nginx-elasticity-study"
MANIFESTS_DIR="$BASE_DIR/manifests"
SCRIPTS_DIR="$BASE_DIR/scripts"
OUTPUT_DIR="$BASE_DIR/output"
ANALYSIS_DIR="$BASE_DIR/analysis"
LOG_DIR="exp_logs/nginx-elasticity-study"
K6_CONFIG_DIR="$SCRIPTS_DIR/k6_configs"

METRIC_SCRIPT="$SCRIPTS_DIR/metric_collector_basic.sh"
EVENTS_SCRIPT="$SCRIPTS_DIR/capture_deployment_events.sh"
LOAD_SCRIPT="$SCRIPTS_DIR/load_test_runner.js"

mkdir -p "$LOG_DIR"
LOG_CENTRAL="$LOG_DIR/experiment_log.txt"
echo "Inicio del experimento: $(date)" | tee -a "$LOG_CENTRAL"

# ---------------------------------------------------------------
# LISTA DE CONFIGURACIONES A PROBAR
# ---------------------------------------------------------------
HPAS=(C1 C2 C3 C4 C5 C6 C7 C8 C9)
LOADS=(L01 L02 L03 L04 L05 L06)

FIRST_RUN=true

# ---------------------------------------------------------------
# BUCLE PRINCIPAL SOBRE TODAS LAS COMBINACIONES
# ---------------------------------------------------------------
for HPA_ID in "${HPAS[@]}"; do
  for LOAD_ID in "${LOADS[@]}"; do

    START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    LOG_FILE="$LOG_DIR/${HPA_ID}_${LOAD_ID}.txt"
    echo "==============================================================" | tee -a "$LOG_CENTRAL"
    echo "[$START_TIME] Inicio del experimento $HPA_ID - $LOAD_ID" | tee -a "$LOG_CENTRAL"
    echo "Inicio: $START_TIME" | tee -a "$LOG_FILE"

    # ---------------------------------------------------------------
    # PASO 1: Desplegar manifiestos en Kubernetes
    # ---------------------------------------------------------------
    echo "[Paso 1] Aplicando manifiestos..." | tee -a "$LOG_FILE"
    kubectl apply -f "$MANIFESTS_DIR/nginx-deployment.yaml" 2>&1 | tee -a "$LOG_FILE"
    kubectl apply -f "$MANIFESTS_DIR/generated/${HPA_ID}_hpa.yaml" 2>&1 | tee -a "$LOG_FILE"
    sleep 20

    # ---------------------------------------------------------------
    # PASO 2: Mostrar IP del clúster (solo en primera ejecución)
    # ---------------------------------------------------------------
    # if [ "$FIRST_RUN" = true ]; then
    #   echo "[Paso 2] IP de los nodos del clúster:" | tee -a "$LOG_FILE"
    #   kubectl get nodes -o wide 2>&1 | tee -a "$LOG_FILE"
    #   echo ""
    #   echo "Edita el archivo:"
    #   echo "    $LOAD_SCRIPT"
    #   echo "y reemplaza la dirección '<IP_DEL_CLUSTER>' por la IP externa de uno de los nodos"
    #   echo "que aparece en la columna 'EXTERNAL-IP' o 'INTERNAL-IP'."
    #   echo ""
    #   read -p "Presiona ENTER para continuar una vez que hayas actualizado la IP..."
    #   FIRST_RUN=false
    # fi

    # ---------------------------------------------------------------
    # PASO 3: Iniciar recolección de métricas y eventos
    # ---------------------------------------------------------------
    echo "[Paso 3] Iniciando recolección de métricas y eventos..." | tee -a "$LOG_FILE"
    bash "$METRIC_SCRIPT" "$HPA_ID" "$LOAD_ID" &
    METRIC_PID=$!
    bash "$EVENTS_SCRIPT" "$HPA_ID" "$LOAD_ID" &
    EVENTS_PID=$!
    sleep 5

    # ---------------------------------------------------------------
    # PASO 4: Ejecutar carga con K6
    # ---------------------------------------------------------------
    echo "[Paso 4] Ejecutando prueba de carga..." | tee -a "$LOG_FILE"
    K6_START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$K6_START_TIME" > "$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_k6_start_time.txt"

    K6_CONF="k6_configs/${LOAD_ID}_config.json"
    k6 run --out csv="$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_k6_results.csv" \
           --summary-export "$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_summary.json" \
           -e K6_CONF="$K6_CONF" \
           "$LOAD_SCRIPT" 2>&1 | tee -a "$LOG_FILE"
    
    # ---------------------------------------------------------------
    # PASO 5: Esperar breve periodo para capturar post-carga
    # ---------------------------------------------------------------
    echo "[Paso 5] Esperando 10 minutos adicionales para observar estabilización..." | tee -a "$LOG_FILE"
    sleep 10m

    # ---------------------------------------------------------------
    # PASO 6: Detener procesos de recolección
    # ---------------------------------------------------------------
    echo "[Paso 6] Deteniendo procesos..." | tee -a "$LOG_FILE"
    kill "$METRIC_PID"
    kill "$EVENTS_PID"

    # ---------------------------------------------------------------
    # PASO 7: Análisis con Docker
    # ---------------------------------------------------------------
    echo "[Paso 7] Ejecutando análisis con Docker..." | tee -a "$LOG_FILE"
    docker build -t nginx-elasticity-analysis "$ANALYSIS_DIR" 2>&1 | tee -a "$LOG_FILE"
    docker run --rm \
      -v "$(pwd)/$OUTPUT_DIR:/app/output" \
      -v "$(pwd)/$ANALYSIS_DIR/images:/app/images" \
      -v "$(pwd)/$K6_CONFIG_DIR:/app/k6_configs" \
      -e HPA_ID="$HPA_ID" \
      -e LOAD_ID="$LOAD_ID" \
      nginx-elasticity-analysis 2>&1 | tee -a "$LOG_FILE"

    # ---------------------------------------------------------------
    # PASO 8: Eliminar recursos de Kubernetes
    # ---------------------------------------------------------------
    echo "[Paso 8] Limpiando recursos de Kubernetes..." | tee -a "$LOG_FILE"
    kubectl delete -f "$MANIFESTS_DIR/nginx-deployment.yaml" 2>&1 | tee -a "$LOG_FILE"
    kubectl delete -f "$MANIFESTS_DIR/generated/${HPA_ID}_hpa.yaml" 2>&1 | tee -a "$LOG_FILE"

    # ---------------------------------------------------------------
    # PASO 9: Organizar archivos del experimento
    # ---------------------------------------------------------------
    echo "[Paso 9] Moviendo archivos a subcarpeta HPA_${HPA_ID}_LOAD_${LOAD_ID}..." | tee -a "$LOG_FILE"
    EXP_OUTPUT_DIR="$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}"
    mkdir -p "$EXP_OUTPUT_DIR"
    mv "$OUTPUT_DIR"/HPA_${HPA_ID}_LOAD_${LOAD_ID}_* "$EXP_OUTPUT_DIR"/

    # ---------------------------------------------------------------
    # FIN DEL EXPERIMENTO
    # ---------------------------------------------------------------
    END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$END_TIME] Fin del experimento $HPA_ID - $LOAD_ID" | tee -a "$LOG_CENTRAL"
    echo "Fin: $END_TIME" | tee -a "$LOG_FILE"

    echo "Esperando 60 segundos antes del siguiente experimento..." | tee -a "$LOG_FILE"
    sleep 60
  done
done

# ---------------------------------------------------------------
# FINALIZACIÓN GENERAL
# ---------------------------------------------------------------
echo "==============================================================" | tee -a "$LOG_CENTRAL"
echo "Fin del experimento: $(date)" | tee -a "$LOG_CENTRAL"
echo "==============================================================" | tee -a "$LOG_CENTRAL"
echo "Todos los experimentos han sido ejecutados satisfactoriamente." | tee -a "$LOG_CENTRAL"
echo "==============================================================" | tee -a "$LOG_CENTRAL"

