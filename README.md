# Microservices-Elasticity

Este repositorio contiene comandos, scripts, configuraciones y documentación para evaluar la **elasticidad de microservicios desplegados en Kubernetes**. El proyecto se enfoca en el impacto del autoescalado reactivo utilizando `HPA` y pruebas de carga, en entornos controlados y reproducibles.

## 📌 Objetivo

El objetivo principal es proporcionar una plataforma de experimentación para medir y analizar la elasticidad de microservicios en Kubernetes, con énfasis en:

- **Selección de métricas clave** para evaluar elasticidad y rendimiento.
- **Despliegue automatizado de infraestructura** para clústeres Kubernetes.
- **Ejecución de pruebas de carga** utilizando herramientas como `k6`.
- **Evaluación del comportamiento del HPA** en diferentes escenarios de uso.
- **Documentación clara y reproducible** para cada experimento realizado.

---

## 🔧 Tecnologías y Herramientas

- **Orquestador**: Kubernetes (`kubeadm`, `kubectl`, `kubelet`)
- **Autoescalado**: HPA (Horizontal Pod Autoscaler)
- **Red de pods**: Flannel
- **Pruebas de carga**: k6
- **Métricas**: Metrics Server
- **Automatización**: Bash scripts

---

## 📂 Estructura del Repositorio

```bash
/docs/                       # Documentación explicativa y guías de navegación
  ├── intro.md               # Introducción general al proyecto
  ├── k8s-configs_overview.md  # Índice y descripción de archivos en /k8s-configs
  └── k8s-tests_overview.md    # Índice y descripción de archivos en /k8s-tests

/k8s-configs/                # Scripts y guías para instalación y reinicio del clúster
  ├── setup_k8s.sh           # Script automatizado para instalar Kubernetes + Metrics Server
  ├── reset_k8s.sh           # Script automatizado para reiniciar el clúster
  ├── setup.md               # Guía paso a paso para la instalación del clúster
  └── reset_cluster.md       # Guía paso a paso para resetear el clúster

/k8s-tests/                  # Pruebas diseñadas para validar el comportamiento del clúster
  ├── 01_test_cluster.md           # Documento que describe una prueba básica de funcionamiento del clúster con nginx y HPA
  ├── 02_escalability_test.md      # Documento que describe una prueba de escalabilidad con carga generada por k6 y monitoreo de HPA
  └── files/                       # Contiene los scripts automatizados y recursos necesarios para las pruebas
      ├── 01_test_cluster.sh       # Script que ejecuta automáticamente la prueba de despliegue, servicio y autoescalado
      ├── 02_escalability_test.sh  # Script que ejecuta la prueba de carga con k6 y monitorea el escalado de pods
      └── scalability_test/        # Recursos YAML y JS utilizados específicamente en la prueba de escalabilidad
          ├── nginx-deployment.yaml  # Despliegue base de una app nginx con límites de CPU definidos
          ├── hpa.yaml               # Configuración del Horizontal Pod Autoscaler para el despliegue nginx
          └── test.js                # Script de prueba de carga para k6, con etapas de aumento y reducción de tráfico

```

---

## 🚀 Cómo Empezar

Antes de ejecutar cualquier script, asegúrate de **leer primero la documentación correspondiente** ubicada en la carpeta `/k8s-configs` o `/k8s-tests`.

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/Microservices-Elasticity.git
   cd Microservices-Elasticity
   ```

2. **Revisa la documentación general**:
   - [Introducción al proyecto](docs/intro.md)
   - [Descripción de archivos de configuración](docs/k8s-configs_overview.md)
   - [Descripción de las pruebas de clúster](docs/k8s-tests_overview.md)

3. **Instala el clúster Kubernetes**:
   - Revisa la guía [01_setup_k8s.md](k8s-configs/01_setup_k8s.md)
   - Luego, ejecuta el script automatizado:
     ```bash
     ./k8s-configs/files/01_setup_k8s.sh
     ```

4. **(Opcional) Resetea el clúster Kubernetes**:
   - Revisa la guía [02_reset_k8s.md](k8s-configs/02_reset_k8s.md)
   - Luego, ejecuta:
     ```bash
     ./k8s-configs/files/02_reset_k8s.sh
     ```

5. **Ejecuta la prueba básica del clúster**:
   - Revisa [01_test_cluster.md](k8s-tests/01_test_cluster.md)
   - Luego, ejecuta:
     ```bash
     ./k8s-tests/files/01_test_cluster.sh
     ```

6. **Ejecuta la prueba de escalabilidad**:
   - Revisa [02_scalability_test.md](k8s-tests/02_scalability_test.md)
   - Luego, ejecuta:
     ```bash
     ./k8s-tests/files/02_scalability_test.sh
     ```

---

## 📜 Licencia

Este proyecto está bajo la licencia **Apache 2.0**. Consulta el archivo `LICENSE` para más detalles.
