# 🧪 Overview de los Experimentos de Elasticidad

Este documento resume los distintos experimentos realizados para analizar la **elasticidad** de un microservicio desplegado en Kubernetes bajo diferentes configuraciones de autoscaling. Cada sección incluye un enlace al archivo detallado del experimento correspondiente, y en algunos casos, a los resultados obtenidos.

---

## 1. Microbenchmark de consumo de CPU

Antes de realizar experimentos de elasticidad, se llevó a cabo un microbenchmark para estimar el consumo promedio de CPU por cada **request** y por cada **usuario virtual (VU)** en el entorno de pruebas. Estos valores son fundamentales para convertir la carga de trabajo en demanda estimada de CPU.

📄 [Ver detalle del microbenchmark](02_exp0_microbenchmark.md)

---

## 2. Experimento: Autoscaling básico (HPA por CPU)

Este experimento aplica una configuración básica de Horizontal Pod Autoscaler (HPA) para escalar un microservicio en función del uso de CPU. El objetivo es observar cómo responde el sistema ante una carga creciente y decreciente.

📄 [Ver detalle del experimento](03_exp1_basic-autoscaling.md)

📊 [Ver resultados del experimento](04_exp1_basic-autoscaling_results.md)

---

## 3. Resultados y métricas de elasticidad

A partir de los datos recolectados durante el experimento de autoscaling, se calcularon un conjunto de métricas para evaluar la **eficiencia y precisión** del sistema al adaptarse a la carga. Estas métricas permiten cuantificar aspectos como el tiempo de reacción, el sobreaprovisionamiento y la precisión del escalamiento.

📄 [Ver resultados del experimento](04_exp1_basic-autoscaling_results.md)

---

