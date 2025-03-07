#!/bin/bash

# Salir si ocurre cualquier error
echo "Iniciando reinicialización de Kubernetes..."
set -e

# Reset de Kubernetes con kubeadm
if command -v kubeadm &> /dev/null; then
    echo "Reseteando Kubernetes..."
    sudo kubeadm reset -f
else
    echo "Error: kubeadm no está instalado."
    exit 1
fi

# Eliminación de archivos de configuración previos
echo "Eliminando archivos de configuración previos..."
rm -rf $HOME/.kube
sudo rm -rf /etc/kubernetes/ /var/lib/etcd /var/lib/kubelet

# Inicialización del cluster Kubernetes
POD_NETWORK="10.244.0.0/16"
echo "Inicializando Kubernetes con CIDR de red de pods: $POD_NETWORK"
sudo kubeadm init --pod-network-cidr=$POD_NETWORK

# Configuración del acceso para el usuario actual
echo "Configurando kubeconfig..."
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Aplicación de la red de pods Flannel
echo "Aplicando configuración de red con Flannel..."
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# Quitando taint al nodo de control para que pueda ejecutar pods
echo "Quitando taint al nodo worker7..."
kubectl taint node worker7 node-role.kubernetes.io/control-plane:NoSchedule- || echo "Aviso: No se pudo quitar el taint, puede que el nodo no exista o ya esté configurado."

echo "Kubernetes ha sido reinicializado exitosamente."

