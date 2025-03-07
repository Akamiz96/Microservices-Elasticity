# Prueba de Funcionamiento del Clúster Kubernetes

Este documento proporciona una prueba básica para verificar que el clúster Kubernetes y las herramientas instaladas están funcionando correctamente. Se utilizará un despliegue sencillo basado en el ejemplo utilizado en **Medir Elasticidad Kubernetes**.

## 📌 Objetivo
El propósito de esta prueba es:
- Validar que Kubernetes está correctamente instalado y operativo.
- Verificar la comunicación entre nodos.
- Confirmar que `kubectl` puede desplegar y gestionar recursos en el clúster.
- Ejecutar un servicio simple para comprobar el autoescalado.

## 🚀 Paso 1: Verificar el Estado del Clúster
Ejecuta el siguiente comando para verificar que todos los nodos están en estado **Ready**:
```bash
kubectl get nodes
```
Si todos los nodos aparecen como **Ready**, el clúster está en funcionamiento.

## 🔧 Paso 2: Desplegar una Aplicación de Prueba
Como prueba básica, desplegaremos un pod con una imagen de prueba (`nginx`) para validar que Kubernetes puede administrar cargas de trabajo.

```bash
kubectl create deployment test-nginx --image=nginx
```
Verifica que el pod esté corriendo:
```bash
kubectl get pods
```
Si aparece el pod en estado **Running**, significa que Kubernetes puede desplegar aplicaciones correctamente.

## 🌐 Paso 3: Exponer la Aplicación
Para asegurarnos de que los servicios funcionan correctamente, expondremos el pod como un servicio accesible dentro del clúster:
```bash
kubectl expose deployment test-nginx --type=NodePort --port=80
```
Verifica el servicio con:
```bash
kubectl get svc
```

## 📊 Paso 4: Probar el Autoescalado
Si el clúster soporta **Horizontal Pod Autoscaler (HPA)**, probemos su funcionamiento:
```bash
kubectl autoscale deployment test-nginx --cpu-percent=50 --min=1 --max=5
```
Verifica la configuración del HPA:
```bash
kubectl get hpa
```
Si se muestra el HPA con la configuración esperada, significa que el autoescalado está funcionando correctamente.

## ✅ Paso 5: Limpiar la Prueba
Después de verificar el funcionamiento, puedes eliminar los recursos creados para la prueba:
```bash
kubectl delete deployment test-nginx
kubectl delete svc test-nginx
kubectl delete hpa test-nginx
```

## 📌 Conclusión
Si todos los pasos se ejecutan sin errores, significa que el clúster Kubernetes está correctamente configurado y listo para ejecutar pruebas más avanzadas sobre elasticidad.