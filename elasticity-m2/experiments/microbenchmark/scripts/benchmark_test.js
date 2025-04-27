// ------------------------------------------------------------------------------
// ARCHIVO: benchmark_test.js
// DESCRIPCIÓN: Script de carga para la herramienta k6, diseñado para generar
//              una carga constante y controlada sobre el microservicio NGINX,
//              que redirige las solicitudes a un servicio Flask desplegado en Kubernetes.
//
// AUTOR: Alejandro Castro Martínez
// FECHA DE MODIFICACIÓN: 27 de abril de 2025
// CONTEXTO:
//   - Utilizado para estimar el consumo promedio de CPU por usuario virtual (VU)
//     o por solicitud HTTP en pruebas de elasticidad.
//   - El servicio debe estar expuesto a través de un NodePort accesible desde el host.
// ------------------------------------------------------------------------------

import http from 'k6/http';   // Módulo para realizar solicitudes HTTP
import { sleep } from 'k6';   // Módulo para simular tiempo de espera entre solicitudes

// ------------------------------------------------------------------------------
// CONFIGURACIÓN DE LA PRUEBA DE CARGA
// stages: define cómo evoluciona la carga (usuarios virtuales) a lo largo del tiempo
// ------------------------------------------------------------------------------
export let options = {
  stages: [
    { duration: '1m', target: 10 },   // Carga constante con 10 usuarios virtuales
  ],
};

// ------------------------------------------------------------------------------
// FUNCIÓN PRINCIPAL
// Se ejecuta una vez por iteración de cada usuario virtual
// ------------------------------------------------------------------------------
export default function () {
  // Realiza una petición HTTP GET al servicio NGINX expuesto en el clúster
  // NOTA: Se apunta al endpoint /compute?n=20 que procesa una operación de Fibonacci

  http.get('http://10.195.20.20:30080/compute?n=20');

  // Simula una pausa de 1 segundo entre solicitudes, imitando el comportamiento de un usuario real
  sleep(1);
}
