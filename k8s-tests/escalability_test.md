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
Aplicamos la configuración:
```bash
kubectl apply -f nginx-deployment.yaml
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
Aplicamos la configuración:
```bash
kubectl apply -f hpa.yaml
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
Reemplaza `<IP_DEL_CLUSTER>` con la IP del nodo donde está corriendo el servicio:
```bash
kubectl get nodes -o wide
```
Ejecutamos la prueba de carga con **k6**:
```bash
k6 run test.js
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

## ✅ Conclusión
Este experimento demuestra cómo Kubernetes ajusta dinámicamente los recursos en respuesta a la demanda. Si el autoescalado funciona correctamente, veremos un aumento progresivo en el número de pods hasta que la carga se reduzca nuevamente. 🚀
