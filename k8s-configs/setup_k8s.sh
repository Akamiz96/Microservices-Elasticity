#!/bin/bash

# Salir si ocurre cualquier error
set -e

# Verificar requisitos previos
echo "Verificando requisitos previos..."
if [[ "$(lsb_release -si)" != "Ubuntu" ]]; then
    echo "Este script solo está diseñado para Ubuntu."
    exit 1
fi

if [[ "$EUID" -ne 0 ]]; then
    echo "Este script debe ejecutarse como root o con sudo."
    exit 1
fi

# Verificar si el usuario tiene permisos sudo
echo "Verificando permisos de sudo..."
if sudo -l &>/dev/null; then
    echo "El usuario tiene permisos de sudo."
else
    echo "Error: El usuario no tiene permisos de sudo. Asegúrate de que tiene privilegios adecuados."
    exit 1
fi

# Instalación de Docker
echo "Verificando e instalando Docker..."
if ! command -v docker &> /dev/null; then
    sudo apt update
    sudo apt install -y docker.io
    sudo systemctl enable docker
    sudo systemctl start docker
else
    echo "Docker ya está instalado."
fi

# Instalación de Kubernetes tools
echo "Verificando e instalando kubeadm, kubelet y kubectl..."
if ! command -v kubeadm &> /dev/null; then
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt update
    sudo apt install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
else
    echo "kubeadm, kubelet y kubectl ya están instalados."
fi

# Desactivar Swap y configurar firewall
echo "Desactivando swap y configurando firewall..."
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
sudo ufw allow 6443/tcp
sudo ufw allow 2379:2380/tcp
sudo ufw allow 10250:10252/tcp
sudo ufw reload

echo "Firewall configurado."

# Inicialización del nodo maestro
echo "Inicializando el nodo maestro de Kubernetes..."
POD_NETWORK="10.244.0.0/16"
sudo kubeadm init --pod-network-cidr=$POD_NETWORK

# Configurar kubectl para el usuario actual
echo "Configurando kubeconfig..."
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Configurar red con Flannel
echo "Aplicando configuración de red con Flannel..."
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# Eliminar taints en nodos trabajadores
echo "Eliminando taints en nodos trabajadores si existen..."
kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule- || echo "No se encontraron taints para eliminar."

# Verificación del estado del clúster
echo "Verificación final del clúster..."
kubectl get nodes

echo "Kubernetes ha sido instalado y configurado exitosamente."
