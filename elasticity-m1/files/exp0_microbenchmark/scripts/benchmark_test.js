// ------------------------------------------------------------------------------
// ARCHIVO: benchmark_test.js
// DESCRIPCIÓN: Script de carga para la herramienta k6, diseñado para generar
//              una carga constante y controlada sobre un servicio NGINX
//              desplegado en Kubernetes. Este script sirve como microbenchmark
//              para estimar el consumo promedio de CPU por usuario virtual o
//              por petición HTTP.
//
// AUTOR: Alejandro Castro Martínez
// FECHA DE MODIFICACIÓN: 27 de marzo de 2025
// CONTEXTO:
//   - Utilizado como referencia para calcular la "resource demand" aproximada.
//   - Permite derivar una equivalencia entre carga generada (VUs/RPS) y consumo real (millicores).
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
  // Realiza una petición HTTP GET al servicio expuesto en el clúster
  // NOTA: Reemplaza '<IP_DEL_CLUSTER>' con la IP del nodo o la IP externa real del servicio
  http.get('http://10.195.20.20:30080');

  // Simula una pausa entre solicitudes, imitando un usuario real
  sleep(1);
}
