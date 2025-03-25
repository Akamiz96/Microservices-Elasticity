# Medición de Elasticidad en Kubernetes

Este documento describe un experimento para medir la elasticidad de un despliegue en Kubernetes utilizando **Horizontal Pod Autoscaler (HPA)** y pruebas de carga con **k6**.

## 📌 Objetivo
El objetivo de esta prueba es observar cómo **Kubernetes** escala automáticamente los pods de una aplicación en respuesta a la carga, utilizando el **Horizontal Pod Autoscaler (HPA)**.

---

## 🚀 Paso 1: Desplegar la Aplicación en Kubernetes

Creamos un archivo YAML llamado **`nginx-deployment.yaml`** para desplegar un servicio basado en **Nginx**:
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
        image: nginx
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "200m"
            memory: "256Mi"
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx-test
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080
  type: NodePort
```
**Este archivo también se encuentra como `files/scalability_test/nginx-deployment.yaml`**

Aplicamos la configuración:
```bash
kubectl apply -f files/scalability_test/nginx-deployment.yaml
```

---

## 🔧 Paso 2: Configurar el Horizontal Pod Autoscaler (HPA)

Creamos un archivo YAML llamado **`hpa.yaml`** para configurar el autoescalado:
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
**Este archivo también se encuentra como `files/scalability_test/hpa.yaml`**

Aplicamos la configuración:
```bash
kubectl apply -f files/scalability_test/hpa.yaml
```

Verificamos el estado del **HPA**:
```bash
kubectl get hpa
```

Si el **HPA** no recolecta métricas correctamente, debemos instalar el **Metrics Server**:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Luego, activamos la opción **--kubelet-insecure-tls**:
```bash
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-", "value":"--kubelet-insecure-tls"}]'
```

Verificamos que el **Metrics Server** esté en ejecución:
```bash
kubectl get pods -n kube-system | grep metrics-server
```

---

## 🌐 Paso 3: Ejecutar Pruebas de Carga con k6

Creamos un archivo **`test.js`** con el siguiente contenido:
```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 50 },  // Aumento gradual de carga
        { duration: '1m', target: 200 },  // Mantener carga media
        { duration: '2m', target: 500 },  // Alta carga sostenida
        { duration: '30s', target: 0 }    // Descenso gradual de carga
    ],
};

export default function () {
    http.get('http://<IP_DEL_CLUSTER>:30080');
    sleep(1);
}
```
**Este archivo también se encuentra como `files/scalability_test/test.js`**

Reemplaza `<IP_DEL_CLUSTER>` con la IP del nodo donde está corriendo el servicio:
```bash
kubectl get nodes -o wide
```

Ejecutamos la prueba de carga con **k6**:
```bash
k6 run files/scalability_test/test.js
```

---

## 📊 Paso 4: Monitoreo del Autoescalado

Podemos monitorear en tiempo real cómo se ajustan los recursos observando el **HPA**:
```bash
kubectl get hpa -w
```

También podemos ver el consumo de recursos con:
```bash
kubectl top pods
```

A medida que la carga aumenta, Kubernetes debe crear más **réplicas** del **nginx-test** hasta alcanzar el límite de **10 pods**.

---

## ⚙️ Uso del Script Automatizado

Todos los pasos anteriores pueden ejecutarse de forma automática utilizando el siguiente script:

```bash
files/02_escalability_test.sh
```

### 🧪 Ejecución del Script

1. Asegúrate de que el archivo tenga permisos de ejecución:
```bash
chmod +x files/02_escalability_test.sh
```

2. Ejecuta el script:
```bash
./files/02_escalability_test.sh
```

Este script:
- Despliega la aplicación.
- Aplica la configuración del HPA.
- Lanza la prueba de carga con `k6`.
- Ejecuta el monitoreo en segundo plano.
- Presenta los resultados automáticamente.

---
## 🧹 Limpieza de Recursos

Una vez finalizada la prueba, puedes liberar los recursos creados (deployment, servicio y HPA) para dejar el clúster limpio.

### Opción 1: Limpieza automática al final del script

El script `files/02_escalability_test.sh` te preguntará si deseas eliminar los recursos creados. Si respondes `y`, ejecutará automáticamente:

```bash
kubectl delete deployment nginx-test
kubectl delete service nginx-service
kubectl delete hpa nginx-hpa
```

Esto eliminará los pods y configuraciones utilizadas durante el experimento.

### Opción 2: Limpieza manual

Si ejecutaste la prueba paso a paso, puedes eliminar los recursos manualmente con los siguientes comandos:

```bash
kubectl delete deployment nginx-test
kubectl delete service nginx-service
kubectl delete hpa nginx-hpa
```

---

## ✅ Conclusión

Este experimento demuestra cómo Kubernetes ajusta dinámicamente los recursos en respuesta a la demanda. Si el autoescalado funciona correctamente, veremos un aumento progresivo en el número de pods hasta que la carga se reduzca nuevamente.
