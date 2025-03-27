// ------------------------------------------------------------------------------
// ARCHIVO: basic_load_test.js
// DESCRIPCIÓN: Script de carga para la herramienta k6, diseñado para generar
//              tráfico HTTP en etapas controladas contra un servicio NGINX
//              desplegado en Kubernetes. La prueba está pensada para inducir
//              comportamiento de escalado y desescalado del HPA.
//
// AUTOR: Alejandro Castro Martínez
// FECHA DE MODIFICACIÓN: 27 de marzo de 2025
// CONTEXTO:
//   - Utilizado en el experimento `exp1_basic-autoscaling`.
//   - El objetivo es observar cómo varía el número de pods con distintas fases
//     de carga sostenida y decreciente.
//   - El servicio NGINX debe estar expuesto a través de un NodePort accesible
//     desde el exterior del clúster.
// ------------------------------------------------------------------------------

import http from 'k6/http';   // Módulo para realizar solicitudes HTTP
import { sleep } from 'k6';   // Módulo para simular tiempo de espera entre solicitudes

// ------------------------------------------------------------------------------
// CONFIGURACIÓN DE LA PRUEBA DE CARGA
// stages: define cómo evoluciona la carga (usuarios virtuales) a lo largo del tiempo
// ------------------------------------------------------------------------------
export let options = {
  stages: [
    { duration: '1m', target: 50 },   // Subida progresiva de carga
    { duration: '3m', target: 150 },  // Carga alta sostenida (debería activar el HPA)
    { duration: '2m', target: 50 },   // Reducción progresiva
    { duration: '1m', target: 0 },    // Descenso total de la carga
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // El 95% de las solicitudes debe responder en < 500 ms
    http_req_failed: ['rate<0.01'],   // Menos del 1% de fallos aceptado
  },
};

// ------------------------------------------------------------------------------
// FUNCIÓN PRINCIPAL
// Se ejecuta una vez por iteración de cada usuario virtual
// ------------------------------------------------------------------------------
export default function () {
  // Realiza una petición HTTP GET al servicio expuesto en el clúster
  // NOTA: Reemplaza '<IP_DEL_CLUSTER>' con la IP externa del nodo Kubernetes
  http.get('http://10.195.20.20:30080');

  // Pausa entre solicitudes, simulando comportamiento real de un usuario
  sleep(1);
}
