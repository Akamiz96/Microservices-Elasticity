# 🚀 03 - Escalamiento Básico con HPA (`exp1_basic-autoscaling`)

Este documento describe el primer experimento de elasticidad, en el que se evalúa el comportamiento de escalamiento automático de un microservicio bajo una configuración básica de Horizontal Pod Autoscaler (HPA). Se busca observar la respuesta del sistema ante una carga creciente, estimar la demanda de recursos y compararla con la oferta para generar la gráfica de elasticidad.

---

## 🌟 Objetivo del experimento

- Observar cómo responde el sistema ante una carga progresiva.
- Registrar y visualizar los eventos de escalamiento (`scaleup`, `scaledown`).
- Estimar:
  - Demanda total de CPU (en millicores).
  - Oferta de CPU disponible según número de réplicas activas.
- Usar estos datos para construir la gráfica de elasticidad del sistema.

---

## ⚙️ Arquitectura del experimento

- **Microservicio**: NGINX (mismo usado en el microbenchmark)
- **Cluster**: Kubernetes local
- **Autoscaler**: HPA con target de CPU = 25%
- **Generador de carga**: k6
- **Duración**: 7 minutos de carga variada

> 🔁 **Requisito previo:** Ejecutar el microbenchmark para obtener las estimaciones de CPU por VU. Los valores resultantes deben actualizarse manualmente en los scripts:
>
> - `plot_elasticity_cpu.py`
> - `plot_elasticity_curve_with_events.py`
>
> Dentro de estos archivos se encuentra la siguiente sección:
> ```python
> # ==============================================================================
> # IMPORTANTE: AJUSTAR SEGÚN MICROBENCHMARK
> # ==============================================================================
> cpu_per_vu = 1.50    # millicores por VU
> cpu_per_req = 0.05   # millicores por request
> requests_per_vu_per_second = 1  # Asumido por diseño del benchmark (1 request/seg por VU)
> ```

---

## ♻️ Flujo del experimento

| Paso | Descripción |
|------|-------------|
| 1. | Despliegue de NGINX y HPA en Kubernetes |
| 2. | Iniciación del recolector de métricas y eventos |
| 3. | Ejecución de la prueba de carga (`basic_autoscaling_test.js`) |
| 4. | Recolección de métricas de CPU y número de pods |
| 5. | Análisis de demanda vs. oferta con scripts en Python |

---

## 📦 Configuraciones utilizadas

### Manifiestos Kubernetes (`manifests/`):
- `deployment.yaml`: despliegue de NGINX con CPU requests/limits definidos.
- `hpa.yaml`: HPA con objetivo de CPU al 25% y entre 1-10 réplicas.

### Scripts (`scripts/`):
- `basic_autoscaling_test.js`: genera carga con picos y descensos progresivos.
- `capture_deployment_events.sh`: captura los eventos de escalamiento del deployment.
- `metric_collector_basic.sh`: recolecta métricas de CPU y número de pods.

### Carga generada con:
```js
stages: [
  { duration: '1m', target: 50 },   // Subida progresiva de carga
  { duration: '3m', target: 150 },  // Carga alta sostenida (debería activar el HPA)
  { duration: '2m', target: 50 },   // Reducción progresiva
  { duration: '1m', target: 0 },    // Descenso total de la carga
]
```

---

## 🔍 Análisis realizado

### Estimación de demanda
```python
cpu_per_vu = 1.5  # millicores por VU (ajustar según resultado del microbenchmark)
estimated_demand = vus * cpu_per_vu
```

### Estimación de oferta
```python
offer = replicas * 100  # 100m = CPU request por pod
```

---

## 📊 Resultados obtenidos

### Gráficos generados:
- `cpu_usage_per_pod.png`: Uso de CPU por pod durante la prueba.
- `cpu_usage_per_pod_with_events.png`: Uso de CPU con eventos de escalamiento.
- `pod_count_over_time.png`: Evolución del número de pods.
- `pod_count_over_time_with_events.png`: Evolución de pods con eventos.
- `elasticity_curve.png`: Comparación demanda vs. oferta.
- `elasticity_curve_with_events.png`: Curva de elasticidad con eventos.

---

## 📁 Estructura del experimento

```
files/basic-autoscaling/
├── manifests/                        # YAMLs de Kubernetes (deployment, HPA)
│   ├── deployment.yaml
│   └── hpa.yaml
├── scripts/                          # Scripts ejecutables del experimento
│   ├── basic_autoscaling_test.js     # Script k6 para generar la carga
│   ├── capture_deployment_events.sh  # Captura eventos de escalamiento
│   └── metric_collector_basic.sh     # Recolector de métricas de CPU y pods
├── output/                           # Resultados crudos del experimento
│   ├── basic_metrics.csv             # Métricas CPU y réplicas
│   ├── k6_summary.json               # Resumen de carga generada por k6
│   ├── k6_start_time.txt             # Timestamp de inicio de carga
│   ├── scaling_events.csv            # Eventos crudos del deployment
│   └── scaling_events_clean.csv      # Eventos filtrados y sincronizados
├── analysis/                         # Scripts y visualizaciones
│   ├── Dockerfile                    # Contenedor para reproducir análisis
│   ├── filter_scaling_events.py      # Limpieza y sincronización de eventos
│   ├── plot_cpu_usage.py             # Gráfico de CPU por pod
│   ├── plot_cpu_usage_with_events.py # CPU con eventos
│   ├── plot_pod_count.py             # Evolución de réplicas
│   ├── plot_pod_count_with_events.py # Réplicas con eventos
│   ├── plot_elasticity_curve.py      # Gráfica de demanda vs. oferta
│   ├── plot_elasticity_curve_with_events.py # Versión con eventos
│   ├── requirements.txt              # Dependencias del análisis
│   └── images/                       # Gráficos generados
│       ├── cpu_usage_per_pod.png
│       ├── cpu_usage_per_pod_with_events.png
│       ├── pod_count_over_time.png
│       ├── pod_count_over_time_with_events.png
│       ├── elasticity_curve.png
│       ├── elasticity_curve_with_events.png
│       └── cpu_pod/                  # Gráficos individuales por pod
│           ├── pod1_cpu.png
│           ├── pod1_cpu_with_events.png
│           ├── pod2_cpu.png
│           └── pod2_cpu_with_events.png
```

---

## 🧾 Salidas del experimento

✅ **[Completado]** El experimento básico de elasticidad ha finalizado exitosamente.

**Archivos generados:**
- Métricas del sistema: `basic-autoscaling/output/basic_metrics.csv`
- Resumen de carga (k6): `basic-autoscaling/output/k6_summary.json`
- Timestamp de inicio k6: `basic-autoscaling/output/k6_start_time.txt`
- Eventos del deployment: `basic-autoscaling/output/scaling_events.csv`
- Eventos limpios: `basic-autoscaling/output/scaling_events_clean.csv`

**Imágenes generadas:**
- CPU por pod: `analysis/images/cpu_usage_per_pod.png`
- CPU por pod + eventos: `analysis/images/cpu_usage_per_pod_with_events.png`
- Evolución de pods: `analysis/images/pod_count_over_time.png`
- Pods + eventos: `analysis/images/pod_count_over_time_with_events.png`
- Elasticidad: `analysis/images/elasticity_curve.png`
- Elasticidad + eventos: `analysis/images/elasticity_curve_with_events.png`
- Por pod (individual): `analysis/images/cpu_pod/*.png`

---

## 🤖 Automatización del proceso

El flujo completo del experimento puede ejecutarse automáticamente mediante el script `exp1_basic-autoscaling.sh`, ubicado en la raíz del proyecto.

### 📍 Ubicación
```
files/exp1_basic-autoscaling.sh
```

### ▶️ Ejecución
Este script debe ejecutarse desde la raíz del proyecto:
```bash
bash exp1_basic-autoscaling.sh
```

### 🔄 Qué realiza automáticamente

1. Aplica los manifiestos en Kubernetes:
```bash
kubectl apply -f basic-autoscaling/manifests/deployment.yaml
kubectl apply -f basic-autoscaling/manifests/hpa.yaml
```

2. Solicita al usuario actualizar la IP del clúster en el script de k6.

3. Lanza el recolector de métricas y la captura de eventos en segundo plano:
```bash
bash basic-autoscaling/scripts/metric_collector_basic.sh &
bash basic-autoscaling/scripts/capture_deployment_events.sh &
```

4. Ejecuta la prueba con k6 y exporta el resumen:
```bash
k6 run --summary-export basic-autoscaling/output/k6_summary.json \
  basic-autoscaling/scripts/basic_autoscaling_test.js
```

5. Espera 30 segundos y luego detiene los recolectores:
```bash
kill $METRIC_PID
kill $EVENTS_PID
```

6. Construye y ejecuta el contenedor de análisis:
```bash
docker build -t basic-autoscaling-analysis basic-autoscaling/analysis

docker run --rm \
  -v "$(pwd)/basic-autoscaling/output:/app/output" \
  -v "$(pwd)/basic-autoscaling/analysis/files:/app/files" \
  -v "$(pwd)/basic-autoscaling/analysis/images:/app/images" \
  basic-autoscaling-analysis
```

7. Limpia los recursos de Kubernetes:
```bash
kubectl delete -f basic-autoscaling/manifests/deployment.yaml
kubectl delete -f basic-autoscaling/manifests/hpa.yaml
```

Este enfoque garantiza reproducibilidad, facilita la recolección de datos y reduce errores humanos durante la ejecución del experimento. y minimiza errores humanos al ejecutar el experimento completo de elasticidad.

