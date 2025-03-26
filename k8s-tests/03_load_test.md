## 🚀 Proceso de Ejecución de la Prueba de Carga

Este documento describe de forma detallada el proceso utilizado para diseñar, ejecutar y monitorear un experimento de prueba de carga, cuyo objetivo es observar el comportamiento de escalabilidad horizontal en un despliegue de **NGINX** utilizando el escalador automático de pods (**HPA**) en **Kubernetes**.

---

## 🎯 1. Objetivo del Experimento

El propósito principal de este experimento es evaluar la capacidad de Kubernetes para escalar automáticamente el número de pods en función del uso de CPU, mediante la implementación de un **Horizontal Pod Autoscaler (HPA)**.

### Objetivos Específicos
- 📈 Generar una carga progresiva que aumente y disminuya con el tiempo.
- 📊 Observar cómo el número de pods del despliegue se ajusta automáticamente.
- 📥 Recolectar métricas relevantes de uso de recursos (CPU y memoria).
- 👁 Visualizar el comportamiento del sistema antes, durante y después de la carga.

---

## 🧱 2. Estructura del Entorno

El experimento está completamente contenido en la carpeta `load_test/`, ubicada dentro de `files/`.

```
load_test/
├── manifests/       # Archivos YAML del despliegue y HPA
├── scripts/         # Scripts de carga y recolección de métricas
├── output/          # Archivo CSV con las métricas
└── analysis/        # Scripts de análisis y visualización en Python
```

---

## ⚙️ 3. Configuración de Kubernetes

Los recursos se configuran mediante archivos YAML ubicados en `load_test/manifests/`.

### 3.1 📄 Despliegue de NGINX (`nginx-deployment.yaml`)

Este archivo define los objetos necesarios para desplegar NGINX y exponerlo al exterior mediante un servicio:

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-test
  template:
    metadata:
      labels:
        app: nginx-test
    spec:
      containers:
      - name: nginx
        image: nginx:1.25.3
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

📝 **Explicación de secciones clave:**
- `replicas`: comienza con 1 pod. Este valor será controlado luego por el HPA.
- `selector.matchLabels`: define cómo Kubernetes empareja los pods con el deployment.
- `template.metadata.labels`: asigna etiquetas necesarias para que el Service y el HPA encuentren los pods.
- `image`: define la versión de la imagen de NGINX utilizada.
- `resources.requests`: reserva mínima de recursos para el contenedor. Es fundamental para que el HPA pueda calcular la utilización.
- `resources.limits`: establece los límites máximos que el contenedor puede consumir.

#### Service
```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort
  selector:
    app: nginx-test
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

📝 **Explicación de secciones clave:**
- `type: NodePort`: expone el servicio a través de un puerto accesible desde fuera del clúster.
- `selector`: se conecta a los pods etiquetados como `app: nginx-test`.
- `port`: define el puerto del servicio dentro del clúster.
- `targetPort`: puerto donde el contenedor escucha (coincide con `containerPort`).
- `nodePort`: expone el servicio en el nodo físico (en este caso, el puerto 30080).

📌 **Diagrama Resumen de Componentes**

```
[Usuarios] ⇨ [NodePort Service:30080] ⇨ [Pods NGINX (Deployment)] ⇨ [Monitoreo HPA ⇨ CPU]
```

### 3.2 📄 Escalador Automático de Pods (`hpa.yaml`)

Este archivo configura un `HorizontalPodAutoscaler` que controla dinámicamente la cantidad de réplicas del deployment `nginx-test` según el uso de CPU.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-test
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 25
```

📝 **Explicación de secciones clave:**
- `scaleTargetRef`: especifica el Deployment que será monitoreado y escalado por el HPA.
- `minReplicas` y `maxReplicas`: indican el rango de pods que puede existir en cualquier momento.
- `metrics.resource`: define que la métrica a monitorear es el uso de CPU.
- `averageUtilization`: umbral objetivo de utilización promedio de CPU (en porcentaje). Si se supera este umbral, el HPA escala hacia arriba.

📋 **Resumen de Configuración del HPA**

| Parámetro          | Valor          | Descripción                                           |
|--------------------|----------------|-------------------------------------------------------|
| `minReplicas`      | 1              | Mínimo número de pods                                 |
| `maxReplicas`      | 10             | Máximo número de pods                                 |
| `target.cpu.util`  | 25%            | Umbral de utilización de CPU para escalar             |
| `scaleTargetRef`   | nginx-test     | Deployment que será escalado                          |

### 3.3 🚀 Despliegue de los Manifiestos

```bash
kubectl apply -f load_test/manifests/nginx-deployment.yaml
kubectl apply -f load_test/manifests/hpa.yaml
```

🔍 **Verificación:**
```bash
kubectl get deployments
kubectl get services
kubectl get hpa
```

> ⚠️ Este proceso también está automatizado dentro del script `03_load_test.sh` (paso 1).



## 🔥 4. Generación de Carga (`test.js`)

El archivo `test.js`, ubicado en la carpeta `load_test/scripts/`, define el comportamiento de la prueba de carga que será aplicada al servicio NGINX desplegado. Utiliza la herramienta `k6`, un framework especializado en pruebas de rendimiento, para simular múltiples usuarios realizando solicitudes HTTP de forma progresiva.

```javascript
export let options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '2m', target: 150 },
    { duration: '3m', target: 300 },
    { duration: '2m', target: 50 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  http.get('http://<IP_DEL_CLUSTER>:30080');
  sleep(1);
}
```

📌 **Importante:** reemplazar `<IP_DEL_CLUSTER>` por la IP del nodo donde está expuesto el servicio. Puede obtenerse mediante:

```bash
kubectl get nodes -o wide
```

> 🛠 Este paso está automatizado parcialmente por el script `03_load_test.sh`, pero la edición manual de la IP puede seguir siendo necesaria.

---

## 📡 5. Recolección de Métricas (`metric_collector.sh`)

Este script recolecta métricas de CPU, memoria y número de pods en ejecución cada 10 segundos durante la prueba de carga.

### Actividades:
- Usa `kubectl top pod` para capturar el uso actual de recursos.
- Extrae `requests.cpu` desde la definición del pod.
- Calcula el % de uso de CPU:

```
%cpu = (uso_actual_millicores / requests_cpu_millicores) * 100
```

- Cuenta los pods activos:
```bash
kubectl get pods --no-headers | wc -l
```

Todos los datos son formateados como CSV y guardados en `load_test/output/metrics.csv`.

### 🧪 Ejemplo de Salida

```csv
timestamp,pod,cpu(millicores),memory(bytes),%cpu,num_pods
2025-03-25 16:14:41,nginx-test-xxx,0,16Mi,0,1
...
```

📌 **Automatización:** el script se ejecuta automáticamente desde `03_load_test.sh` en segundo plano (paso 3) y se detiene al finalizar la prueba.

#### ⚠️ Si queda corriendo
```bash
ps aux | grep metric_collector.sh
kill <PID>
```

---

## 📈 6. Análisis de Resultados (Python)

### 6.1 `plot_cpu_usage.py`
Este script genera visualizaciones del uso de CPU para cada pod a lo largo del tiempo:
- Gráfico combinado de todos los pods.
- Gráficos individuales por pod (`images/cpu_pod/`).

```python
file_path = "output/metrics.csv"
df = pd.read_csv(file_path)
df["timestamp"] = pd.to_datetime(df["timestamp"])
...
```

### 6.2 `plot_pod_count.py`
Genera un gráfico de la evolución del número de pods:
```python
plt.plot(df["timestamp"], df["num_pods"])
plt.savefig("images/pod_count_over_time.png")
```

📌 Asegura tener instaladas las dependencias (`pandas`, `matplotlib`) y configurar rutas si cambias el CSV de lugar.

---

## 🐳 7. Automatización con Docker

Para garantizar reproducibilidad del entorno de análisis:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY plot_*.py requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p images output
CMD ["sh", "-c", "python plot_cpu_usage.py && python plot_pod_count.py"]
```

📦 El contenedor se lanza automáticamente desde `03_load_test.sh` (paso 6) y monta volúmenes necesarios para el análisis.

---

## 🧹 8. Eliminación de Recursos del Clúster

```bash
kubectl delete -f load_test/manifests/nginx-deployment.yaml
kubectl delete -f load_test/manifests/hpa.yaml
```

> Esta operación está automatizada en el paso 7 de `03_load_test.sh`.

---

✅ **Con este flujo completo, es posible simular carga, recolectar datos, analizarlos y automatizar el ciclo de prueba para validar la escalabilidad horizontal de un servicio en Kubernetes.**

