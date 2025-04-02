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

| Carpeta | Descripción |
|--------|-------------|
| [`/docs/`](docs/) | Documentación general del proyecto y navegación entre pruebas. |
| [`/k8s-configs/`](k8s-configs/) | Scripts y guías para instalar, configurar y reiniciar un clúster Kubernetes local. |
| [`/k8s-tests/`](k8s-tests/) | Pruebas de validación funcional y simulación de carga sobre el clúster. |
| [`/elasticity-m1/`](elasticity-m1/) | Conjunto de experimentos de elasticidad centrados en un solo microservicio. |

Para consultar el contenido completo de cada una de estas secciones, revisa los siguientes archivos:

- [`docs/k8s-configs_overview.md`](docs/k8s-configs_overview.md) – Detalle de `/k8s-configs`
- [`docs/k8s-tests_overview.md`](docs/k8s-tests_overview.md) – Detalle de `/k8s-tests`
- [`docs/elasticity-m1_overview.md`](docs/elasticity-m1_overview.md) – Detalle de `/elasticity-m1`


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

---

## 🤝 Contribuciones

Este repositorio incluye plantillas de Pull Request en **español** e **inglés**.

Cuando abras un nuevo PR, GitHub te permitirá elegir una de las siguientes plantillas:

- 📄 `pr_template_es.md` – Plantilla en español
- 📄 `pr_template_en.md` – Template in English

Por favor, usa una de ellas para facilitar la revisión y mantener la consistencia del proyecto. 🚀