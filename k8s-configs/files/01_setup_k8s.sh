#!/bin/bash

# Script para instalar y configurar un clúster Kubernetes en Ubuntu
# Requisitos: ejecución como root o mediante sudo

set -e

# ================================================
# 1. Verificación de requisitos previos
# ================================================
echo "[FASE 1] Verificando sistema operativo..."
if [[ "$(lsb_release -si)" != "Ubuntu" ]]; then
    echo "Este script está diseñado para Ubuntu."
    exit 1
fi

if [[ "$EUID" -ne 0 ]]; then
    echo "Este script debe ejecutarse como root o con sudo."
    exit 1
fi

echo "[INFO] Verificando permisos de sudo..."
if sudo -l &>/dev/null; then
    echo "Permisos de sudo verificados."
else
    echo "Error: El usuario no tiene permisos de sudo."
    exit 1
fi
sleep 2

# ================================================
# 2. Instalación de Docker
# ================================================
echo "[FASE 2] Verificando e instalando Docker..."
if ! command -v docker &> /dev/null; then
    sudo apt update
    sudo apt install -y docker.io
    sudo systemctl enable docker
    sudo systemctl start docker
else
    echo "Docker ya está instalado."
fi
sleep 2

# ================================================
# 3. Instalación de kubeadm, kubelet y kubectl
# ================================================
echo "[FASE 3] Instalando herramientas de Kubernetes..."
if ! command -v kubeadm &> /dev/null; then
    sudo apt install -y apt-transport-https ca-certificates curl
    curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt update
    sudo apt install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
else
    echo "kubeadm, kubelet y kubectl ya están instalados."
fi
sleep 2

# ================================================
# 4. Configuración del entorno
# ================================================
echo "[FASE 4] Desactivando swap y configurando firewall..."
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
sudo ufw allow 6443/tcp
sudo ufw allow 2379:2380/tcp
sudo ufw allow 10250:10252/tcp
sudo ufw reload
sleep 2

# ================================================
# 5. Inicialización del clúster
# ================================================
echo "[FASE 5] Inicializando el nodo maestro de Kubernetes..."
POD_NETWORK="10.244.0.0/16"
sudo kubeadm init --pod-network-cidr=$POD_NETWORK
sleep 5

# ================================================
# 6. Configuración de kubectl
# ================================================
echo "[FASE 6] Configurando acceso kubectl para el usuario actual..."
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
sleep 2

# ================================================
# 7. Aplicar red de pods con Flannel
# ================================================
echo "[FASE 7] Aplicando red con Flannel..."
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
sleep 5

# ================================================
# 8. Eliminar taints para permitir programación de pods
# ================================================
echo "[FASE 8] Eliminando taints en nodos..."
kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule- || echo "No se encontraron taints para eliminar."
sleep 2

# ================================================
# 9. Instalación del Metrics Server
# ================================================
echo "[FASE 9] Instalando Metrics Server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
sleep 5

# ================================================
# 10. Habilitar --kubelet-insecure-tls en Metrics Server
# ================================================
echo "[FASE 10] Habilitando flag --kubelet-insecure-tls en Metrics Server..."
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-", "value":"--kubelet-insecure-tls"}]'
sleep 3

# ================================================
# 11. Verificación del Metrics Server
# ================================================
echo "[FASE 11] Verificando estado del Metrics Server..."
kubectl get pods -n kube-system | grep metrics-server || echo "Metrics Server no se encuentra en ejecución."
sleep 2

# ================================================
# 12. Verificación final del clúster
# ================================================
echo "[RESULTADO] Verificación del estado del clúster:"
kubectl get nodes

# ================================================
# Finalización
# ================================================
echo "[FIN] Kubernetes ha sido instalado y configurado exitosamente."
