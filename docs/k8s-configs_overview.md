# 📂 Guía de Contenido - Carpeta `k8s-configs`

Esta carpeta contiene los archivos y scripts necesarios para la configuración y reinicio de un clúster Kubernetes utilizando `kubeadm`. A continuación, se describen brevemente los archivos incluidos y su propósito.

---

## 📜 Archivos de Documentación

### 1️⃣ [`setup.md`](../k8s-configs/setup.md)
Este archivo proporciona una **guía paso a paso** sobre cómo instalar y configurar un clúster Kubernetes desde cero. Incluye instrucciones para:
- Instalación de Docker y herramientas de Kubernetes (`kubeadm`, `kubelet`, `kubectl`).
- Configuración del entorno (swap, firewall, red, taints).
- Inicialización del nodo maestro y unión de nodos trabajadores.
- Verificación de la configuración y estado del clúster.

### 2️⃣ [`reset_cluster.md`](../k8s-configs/reset_cluster.md)
Este archivo describe el **proceso de reseteo completo** del clúster Kubernetes. Explica cómo eliminar todas las configuraciones y volver a instalar Kubernetes desde cero. Incluye:
- Comandos para limpiar el clúster y eliminar configuraciones previas.
- Reconfiguración del nodo maestro y aplicación de la red de pods.
- Verificación de la correcta restauración del clúster.

---

## 🖥️ Scripts de Automatización

### 3️⃣ [`setup_k8s.sh`](../k8s-configs/setup_k8s.sh)
Este script **automatiza la instalación y configuración inicial** de Kubernetes. Ejecuta los pasos necesarios para instalar dependencias, configurar el entorno y desplegar el clúster sin intervención manual.

### 4️⃣ [`reset_k8s.sh`](../k8s-configs/reset_k8s.sh)
Este script permite **borrar completamente un clúster Kubernetes** y reiniciarlo desde cero. Es útil en caso de fallos críticos o cuando se necesita un entorno limpio para pruebas.

---

## 📌 Conclusión

Los archivos en esta carpeta están diseñados para facilitar la configuración y administración de un clúster Kubernetes. Si necesitas instalar Kubernetes por primera vez, revisa `setup.md` y usa el script `setup_k8s.sh`. Si necesitas resetear el clúster, sigue las instrucciones en `reset_cluster.md` o ejecuta `reset_k8s.sh`. 🚀
