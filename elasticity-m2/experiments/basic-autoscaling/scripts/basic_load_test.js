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
// CARGA DE CONFIGURACIÓN EXTERNA DESDE UN ARCHIVO JSON
// ------------------------------------------------------------------------------
const config = JSON.parse(open('k6_configs/config.json')); 

// ------------------------------------------------------------------------------
// CONFIGURACIÓN DE LA PRUEBA DE CARGA
// stages: define cómo evoluciona la carga (usuarios virtuales) a lo largo del tiempo
// ------------------------------------------------------------------------------
export let options = {
  stages: config.stages,
  thresholds: config.thresholds,
};

// ------------------------------------------------------------------------------
// FUNCIÓN PRINCIPAL
// Se ejecuta una vez por iteración de cada usuario virtual
// ------------------------------------------------------------------------------
export default function () {
  // Realiza una petición HTTP GET al servicio expuesto en el clúster
  // NOTA: Reemplaza '<IP_DEL_CLUSTER>' con la IP externa del nodo Kubernetes
  http.get('http://10.195.20.20:30080/compute?n=20');

  // Pausa entre solicitudes, simulando comportamiento real de un usuario
  sleep(1);
}
