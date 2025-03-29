# Configuración del Entorno para Kubernetes

Este documento proporciona una guía paso a paso para la instalación y configuración de un clúster Kubernetes utilizando **kubeadm**. La configuración adecuada del entorno es fundamental para garantizar un despliegue exitoso y un clúster estable.

## 📌 Requisitos Previos
Antes de comenzar, asegúrate de cumplir con los siguientes requisitos:
- **Sistemas operativos compatibles**: Ubuntu, CentOS, Fedora (se recomienda Ubuntu).
- **Acceso root o permisos sudo**.
- **Al menos dos nodos** (uno maestro y uno o más trabajadores).
- **Conectividad de red entre los nodos**.

---

## 🚀 Paso 1: Instalación de Kubernetes

### 1.1 Verificar el Sistema Operativo
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Instalar Docker
```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
```

### 1.3 Instalar kubeadm, kubelet y kubectl
```bash
  sudo apt install -y apt-transport-https ca-certificates curl gnupg
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | \
        gpg --dearmor | sudo tee /etc/apt/keyrings/kubernetes-apt-keyring.gpg > /dev/null
  echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /" | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo apt update
  sudo apt install -y kubelet kubeadm kubectl
  sudo apt-mark hold kubelet kubeadm kubectl
```

---

## 🛠 Paso 2: Configuración de los Nodos

### 2.1 Configurar los Hostnames
```bash
sudo hostnamectl set-hostname <nombre-del-nodo>
```

### 2.2 Desactivar Swap
```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
```

### 2.3 Configuración del Firewall
```bash
sudo ufw allow 6443/tcp
sudo ufw allow 2379:2380/tcp
sudo ufw allow 10250:10252/tcp
sudo ufw reload
```

### 2.4 Configurar Taints en Nodos Trabajadores
```bash
kubectl taint node worker7 node-role.kubernetes.io/control-plane:NoSchedule-
```
O de forma genérica:
```bash
kubectl taint node <nombre-del-nodo> node-role.kubernetes.io/control-plane:NoSchedule-
```

Verifica los taints:
```bash
kubectl get nodes -o wide
kubectl describe node <nombre-del-nodo>
```

---

## 🏗 Paso 3: Inicialización del Clúster

### 3.1 Inicializar el Nodo Maestro
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

### 3.2 Configurar `kubectl`
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 3.3 Unir Nodos Trabajadores al Clúster
```bash
sudo kubeadm join <MAESTRO_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>
```

---

## 🌐 Paso 4: Configuración de la Red

### 4.1 Instalar Flannel
```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

### 4.2 Verificar la red
```bash
kubectl get pods -n kube-system
```

---

## 📊 Paso 5: Instalación del Metrics Server

### 5.1 Verificar si HPA recolecta métricas
```bash
kubectl get hpa
```

### 5.2 Instalar el Metrics Server
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 5.3 Habilitar `--kubelet-insecure-tls`
```bash
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-", "value":"--kubelet-insecure-tls"}]'
```

### 5.4 Verificar el Metrics Server
```bash
kubectl get pods -n kube-system | grep metrics-server
```

---

## 🔍 Paso 6: Verificación del Clúster

```bash
kubectl get nodes
```
Los nodos deben aparecer con el estado **Ready**.

---

## ✅ Conclusión

Siguiendo estos pasos, tendrás un clúster Kubernetes funcional y listo para experimentar con elasticidad y autoescalado. En los siguientes documentos se abordará la configuración de **Horizontal Pod Autoscaler (HPA)**.
