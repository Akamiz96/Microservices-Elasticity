// Este script es usado por k6 para generar una carga HTTP controlada
// contra el servicio nginx desplegado en el clúster Kubernetes.

// ---------------------------------------------------------------
// CONFIGURACIÓN DE ESCENARIOS
// ---------------------------------------------------------------
export let options = {
    stages: [
        { duration: '30s', target: 50 },   // Subida gradual a 50 usuarios
        { duration: '1m', target: 200 },   // Mantener 200 usuarios durante 1 minuto
        { duration: '2m', target: 500 },   // Pico de carga con 500 usuarios durante 2 minutos
        { duration: '30s', target: 0 }     // Descenso gradual hasta 0
    ],
};

// ---------------------------------------------------------------
// FUNCIÓN PRINCIPAL DE PRUEBA
// ---------------------------------------------------------------
export default function () {
    // IMPORTANTE: reemplaza <IP_DEL_CLUSTER> con la IP externa del nodo Kubernetes
    // que esté exponiendo el puerto 30080 (servicio NodePort)
    http.get('http://<IP_DEL_CLUSTER>:30080'); // Solicitud HTTP GET a la app nginx
    sleep(1);                                  // Tiempo de espera de 1 segundo entre solicitudes
}

import http from 'k6/http';
import { sleep } from 'k6';
