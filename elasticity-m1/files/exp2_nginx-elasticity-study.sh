# ------------------------------------------------------------------------------
# ARCHIVO: run_all_experiments.sh
# DESCRIPCIÓN: Automatiza la ejecución de todos los experimentos combinando
#              configuraciones de HPA (C1-C9) y patrones de carga (L01-L06).
#              Para cada combinación se despliegan los recursos, se recolectan
#              métricas, se lanza la carga y se ejecuta el análisis.
#              Se mantiene un log central y logs individuales por combinación.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 15 de abril de 2025
# CONTEXTO:
#   - Forma parte del estudio de elasticidad con NGINX en Kubernetes.
# ------------------------------------------------------------------------------

# ---------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE RUTAS
# ---------------------------------------------------------------
BASE_DIR="nginx-elasticity-study"
MANIFESTS_DIR="$BASE_DIR/manifests"
SCRIPTS_DIR="$BASE_DIR/scripts"
OUTPUT_DIR="$BASE_DIR/output"
ANALYSIS_DIR="$BASE_DIR/analysis"
LOG_DIR="exp_logs/nginx-elasticity-study"

METRIC_SCRIPT="$SCRIPTS_DIR/metric_collector_basic.sh"
EVENTS_SCRIPT="$SCRIPTS_DIR/capture_deployment_events.sh"
LOAD_SCRIPT="$SCRIPTS_DIR/load_test_runner.js"
K6_CONFIG_DIR="$SCRIPTS_DIR/k6_configs"

mkdir -p "$LOG_DIR"
LOG_CENTRAL="$LOG_DIR/experiment_log.txt"
echo "Inicio del experimento: $(date)" >> "$LOG_CENTRAL"

# ---------------------------------------------------------------
# LISTA DE CONFIGURACIONES A PROBAR
# ---------------------------------------------------------------
HPAS=(C1)
LOADS=(L01)

# ---------------------------------------------------------------
# BUCLE PRINCIPAL SOBRE TODAS LAS COMBINACIONES
# ---------------------------------------------------------------
FIRST_RUN=true

for HPA_ID in "${HPAS[@]}"; do
  for LOAD_ID in "${LOADS[@]}"; do
    echo "==============================================================="
    echo "Ejecutando experimento HPA: $HPA_ID | Carga: $LOAD_ID"
    echo "==============================================================="

    START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    LOG_FILE="$LOG_DIR/${HPA_ID}_${LOAD_ID}.log"
    echo "[$START_TIME] Inicio del experimento $HPA_ID - $LOAD_ID" >> "$LOG_CENTRAL"
    echo "Inicio: $START_TIME" > "$LOG_FILE"

    # ---------------------------------------------------------------
    # PASO 1: Desplegar manifiestos en Kubernetes
    # ---------------------------------------------------------------
    kubectl apply -f "$MANIFESTS_DIR/nginx-deployment.yaml" >> "$LOG_FILE" 2>&1
    kubectl apply -f "$MANIFESTS_DIR/generated/${HPA_ID}_hpa.yaml" >> "$LOG_FILE" 2>&1
    echo "[Paso 1] Manifiestos aplicados" >> "$LOG_FILE"

    echo "Esperando 20 segundos para que los pods inicien..."
    sleep 20

    # ---------------------------------------------------------------
    # PASO 2: Mostrar IP de nodos (solo en la primera ejecución)
    # ---------------------------------------------------------------
    if [ "$FIRST_RUN" = true ]; then
      echo "[Paso 2] IP de nodos del clúster:" >> "$LOG_FILE"
      kubectl get nodes -o wide >> "$LOG_FILE" 2>&1

      echo ""
      echo "Edita el archivo:"
      echo "    $LOAD_SCRIPT"
      echo "y reemplaza la dirección '<IP_DEL_CLUSTER>' por la IP externa de uno de los nodos"
      echo "que aparece en la columna 'EXTERNAL-IP' o 'INTERNAL-IP' del resultado anterior."
      echo ""
      read -p "Presiona ENTER para continuar una vez que hayas actualizado la IP..."

      FIRST_RUN=false
    fi

    # ---------------------------------------------------------------
    # PASO 3: Iniciar recolección de métricas y eventos en segundo plano
    # ---------------------------------------------------------------

    # Recolector de métricas
    bash "$METRIC_SCRIPT" "$HPA_ID" "$LOAD_ID" &
    METRIC_PID=$!
    echo "[Info] Recolector de métricas iniciado con PID $METRIC_PID" >> "$LOG_FILE"

    # Captura de eventos
    bash "$EVENTS_SCRIPT" "$HPA_ID" "$LOAD_ID" &
    EVENTS_PID=$!
    echo "[Info] Captura de eventos iniciada con PID $EVENTS_PID" >> "$LOG_FILE"

    echo "[Paso 3] Recolectores iniciados. Esperando 5 segundos..." >> "$LOG_FILE"
    sleep 5

    # ---------------------------------------------------------------
    # PASO 4: Ejecutar prueba de carga con k6
    # ---------------------------------------------------------------
    K6_START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$K6_START_TIME" > "$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_k6_start_time.txt"

    K6_CONF="$K6_CONFIG_DIR/${LOAD_ID}_config.json"
    k6 run --out csv="$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_results.csv" \
           --summary-export "$OUTPUT_DIR/HPA_${HPA_ID}_LOAD_${LOAD_ID}_summary.json" \
           -e K6_CONF="$K6_CONF" \
           "$LOAD_SCRIPT" >> "$LOG_FILE" 2>&1

    echo "[Paso 4] Carga ejecutada. Esperando 30s post-carga..." >> "$LOG_FILE"
    sleep 30

    # ---------------------------------------------------------------
    # PASO 5: Detener procesos de recolección
    # ---------------------------------------------------------------
    kill "$METRIC_PID"
    kill "$EVENTS_PID"
    echo "[Paso 5] Recolectores detenidos" >> "$LOG_FILE"

    # ---------------------------------------------------------------
    # PASO 6: Ejecutar análisis automático con Docker
    # ---------------------------------------------------------------
    docker build -t nginx-elasticity-analysis "$ANALYSIS_DIR" >> "$LOG_FILE" 2>&1
    docker run --rm \
      -v "$(pwd)/$OUTPUT_DIR:/app/output" \
      -v "$(pwd)/$ANALYSIS_DIR/images:/app/images" \
      -v "$(pwd)/$K6_CONFIG_DIR:/app/k6_configs" \
      -e HPA_ID="$HPA_ID" \
      -e LOAD_ID="$LOAD_ID" \
      nginx-elasticity-analysis >> "$LOG_FILE" 2>&1

    echo "[Paso 6] Análisis completado" >> "$LOG_FILE"

    # ---------------------------------------------------------------
    # PASO 7: Eliminar recursos de Kubernetes
    # ---------------------------------------------------------------
    kubectl delete -f "$MANIFESTS_DIR/nginx-deployment.yaml" >> "$LOG_FILE" 2>&1
    kubectl delete -f "$MANIFESTS_DIR/${HPA_ID}_hpa.yaml" >> "$LOG_FILE" 2>&1
    echo "[Paso 7] Recursos eliminados" >> "$LOG_FILE"

    END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$END_TIME] Fin del experimento $HPA_ID - $LOAD_ID" >> "$LOG_CENTRAL"
    echo "Fin: $END_TIME" >> "$LOG_FILE"

    echo "Esperando 30 segundos antes del siguiente experimento..."
    sleep 30
  done
done

# ---------------------------------------------------------------
# FINALIZACIÓN
# ---------------------------------------------------------------
echo "Fin del experimento: $(date)" >> "$LOG_CENTRAL"
echo "Todos los experimentos han sido ejecutados satisfactoriamente."
