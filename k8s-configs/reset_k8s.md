# Reinicio Completo del Clúster Kubernetes

Este documento detalla los pasos necesarios para **borrar completamente un clúster Kubernetes** y **volver a montarlo desde cero** utilizando `kubeadm`.

## 📌 Advertencia
**Este proceso eliminará todo el clúster Kubernetes, incluyendo nodos, configuraciones y datos persistentes.** Solo realízalo si deseas resetear completamente tu entorno.

---

## 🚀 Paso 1: Eliminar el Clúster con kubeadm

Ejecuta el siguiente comando en el nodo **maestro** para resetear la configuración de Kubernetes:
```bash
sudo kubeadm reset
```
Este comando eliminará la configuración del clúster, pero **no eliminará los paquetes de Kubernetes ni las configuraciones en los nodos trabajadores**.

Si deseas omitir la confirmación interactiva, usa:
```bash
sudo kubeadm reset -f
```

## 🔥 Paso 2: Limpiar Configuración del Usuario
Elimina la configuración de `kubectl` para evitar problemas al volver a inicializar el clúster:
```bash
rm -rf $HOME/.kube
```

## 🧹 Paso 3: Eliminar Configuraciones en los Nodos Trabajadores
Ejecuta el siguiente comando en **todos los nodos trabajadores** para desconectarlos correctamente:
```bash
sudo kubeadm reset
```

Si `kubeadm reset` no se ejecuta correctamente, también puedes forzar la eliminación de los archivos de configuración:
```bash
sudo rm -rf /etc/kubernetes/ /var/lib/etcd /var/lib/kubelet
sudo systemctl stop kubelet
sudo systemctl disable kubelet
```

## 🔧 Paso 4: Desinstalar Kubernetes (Opcional)
Si deseas eliminar por completo Kubernetes de los nodos:
```bash
sudo apt-get remove --purge -y kubeadm kubectl kubelet
sudo apt-get autoremove -y
```
También elimina cualquier directorio residual:
```bash
sudo rm -rf /etc/kubernetes /var/lib/kubelet /var/lib/etcd /root/.kube
```

## 📡 Paso 5: Reiniciar la Instalación de Kubernetes
Si deseas reinstalar Kubernetes desde cero, sigue los pasos del archivo `setup.md` para configurar el clúster nuevamente:

### 1️⃣ Instalar Kubernetes
```bash
sudo apt update && sudo apt install -y kubeadm kubelet kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

### 2️⃣ Inicializar el Clúster en el Nodo Maestro
```bash
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```
Después de la inicialización, configura `kubectl`:
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 3️⃣ Configurar la Red del Clúster
Instalar Flannel para gestionar la red entre los pods:
```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```
Verifica que los pods de Flannel estén ejecutándose:
```bash
kubectl get pods -n kube-system
```

### 4️⃣ Unir Nodos Trabajadores al Clúster
Ejecuta el comando generado tras la inicialización en cada nodo trabajador:
```bash
sudo kubeadm join <MAESTRO_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>
```
Verifica que los nodos se han unido correctamente:
```bash
kubectl get nodes
```

## ✅ Conclusión
Siguiendo estos pasos, habrás reseteado completamente el clúster Kubernetes y podrás reinstalarlo sin problemas. 🚀
