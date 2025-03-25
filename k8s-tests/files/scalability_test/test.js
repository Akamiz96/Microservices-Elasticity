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
        { duration: '30s', target: 50 },   // Subida gradual a 50 usuarios
        { duration: '1m', target: 200 },   // Mantener 200 usuarios durante 1 minuto
        { duration: '2m', target: 500 },   // Pico de carga con 500 usuarios durante 2 minutos
        { duration: '30s', target: 0 }     // Descenso gradual hasta 0
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
