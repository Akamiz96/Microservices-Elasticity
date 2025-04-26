#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------
# Script: exp0_test-deployment.sh
# Descripción: Construye la imagen de service-s0,
# importa en containerd, despliega NGINX + s0,
# verifica la comunicación y limpia al final.
# Ubicación: raíz de elasticity-m2/
# -------------------------------------------------

# Variables
NAMESPACE="elasticity-m2"
IMAGE="service-s0:latest"
DOCKERFILE="deployment/dockerfiles/Dockerfile-s0"
CONTEXT_DIR="deployment"
DEPLOY_DIR="deployment/app"

echo -e "\n=== 0. ELIMINANDO DESPLIEGUE ANTERIOR ==="
echo "➜ kubectl delete -n ${NAMESPACE} -f ${DEPLOY_DIR}/ --ignore-not-found"
kubectl delete -n "${NAMESPACE}" -f "${DEPLOY_DIR}/" --ignore-not-found

echo -e "\n=== 1. CONSTRUYENDO IMAGEN Docker ==="
echo "➜ docker build -f ${DOCKERFILE} -t ${IMAGE} ${CONTEXT_DIR}/"
docker build -f "${DOCKERFILE}" -t "${IMAGE}" "${CONTEXT_DIR}/"

echo -e "\n=== 2. IMPORTANDO IMAGEN EN containerd ==="
echo "➜ docker save ${IMAGE} | sudo ctr -n k8s.io images import -"
docker save "${IMAGE}" | sudo ctr -n k8s.io images import -

echo -e "\n=== 3. CREANDO NAMESPACE SI NO EXISTE ==="
echo "➜ kubectl get namespace ${NAMESPACE}"
if ! kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1; then
  echo "kubectl create namespace ${NAMESPACE}"
  kubectl create namespace "${NAMESPACE}"
else
  echo "Namespace '${NAMESPACE}' ya existe"
fi

echo -e "\n=== 4. DESPLEGANDO MANIFIESTOS ==="
echo "➜ kubectl apply -n ${NAMESPACE} -f ${DEPLOY_DIR}/"
kubectl apply -n "${NAMESPACE}" -f "${DEPLOY_DIR}/"

echo -e "\n=== 5. ESPERANDO ROLLOUT DE LOS DEPLOYMENTS ==="
echo "➜ kubectl -n ${NAMESPACE} rollout status deployment/service-s0"
kubectl -n "${NAMESPACE}" rollout status deployment/service-s0
echo "➜ kubectl -n ${NAMESPACE} rollout status deployment/nginx-gateway"
kubectl -n "${NAMESPACE}" rollout status deployment/nginx-gateway

echo -e "\n=== 6. LISTANDO PODS Y SERVICES ==="
echo "➜ kubectl get pods -n ${NAMESPACE}"
kubectl get pods -n "${NAMESPACE}"
echo -e "\n➜ kubectl get svc -n ${NAMESPACE}"
kubectl get svc -n "${NAMESPACE}"

echo -e "\n=== 7. PROBANDO COMUNICACIÓN A TRAVÉS DE NGINX ==="
echo "➜ kubectl port-forward -n ${NAMESPACE} svc/nginx-gateway 8080:80 &"
kubectl port-forward -n "${NAMESPACE}" svc/nginx-gateway 8080:80 >/dev/null 2>&1 &
PF_PID=$!
sleep 5

echo "➜ curl -s http://localhost:8080/compute?n=10"
curl -s "http://localhost:8080/compute?n=10"

echo -e "\nTerminando port-forward (PID=${PF_PID})"
kill "${PF_PID}"

echo -e "\n=== 8. LIMPIANDO DESPLIEGUE FINAL ==="
echo "➜ kubectl delete -n ${NAMESPACE} -f ${DEPLOY_DIR}/ --ignore-not-found"
kubectl delete -n "${NAMESPACE}" -f "${DEPLOY_DIR}/" --ignore-not-found

echo -e "\n=== 🎉 DESPLIEGUE Y PRUEBA COMPLETADOS CON ÉXITO 🎉 ===\n"
