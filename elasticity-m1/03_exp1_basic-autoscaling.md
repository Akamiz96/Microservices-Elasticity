# 🚀 Escalamiento Básico con HPA (`exp1_basic-autoscaling`)

Este documento describe el flujo completo del primer experimento de elasticidad, en el cual se evalúa cómo un sistema Kubernetes responde a una carga progresiva utilizando el Horizontal Pod Autoscaler (HPA). 

El experimento simula una aplicación web básica (NGINX) desplegada en un clúster, expuesta a una carga generada por usuarios virtuales mediante k6. El objetivo es observar cómo varía el número de réplicas del microservicio en respuesta al uso de CPU, analizar la relación entre la demanda estimada y la oferta disponible de recursos, y construir curvas de elasticidad que reflejen la capacidad adaptativa del sistema.

Este experimento es el punto de partida para analizar el comportamiento de escalado horizontal automático bajo condiciones controladas, utilizando configuraciones mínimas para facilitar la observación y análisis del sistema.

---

## 🎯 Objetivo

El propósito de este experimento es analizar el comportamiento de un sistema Kubernetes que implementa escalamiento automático horizontal (Horizontal Pod Autoscaler - HPA) bajo una carga progresiva y controlada. A través de este proceso se busca:

- Observar la dinámica de escalado del sistema en respuesta a cambios en el uso de CPU.
- Registrar eventos clave de escalamiento (`scaleup` y `scaledown`) generados por el HPA.
- Estimar la demanda teórica de CPU en función de la carga generada (usuarios virtuales o requests).
- Calcular la oferta efectiva de CPU proporcionada por los pods activos durante la prueba.
- Construir curvas de elasticidad que permitan comparar demanda y oferta de recursos a lo largo del tiempo.
- Identificar posibles situaciones de subaprovisionamiento o sobreaprovisionamiento.
- **Calcular métricas cuantitativas de elasticidad**, tales como:
  - Precisión promedio del escalado hacia arriba y hacia abajo.
  - Tiempos acumulados y promedios en estados de sub/sobreaprovisionamiento.
  - Recursos promedio utilizados o desperdiciados en dichos estados.
  - Elasticidad total del sistema, considerando tanto capacidad como tiempo de respuesta.

Este análisis permite evaluar qué tan efectiva es la configuración básica del HPA para responder a fluctuaciones de carga y qué tan bien se adapta la infraestructura a la demanda.

---

## 🧩 Arquitectura del experimento

Este experimento se ejecuta en un entorno Kubernetes, donde se despliegan los siguientes componentes:

- **Microservicio (NGINX)**: Servicio simulado que actúa como blanco de la carga. Se usa una imagen ligera de NGINX configurada con límites y solicitudes (`requests`) de CPU definidos para permitir que el HPA actúe correctamente.

- **Horizontal Pod Autoscaler (HPA)**: Controlador nativo de Kubernetes que monitorea el uso promedio de CPU de los pods en ejecución y ajusta automáticamente el número de réplicas para mantener el uso cerca de un objetivo configurado. En este experimento, el objetivo es del 25%.

- **Generador de carga (k6)**: Herramienta de pruebas de carga que simula usuarios virtuales (VUs) generando solicitudes HTTP al microservicio durante un periodo de tiempo. La carga se define en etapas para observar cómo responde el sistema a incrementos y reducciones.

- **Recolectores de datos (scripts Bash)**: Capturan métricas relevantes durante la ejecución del experimento:
  - Uso de CPU por pod.
  - Número de réplicas activas.
  - Eventos de escalamiento registrados por Kubernetes.

- **Módulo de análisis (scripts Python + contenedor Docker)**: Procesa los datos recolectados, sincroniza eventos y métricas, y genera gráficos y métricas de elasticidad.

### Diagrama de interacción

```
       +------------------+
       | Generador de     |
       | carga (k6)       |
       +--------+---------+
                |
                v
       +--------+---------+
       | Microservicio    |
       | (NGINX)          |
       +--------+---------+
                |
                v
       +--------+---------+
       | Pods del         |
       | Deployment       |
       +--------+---------+
                |
       (Reportan uso de CPU)
                |
                v
       +------------------+
       | Autoscaler (HPA) |
       | Target: 25% CPU  |
       +--------+---------+
                |
       (Escala número de pods)
                |
                v
       +------------------------+
       | Registro de eventos   |
       | (Kubernetes Event Log)|
       +--------+--------------+
                |
                v
       +------------------------+
       | Recolectores de datos |
       | y scripts de análisis |
       +------------------------+
```

Este diseño modular permite ejecutar y analizar el experimento de forma automatizada, controlada y reproducible.

## 🧪 Flujo del experimento paso a paso

A continuación se describe el proceso completo que ocurre durante la ejecución del experimento, desde el despliegue hasta la generación de resultados. Cada paso representa una acción concreta del sistema o de los scripts que forman parte de la infraestructura experimental.

| Paso | Descripción técnica |
|------|---------------------|
| 1️⃣   | **Despliegue del microservicio y del HPA**: Se aplican los manifiestos YAML (`deployment.yaml` y `hpa.yaml`) que crean el Deployment de NGINX con sus límites de CPU y el HPA con su objetivo de 25% de utilización promedio. |
| 2️⃣   | **Inicialización de recolectores de datos**: Se ejecutan en segundo plano dos scripts Bash: uno para capturar métricas periódicas de uso de CPU y número de pods (`metric_collector_basic.sh`), y otro para registrar eventos de escalamiento desde el clúster (`capture_deployment_events.sh`). |
| 3️⃣   | **Ejecución de la carga con k6**: Se lanza el script de prueba (`basic_autoscaling_test.js`) que genera carga HTTP con diferentes niveles de usuarios virtuales (VUs) durante una ventana de tiempo de 7 minutos, provocando variaciones en el uso de CPU. |
| 4️⃣   | **Monitoreo del comportamiento del HPA**: Kubernetes recolecta las métricas de CPU de los pods y el HPA toma decisiones de escalamiento, aumentando o reduciendo réplicas para mantener la utilización cercana al 25%. Estas decisiones quedan registradas como eventos. |
| 5️⃣   | **Finalización y recolección de datos**: Una vez terminada la carga, los recolectores se detienen y todos los datos se consolidan en archivos CSV y JSON en la carpeta `output/`. |
| 6️⃣   | **Procesamiento y análisis**: Se ejecutan scripts Python desde un contenedor Docker que procesan las métricas, sincronizan los eventos con los datos de CPU, generan los gráficos de comportamiento y calculan las métricas de elasticidad. |

Este flujo es ejecutado manualmente o de forma automática mediante el script `exp1_basic-autoscaling.sh`, lo que permite replicar el experimento de forma consistente.

---

## 📦 Archivos y configuraciones

El experimento se apoya en varios archivos clave organizados en carpetas específicas. Cada uno cumple un rol dentro del proceso de despliegue, recolección de datos, generación de carga y análisis.

### 🗂️ `manifests/` - Manifiestos de Kubernetes

- `deployment.yaml`: Define el Deployment de NGINX, especificando la imagen utilizada, el número inicial de réplicas, los `resource requests` y `limits` de CPU, así como los probes necesarios.
- `hpa.yaml`: Contiene la configuración del Horizontal Pod Autoscaler (HPA), con un objetivo de utilización promedio de CPU del 25%, y un rango de réplicas entre 1 y 10.

### 🗂️ `scripts/` - Generación de carga y captura de datos

- `basic_autoscaling_test.js`: Script de k6 que define un escenario de carga dividido en etapas. Simula la actividad de usuarios virtuales con un patrón escalonado: subida, carga sostenida, bajada y finalización.
- `capture_deployment_events.sh`: Ejecuta un ciclo periódico para registrar eventos del tipo `ScalingReplicaSet` generados por el HPA. Estos eventos permiten identificar cuándo y cuántas réplicas fueron añadidas o eliminadas.
- `metric_collector_basic.sh`: Utiliza `kubectl top pods` y `kubectl get deployment` para recolectar el uso de CPU por pod y el número de réplicas activas, generando un log cada 10 segundos.

### 🔧 Carga generada (en `basic_autoscaling_test.js`)

La carga simulada se define por etapas en el script de k6. Cada etapa especifica cuántos usuarios virtuales (VUs) estarán activos y por cuánto tiempo:

```js
stages: [
  { duration: '1m', target: 50 },   // Subida progresiva de carga
  { duration: '3m', target: 150 },  // Carga alta sostenida (debería activar el HPA)
  { duration: '2m', target: 50 },   // Reducción progresiva
  { duration: '1m', target: 0 },    // Descenso total de la carga
]
```

### 🗂️ `analysis/` - Análisis de datos y visualización (ubicado en `files/basic-autoscaling/analysis/`)

Esta carpeta contiene los scripts de Python encargados del procesamiento de los datos crudos recolectados durante el experimento. También incluye herramientas para graficar la evolución del sistema y calcular métricas de elasticidad.

#### Scripts principales:

- `filter_scaling_events.py`: Filtra los eventos de escalamiento del archivo crudo (`scaling_events.csv`) y los sincroniza temporalmente con el inicio de la carga, generando una versión limpia (`scaling_events_clean.csv`).

- `plot_cpu_usage.py`: Genera gráficos del uso de CPU por pod a lo largo del tiempo. Útil para observar carga distribuida entre réplicas.

- `plot_cpu_usage_with_events.py`: Variante del anterior que incluye líneas verticales que marcan los momentos de escalamiento (`scaleup`, `scaledown`).

- `plot_pod_count.py`: Grafica la evolución del número de réplicas activas del microservicio durante el experimento.

- `plot_pod_count_with_events.py`: Incluye eventos de escalamiento en la gráfica anterior.

- `plot_elasticity_curve.py`: Construye la curva de elasticidad comparando la demanda estimada de CPU (por VUs o requests) con la oferta disponible basada en el número de pods.

- `plot_elasticity_curve_with_events.py`: Variante con anotaciones de eventos de escalamiento para enriquecer el análisis visual.

- `calculate_elasticity_metrics.py`: Calcula un conjunto completo de métricas de elasticidad, incluyendo precisión de escalamiento, tiempos y recursos en estados de sub/sobreaprovisionamiento, y elasticidad global.

- `plot_indirect_elasticity_metrics.py`: Visualiza métricas de elasticidad complementarias para facilitar su interpretación.

#### Archivos auxiliares:

- `Dockerfile`: Define el entorno reproducible para ejecutar los scripts de análisis desde un contenedor. Incluye todas las dependencias necesarias.

- `requirements.txt`: Lista de paquetes de Python requeridos (pandas, matplotlib, etc.) para ejecutar los scripts sin errores.

- `images/`: Carpeta donde se guardan automáticamente todos los gráficos generados por los scripts.

> 📂 Todos estos archivos están ubicados en:  
> `files/basic-autoscaling/analysis/`  
> y el presente documento Markdown se encuentra en la raíz de `files/basic-autoscaling/`.

---

## 🔁 Requisito previo: ejecutar el microbenchmark

Antes de ejecutar este experimento de autoscaling, es necesario obtener una estimación precisa del consumo de CPU por usuario virtual (VU) o por request. Para ello, se debe realizar primero el experimento descrito en el archivo [`02_exp0_microbenchmark.md`](./02_exp0_microbenchmark.md).

Dicho experimento proporciona los valores de referencia necesarios para estimar la demanda teórica de CPU a partir de la carga generada. Estos valores deben ser actualizados manualmente en los scripts de análisis que construyen las curvas de elasticidad y calculan las métricas.

### 📌 Variables a definir (extraídas del microbenchmark):

```python
# ==============================================================================
# IMPORTANTE: AJUSTAR SEGÚN MICROBENCHMARK
# ==============================================================================
cpu_per_vu = 1.50    # millicores por VU
cpu_per_req = 0.05   # millicores por request
requests_per_vu_per_second = 1  # Asumido por diseño del benchmark (1 request/seg por VU)
```

Estas variables permiten traducir la carga generada (VUs o requests por segundo) en demanda estimada de CPU (millicores), que luego se compara con la oferta disponible para construir las curvas de elasticidad.

### 🛠️ Archivos donde deben ser modificadas:

- `analysis/calculate_elasticity_metrics.py`
- `analysis/plot_elasticity_curve.py`
- `analysis/plot_elasticity_curve_with_events.py`

> ⚠️ Si no se actualizan estos valores, los resultados obtenidos del análisis de elasticidad serán inconsistentes con la carga real aplicada al sistema.


---

## 📊 Resultados obtenidos

El análisis posterior al experimento produce una serie de salidas en formato gráfico y archivos de texto que resumen el comportamiento del sistema, la respuesta del HPA, y la calidad del escalamiento.

### 📈 Gráficos generados

Los gráficos se encuentran organizados en subcarpetas dentro de `analysis/images/` según el tipo de información visualizada:

#### 🧠 Uso de CPU por pod (`analysis/images/cpu_pod/`)
- `cpu_usage_per_pod.png`: Uso de CPU de todos los pods a lo largo del tiempo.
- `cpu_usage_per_pod_with_events.png`: Igual al anterior, pero incluye líneas verticales que indican eventos de escalamiento.
- `podX_cpu.png`: Uso de CPU individual por pod (siendo X el número del pod correspondiente).
- `podX_cpu_with_events.png`: Versión con eventos (siendo X el número del pod correspondiente).

#### 🔢 Conteo de pods (`analysis/images/pod_count/`)
- `pod_count_over_time.png`: Evolución del número de réplicas durante la prueba.
- `pod_count_over_time_with_events.png`: Incluye momentos de escalamiento.

#### ⚖️ Curvas de elasticidad (`analysis/images/elasticity/`)
- `elasticity_curve_vu.png`: Comparación entre demanda estimada (por VU) y oferta de CPU.
- `elasticity_curve_vus_with_events.png`: Versión con eventos.
- `elasticity_curve_req.png`: Curva basada en estimación por número de requests.
- `elasticity_curve_reqs_with_events.png`: Versión con eventos.

#### 📉 Métricas indirectas (`analysis/images/indirect_metrics/`)
- `latency_avg.png`, `latency_avg_events.png`: Latencia promedio.
- `throughput.png`, `throughput_events.png`: Rendimiento total (requests por segundo).
- `throughput_vs_vus.png`: Relación entre carga y throughput.
- `http_errors.png`, `http_errors_events.png`: Errores HTTP detectados.

### 📄 Archivos de salida (en `output/`)

Estos archivos contienen los datos crudos y procesados del experimento:

- `basic_metrics.csv`: Métricas de CPU y réplicas recolectadas durante la prueba.
- `scaling_events.csv`: Eventos de escalamiento sin procesar.
- `scaling_events_clean.csv`: Eventos sincronizados con el inicio del test.
- `k6_summary.json`: Resumen de la ejecución de carga desde k6.
- `k6_results.csv`: Resultados detallados por segundo desde k6.
- `k6_start_time.txt`: Marca de tiempo del inicio de la carga.
- `elasticity_metrics_vus.txt`: Métricas de elasticidad (por VU), incluyendo precisión, tiempos de sub/sobreaprovisionamiento y recursos usados/desperdiciados.
- `elasticity_metrics_requests.txt`: Misma información, calculada en función de la demanda por número de requests.

La interpretación combinada de estas métricas y gráficos permite tener una visión detallada de la eficiencia y elasticidad del sistema bajo la configuración básica del HPA.

---

## 🧪 Ejecución y automatización del proceso

Este experimento puede ejecutarse manualmente paso a paso o de forma automatizada mediante un script Bash. A continuación se describe cada enfoque.

---

### 🧾 Ejecución manual paso a paso

Para ejecutar el experimento manualmente, se deben realizar las siguientes acciones desde la raíz del proyecto (`elasticity-m1`):

1. **Aplicar los manifiestos de Kubernetes**:

```bash
kubectl apply -f basic-autoscaling/manifests/nginx-deployment.yaml
kubectl apply -f basic-autoscaling/manifests/hpa.yaml
```

2. **Esperar que los pods estén listos**, y obtener la IP del nodo para configurar la prueba:

```bash
kubectl get nodes -o wide
```

3. **Editar el script de carga** para reemplazar `<IP_DEL_CLUSTER>` por la IP del nodo en:
```
basic-autoscaling/scripts/basic_load_test.js
```

4. **Iniciar los recolectores en segundo plano**:

```bash
bash basic-autoscaling/scripts/metric_collector_basic.sh &
METRIC_PID=$!
bash basic-autoscaling/scripts/capture_deployment_events.sh &
EVENTS_PID=$!
```

5. **Ejecutar la prueba de carga con k6**:

```bash
k6 run --out csv=basic-autoscaling/output/k6_results.csv \
       --summary-export=basic-autoscaling/output/k6_summary.json \
       basic-autoscaling/scripts/basic_load_test.js
```

6. **Esperar unos segundos adicionales** tras la prueba:

```bash
sleep 30
```

7. **Detener los recolectores**:

```bash
kill $METRIC_PID
kill $EVENTS_PID
```

8. **Ejecutar análisis desde Docker**:

```bash
docker build -t basic-autoscaling-analysis basic-autoscaling/analysis
docker run --rm \
  -v "$(pwd)/basic-autoscaling/output:/app/output" \
  -v "$(pwd)/basic-autoscaling/analysis/images:/app/images" \
  basic-autoscaling-analysis
```

9. **Eliminar recursos de Kubernetes**:

```bash
kubectl delete -f basic-autoscaling/manifests/nginx-deployment.yaml
kubectl delete -f basic-autoscaling/manifests/hpa.yaml
```

---

### 🤖 Ejecución automatizada con `exp1_basic-autoscaling.sh`

Todo el flujo anterior ha sido automatizado mediante el script:

```
exp1_basic-autoscaling.sh
```

Este script ejecuta cada uno de los pasos en orden, incluyendo despliegue, recolección de datos, ejecución de carga, análisis y limpieza de recursos.

> 📂 El script se encuentra en la raíz del proyecto:  
> `elasticity-m1/exp1_basic-autoscaling.sh`

#### ▶️ Modo de ejecución:

```bash
bash exp1_basic-autoscaling.sh
```

> ⚠️ **Importante**: el script debe ejecutarse desde la raíz del repositorio (`elasticity-m1`) para que las rutas relativas funcionen correctamente.

#### 🔍 Acciones que realiza automáticamente:

1. Aplica los manifiestos de Kubernetes.
2. Muestra la IP del clúster y solicita al usuario editar la IP en el archivo `basic_load_test.js`.
3. Inicia los recolectores de métricas y eventos.
4. Ejecuta la prueba de carga con k6.
5. Espera un breve periodo tras la carga.
6. Detiene los procesos de recolección.
7. Ejecuta el análisis desde Docker.
8. Elimina los recursos desplegados en el clúster.

Este enfoque garantiza reproducibilidad, automatización y una mínima intervención manual.



