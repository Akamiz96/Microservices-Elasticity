# Microservices-Elasticity  

Este repositorio contiene comandos, ejemplos y herramientas para evaluar la elasticidad de microservicios desplegados en **Kubernetes**. Se enfoca en el impacto del autoescalado reactivo en aplicaciones con dependencias, utilizando métricas y metodologías de experimentación para medir su rendimiento bajo diferentes condiciones de carga.  

## 📌 Objetivo  
El objetivo principal es proporcionar una plataforma de experimentación para medir y analizar la elasticidad de microservicios en Kubernetes, con énfasis en:  

- **Selección de métricas clave** para evaluar elasticidad y rendimiento.  
- **Despliegue de infraestructura** para experimentación con Kubernetes.  
- **Ejecución de pruebas de carga** utilizando herramientas como `k6`, `Prometheus`, `Grafana`, `HPA` y `KEDA`.  
- **Análisis de resultados** para proponer mejoras en configuraciones de autoescalado y arquitectura de microservicios.  

## 🔧 Tecnologías y Herramientas  
- **Orquestador**: Kubernetes  
- **Monitoreo y métricas**: Prometheus, Grafana  
- **Pruebas de carga**: k6  
- **Autoescalado**: HPA (Horizontal Pod Autoscaler), KEDA  
- **Scripts y automatización**: Bash, YAML  

## 📂 Estructura del Repositorio  
```
/docs               # Documentación y referencias
/scripts           # Scripts útiles para experimentos
/k8s-configs       # Archivos YAML para despliegues en Kubernetes
/results           # Resultados y análisis de experimentos
```

## 🚀 Cómo Empezar  
1. **Clona este repositorio**  
   ```bash
   git clone https://github.com/tu-usuario/Microservices-Elasticity.git
   cd Microservices-Elasticity
   ```
2. **Explora los scripts y configuraciones** en la carpeta `/k8s-configs`.  
3. **Ejecuta experimentos** con las instrucciones en `/docs`.  

## 📜 Licencia  
Este proyecto está bajo la licencia **Apache 2.0**. Consulta el archivo `LICENSE` para más detalles.