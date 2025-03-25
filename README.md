# ElasticLab

*ElasticLab* es un entorno experimental diseñado para estudiar el comportamiento elástico de microservicios desplegados en Kubernetes. Su nombre nace de la unión entre "elasticidad" y "laboratorio", reflejando su propósito como plataforma flexible y controlada para pruebas, análisis y automatización de escalado dinámico en arquitecturas modernas.

Este repositorio contiene scripts, configuraciones y documentación para **evaluar la elasticidad de microservicios desplegados en Kubernetes**. El proyecto está diseñado como un entorno de pruebas controlado, reproducible y documentado, que permite analizar cómo se comportan los mecanismos de autoescalado (como el Horizontal Pod Autoscaler) en respuesta a diferentes tipos de carga.

Autor: **Alejandro Castro Martínez**

---

## 🌟 Objetivo del Proyecto

El objetivo de este laboratorio es estudiar y documentar el **comportamiento dinámico de sistemas distribuidos** basados en microservicios ante fluctuaciones de demanda, enfocado especialmente en:

- Entender la relación entre carga de trabajo, uso de recursos y escalado automático.
- Evaluar el desempeño del **HPA (Horizontal Pod Autoscaler)** con distintas configuraciones.
- Analizar métricas como uso de CPU, número de réplicas, tiempo de reacción y estabilidad del sistema.
- Automatizar entornos de prueba con Kubernetes y scripts Bash.
- Generar evidencia visual y cuantitativa del proceso de escalado (gráficas, métricas, etc.).
- Servir como base para experimentación académica o técnica en elasticidad de sistemas.

---

## ⚙️ Tecnologías y Herramientas Utilizadas

- **Orquestador**: Kubernetes (`kubeadm`, `kubectl`, `kubelet`)
- **Autoescalado**: Horizontal Pod Autoscaler (HPA)
- **Red de Pods**: Flannel
- **Pruebas de carga**: [`k6`](https://k6.io)
- **Métricas**: Metrics Server
- **Automatización**: Bash scripts
- **Contenedores**: Docker (para ejecutar los análisis en Python)
- **Análisis de resultados**: Python (pandas, matplotlib)

---

## 📁 Estructura del Repositorio

```bash
/docs/                     
  ├── intro.md                     # Introducción general al proyecto
  ├── k8s-configs_overview.md     # Índice y descripción de archivos en /k8s-configs
  └── k8s-tests_overview.md       # Índice y descripción de archivos en /k8s-tests

/k8s-configs/                
  ├── 01_setup_k8s.md             # Guía de instalación del clúster Kubernetes
  ├── 02_reset_k8s.md             # Guía para reiniciar el clúster Kubernetes
  └── files/
      ├── 01_setup_k8s.sh         # Script automatizado para instalación
      └── 02_reset_k8s.sh         # Script automatizado para reinicio

/k8s-tests/                  
  ├── 01_test_cluster.md              # Prueba básica del clúster con nginx y HPA
  ├── 02_escalability_test.md         # Prueba de escalabilidad con carga generada por k6
  ├── 03_load_test.md                 # Descripción de la prueba de carga con análisis de métricas
  ├── 04_results_load_test.md         # Resultados y visualización de métricas obtenidas
  └── files/
      ├── 01_test_cluster.sh          # Script automatizado para prueba básica
      ├── 02_escalability_test.sh     # Script automatizado para prueba de escalabilidad
      ├── 03_load_test.sh             # Script automatizado para la prueba de carga y recolección de métricas
      └── load_test/                  # Carpeta con recursos y resultados de la prueba de carga
          ├── analysis/               # Scripts de análisis y visualización en Python
          │   ├── Dockerfile          # Imagen para entorno de análisis
          │   ├── plot_cpu_usage.py   # Script para graficar uso de CPU
          │   ├── plot_pod_count.py   # Script para graficar número de pods
          │   └── requirements.txt    # Dependencias del entorno de análisis
          ├── manifests/              # Archivos de configuración de Kubernetes
          │   ├── hpa.yaml            # Configuración del Horizontal Pod Autoscaler
          │   └── nginx-deployment.yaml # Despliegue del servicio nginx
          ├── scripts/                # Scripts de ejecución para la prueba de carga
          │   ├── metric_collector.sh # Recolector de métricas en Bash
          │   └── test.js             # Script de prueba de carga para k6
          └── output/
              └── metrics.csv         # Métricas recolectadas durante la prueba (CPU, réplicas, etc.)
```

---

## 🚀 Cómo Empezar

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/elasticlab.git
cd elasticlab
```

---

### 2. Lee la documentación general

- [`docs/intro.md`](docs/intro.md)
- [`docs/k8s-configs_overview.md`](docs/k8s-configs_overview.md)
- [`docs/k8s-tests_overview.md`](docs/k8s-tests_overview.md)

---

### 3. Instala el clúster Kubernetes

- Revisa la guía: `k8s-configs/01_setup_k8s.md`
- Luego ejecuta:

```bash
./k8s-configs/files/01_setup_k8s.sh
```

---

### 4. (Opcional) Reinicia el clúster

- Revisa la guía: `k8s-configs/02_reset_k8s.md`
- Luego ejecuta:

```bash
./k8s-configs/files/02_reset_k8s.sh
```

---

### 5. Ejecuta la prueba básica del clúster

- Revisa: `k8s-tests/01_test_cluster.md`
- Ejecuta:

```bash
./k8s-tests/files/01_test_cluster.sh
```

---

### 6. Ejecuta la prueba de escalabilidad

- Revisa: `k8s-tests/02_escalability_test.md`
- Ejecuta:

```bash
./k8s-tests/files/02_escalability_test.sh
```

---

### 7. Ejecuta la prueba de carga y análisis

- Revisa:
  - `k8s-tests/03_load_test.md`
  - `k8s-tests/04_results_load_test.md`

- Ejecuta:

```bash
./k8s-tests/files/03_load_test.sh
```

---

## 📜 Licencia

Este proyecto está bajo la licencia **Apache 2.0**. Consulta el archivo `LICENSE` para más detalles.

