// ------------------------------------------------------------------------------
// ARCHIVO: test.js
// DESCRIPCIÓN: Script de carga para la herramienta k6, diseñado para generar
//              tráfico HTTP progresivo contra un servicio NGINX desplegado en Kubernetes.
//              La prueba simula aumentos y reducciones de carga para evaluar el
//              comportamiento del escalado automático (HPA).
//
// AUTOR: Alejandro Castro Martínez
// FECHA DE MODIFICACIÓN: 25 de marzo de 2025
// CONTEXTO:
//   - Utilizado en pruebas de escalabilidad horizontal con HPA en Kubernetes.
//   - Se recomienda ejecutarlo mientras se recolectan métricas de uso de CPU y número de pods.
//   - El servicio debe estar expuesto a través de un NodePort accesible desde el host.
// ------------------------------------------------------------------------------

import http from 'k6/http';   // Módulo para realizar solicitudes HTTP
import { sleep } from 'k6';   // Módulo para simular tiempo de espera entre solicitudes

// ------------------------------------------------------------------------------
// CONFIGURACIÓN DE LA PRUEBA DE CARGA
// stages: define cómo evoluciona la carga (usuarios virtuales) a lo largo del tiempo
// thresholds: define criterios de éxito (rendimiento mínimo aceptable)
// ------------------------------------------------------------------------------
export let options = {
  stages: [
    { duration: '1m', target: 50 },   // Calentamiento inicial
    { duration: '2m', target: 150 },  // Aumento rápido de carga
    { duration: '3m', target: 300 },  // Carga máxima durante 3 minutos
    { duration: '2m', target: 50 },   // Reducción de carga
    { duration: '2m', target: 0 },    // Descenso completo
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // El 95% de las solicitudes deben completarse en menos de 500 ms
    http_req_failed: ['rate<0.01'],   // Menos del 1% de las solicitudes deben fallar
  },
};

// ------------------------------------------------------------------------------
// FUNCIÓN PRINCIPAL
// Se ejecuta una vez por iteración de cada usuario virtual
// ------------------------------------------------------------------------------
export default function () {
  // Realiza una petición HTTP GET al servicio expuesto en el clúster
  // NOTA: Reemplaza '<IP_DEL_CLUSTER>' con la IP del nodo o la IP externa real del servicio
  http.get('http://<IP_DEL_CLUSTER>:30080');

  // Simula una pausa entre solicitudes, imitando un usuario real
  sleep(1);
}
