// ------------------------------------------------------------------------------
// ARCHIVO: baseline_test.js
// DESCRIPCIÓN: Script de carga para la herramienta k6, diseñado para generar
//              tráfico HTTP en etapas controladas contra un servicio NGINX
//              desplegado en Kubernetes. La prueba simula una carga moderada,
//              estable por un tiempo y luego decreciente para observar el
//              comportamiento del escalado automático (HPA).
//
// AUTOR: Alejandro Castro Martínez
// FECHA DE MODIFICACIÓN: 26 de marzo de 2025
// CONTEXTO:
//   - Utilizado en pruebas de elasticidad en un entorno Kubernetes con HPA activado.
//   - Permite observar cómo se adapta el sistema ante una carga que sube,
//     se mantiene y luego desaparece progresivamente.
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
    { duration: '30s', target: 10 },  // Aumento inicial de carga
    { duration: '1m', target: 10 },   // Carga estable durante 1 minuto
    { duration: '30s', target: 0 },   // Reducción gradual de la carga
  ],
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
