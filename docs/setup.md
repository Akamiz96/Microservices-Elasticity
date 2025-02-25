# Configuración del Entorno para Kubernetes

Este documento proporciona una guía paso a paso para la instalación y configuración de un clúster Kubernetes utilizando **kubeadm**. La configuración adecuada del entorno es fundamental para garantizar un despliegue exitoso y un clúster estable.

## 📌 Requisitos Previos
Antes de comenzar, asegúrate de cumplir con los siguientes requisitos:
- **Sistemas operativos compatibles**: Ubuntu, CentOS, Fedora (se recomienda Ubuntu).
- **Acceso root o permisos sudo**.
- **Al menos dos nodos** (uno maestro y uno o más trabajadores).
- **Conectividad de red entre los nodos**.

## 🚀 Instalación de Kubernetes

### 1️⃣ Verificar el Sistema Operativo
Asegúrate de que los nodos ejecuten la misma versión de Linux y que estén actualizados:
```bash
sudo apt update && sudo apt upgrade -y
```

### 2️⃣ Instalar Docker
Kubernetes usa contenedores, por lo que es necesario instalar Docker:
```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

### 3️⃣ Instalar kubeadm, kubelet y kubectl
Estas herramientas son esenciales para la administración del clúster:
```bash
sudo apt install -y apt-transport-https ca-certificates curl
curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

## 🛠 Configuración de los Nodos

### 4️⃣ Configurar los Hostnames
Cada nodo debe tener un nombre único:
```bash
sudo hostnamectl set-hostname <nombre-del-nodo>
```

### 5️⃣ Desactivar Swap
Kubernetes requiere que el swap esté desactivado:
```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
```

### 6️⃣ Configuración del Firewall
Abrir los puertos requeridos:
```bash
sudo ufw allow 6443/tcp
sudo ufw allow 2379:2380/tcp
sudo ufw allow 10250:10252/tcp
sudo ufw reload
```

## 🏗 Inicialización del Clúster

### 7️⃣ Inicializar el Nodo Maestro
En el nodo maestro, ejecuta:
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```
Después de la inicialización, configura `kubectl`:
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 8️⃣ Unir Nodos Trabajadores al Clúster
Ejecuta el comando generado tras la inicialización en cada nodo trabajador:
```bash
sudo kubeadm join <MAESTRO_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>
```

## 🌐 Configuración de la Red
Instalar Flannel para gestionar la red entre los pods:
```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```
Verifica que los pods de Flannel estén ejecutándose:
```bash
kubectl get pods -n kube-system
```

## 🔍 Verificación del Clúster
Para comprobar el estado del clúster, usa:
```bash
kubectl get nodes
```
Si todo está correctamente configurado, los nodos aparecerán en estado **Ready**.

## 📌 Conclusión
Siguiendo estos pasos, tendrás un clúster Kubernetes funcional listo para experimentar con elasticidad y autoescalado. En los siguientes documentos exploraremos cómo configurar **HPA (Horizontal Pod Autoscaler)** y herramientas de monitoreo como **Prometheus y Grafana**.
