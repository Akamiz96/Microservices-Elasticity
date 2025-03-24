# Reinicio Completo del Clúster Kubernetes

Este documento detalla los pasos necesarios para **borrar completamente un clúster Kubernetes** y **volver a montarlo desde cero** utilizando `kubeadm`.

## 📌 Advertencia
**Este proceso eliminará todo el clúster Kubernetes, incluyendo nodos, configuraciones y datos persistentes.** Solo realízalo si deseas resetear completamente tu entorno.

---

## 🔁 Paso 1: Eliminar el Clúster con kubeadm

### 1.1 Ejecutar el reset en el nodo maestro
```bash
sudo kubeadm reset
```

### 1.2 Ejecutar sin confirmación interactiva
```bash
sudo kubeadm reset -f
```

---

## 🧹 Paso 2: Limpiar Configuración del Usuario

### 2.1 Eliminar configuración local de `kubectl`
```bash
rm -rf $HOME/.kube
```

---

## 🖥️ Paso 3: Limpiar Configuraciones en Nodos Trabajadores

### 3.1 Reset con kubeadm
```bash
sudo kubeadm reset
```

### 3.2 Eliminación forzada de archivos (opcional)
```bash
sudo rm -rf /etc/kubernetes/ /var/lib/etcd /var/lib/kubelet
sudo systemctl stop kubelet
sudo systemctl disable kubelet
```

---

## ❌ Paso 4: Desinstalar Kubernetes (Opcional)

### 4.1 Eliminar paquetes
```bash
sudo apt-get remove --purge -y kubeadm kubectl kubelet
sudo apt-get autoremove -y
```

### 4.2 Eliminar directorios residuales
```bash
sudo rm -rf /etc/kubernetes /var/lib/kubelet /var/lib/etcd /root/.kube
```

---

## 🔧 Paso 5: Reiniciar la Instalación de Kubernetes

### 5.1 Instalar Kubernetes
```bash
sudo apt update && sudo apt install -y kubeadm kubelet kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

### 5.2 Inicializar el Clúster en el Nodo Maestro
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

### 5.3 Configurar kubectl
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 5.4 Instalar Flannel
```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

### 5.5 Verificar Flannel
```bash
kubectl get pods -n kube-system
```

---

## 📊 Paso 6: Instalación del Metrics Server

### 6.1 Verificar si HPA recolecta métricas
```bash
kubectl get hpa
```

### 6.2 Instalar el Metrics Server
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 6.3 Habilitar `--kubelet-insecure-tls`
```bash
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-", "value":"--kubelet-insecure-tls"}]'
```

### 6.4 Verificar que el Metrics Server esté en ejecución
```bash
kubectl get pods -n kube-system | grep metrics-server
```

---

## 🔗 Paso 7: Unir Nodos Trabajadores al Clúster

### 7.1 Ejecutar el join
```bash
sudo kubeadm join <MAESTRO_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>
```

### 7.2 Verificar los nodos
```bash
kubectl get nodes
```

---

## ✅ Conclusión

Siguiendo estos pasos, habrás reseteado completamente el clúster Kubernetes y podrás reinstalarlo sin problemas.
