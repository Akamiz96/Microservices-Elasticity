# 📂 Guía de Contenido - Carpeta `k8s-tests`

Esta carpeta contiene archivos de prueba diseñados para validar el correcto funcionamiento de un clúster Kubernetes previamente configurado. Las pruebas incluyen desde el despliegue básico de aplicaciones hasta evaluaciones de escalabilidad, y permiten asegurar que el entorno esté listo para ejecutar cargas reales.

---

## 🧪 Archivos de Prueba

### 1️⃣ [`01_test_cluster.md`](../k8s-tests/01_test_cluster.md)

Este archivo describe una **prueba básica de validación del clúster**, asegurando que se pueda desplegar correctamente una aplicación simple. Incluye:

- Creación de un Deployment y un Service en Kubernetes.
- Verificación de la correcta ejecución de pods y exposición del servicio.
- Comprobación del acceso a la aplicación desde fuera del clúster.

Ideal para verificar que el clúster fue instalado correctamente y está operativo.

### 2️⃣ [`02_scalability_test.md`](../k8s-tests/02_scalability_test.md)

Este archivo documenta una **prueba de escalabilidad del clúster**, con el objetivo de evaluar el comportamiento del sistema bajo una carga creciente. Contiene:

- Despliegue de múltiples réplicas de una aplicación.
- Monitoreo del comportamiento del clúster ante el aumento de pods.
- Evaluación de tiempos de respuesta, uso de recursos y capacidad de autoescalado (si está configurado).

Es útil para validar la elasticidad del sistema y su preparación para entornos productivos o pruebas de estrés.

---

## ⚙️ Scripts de Automatización

### 3️⃣ [`01_test_cluster.sh`](../k8s-tests/files/01_test_cluster.sh)

Este script automatiza la **prueba básica de despliegue de una aplicación** en el clúster Kubernetes. Ejecuta los comandos necesarios para:

- Crear un Deployment y un Service.
- Esperar a que los pods estén listos.
- Imprimir información de acceso para validar el despliegue.

Útil para realizar pruebas rápidas y repetir el proceso de validación sin intervención manual.

### 4️⃣ [`02_scalability_test.sh`](../k8s-tests/files/02_scalability_test.sh)

Este script ejecuta de forma automatizada la **prueba de escalabilidad** descrita en el archivo correspondiente. Incluye:

- Despliegue progresivo de múltiples réplicas de una aplicación.
- Medición de tiempos de despliegue y recolección de métricas básicas.
- Limpieza de recursos tras la prueba.

Ideal para pruebas de rendimiento controladas y repetibles sobre el clúster.

---

Los archivos en esta carpeta están diseñados para verificar que el clúster Kubernetes pueda ejecutar aplicaciones correctamente y escalar ante diferentes niveles de carga. Se recomienda ejecutar estas pruebas después de realizar la configuración inicial con éxito.

🚀 ¡Con estos tests y scripts, tu clúster estará listo para cualquier desafío!
