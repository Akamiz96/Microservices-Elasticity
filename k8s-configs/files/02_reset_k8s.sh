#!/bin/bash

# Script para reinicializar completamente un clúster Kubernetes
# Incluye reseteo, reconfiguración del entorno, red de pods y Metrics Server

set -e

# ================================================
# 1. Reset del clúster Kubernetes
# ================================================
echo "[FASE 1] Reseteando el clúster Kubernetes..."
if command -v kubeadm &> /dev/null; then
    sudo kubeadm reset -f
else
    echo "Error: kubeadm no está instalado."
    exit 1
fi
sleep 2

# ================================================
# 2. Eliminación de archivos de configuración
# ================================================
echo "[FASE 2] Eliminando archivos y configuraciones previas..."
rm -rf $HOME/.kube
sudo rm -rf /etc/kubernetes/ /var/lib/etcd /var/lib/kubelet
sleep 2

# ================================================
# 3. Inicialización del nuevo clúster
# ================================================
echo "[FASE 3] Inicializando el nuevo clúster..."
POD_NETWORK="10.244.0.0/16"
sudo kubeadm init --pod-network-cidr=$POD_NETWORK
sleep 5

# ================================================
# 4. Configuración de acceso a kubectl
# ================================================
echo "[FASE 4] Configurando acceso kubectl para el usuario actual..."
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
sleep 2

# ================================================
# 5. Aplicación de red de pods con Flannel
# ================================================
echo "[FASE 5] Aplicando red con Flannel..."
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
sleep 5

# ================================================
# 6. Eliminar taint del nodo para permitir ejecución de pods
# ================================================
echo "[FASE 6] Quitando taint del nodo de control..."
kubectl taint node $(hostname) node-role.kubernetes.io/control-plane:NoSchedule- || echo "Aviso: No se encontró taint en el nodo."
sleep 2

# ================================================
# 7. Instalación del Metrics Server
# ================================================
echo "[FASE 7] Instalando Metrics Server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
sleep 5

# ================================================
# 8. Habilitar --kubelet-insecure-tls en Metrics Server
# ================================================
echo "[FASE 8] Habilitando flag --kubelet-insecure-tls en Metrics Server..."
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-", "value":"--kubelet-insecure-tls"}]'
sleep 3

# ================================================
# 9. Verificación del Metrics Server
# ================================================
echo "[FASE 9] Verificando estado del Metrics Server..."
kubectl get pods -n kube-system | grep metrics-server || echo "Metrics Server no se encuentra en ejecución."
sleep 2

# ================================================
# 10. Verificación final del clúster
# ================================================
echo "[RESULTADO] Estado del clúster tras reinicialización:"
kubectl get nodes

# ================================================
# Finalización
# ================================================
echo "[FIN] Clúster Kubernetes reinicializado correctamente."
