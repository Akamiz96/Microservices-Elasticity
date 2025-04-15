// ------------------------------------------------------------------------------
// ARCHIVO: load_test_runner.js
// DESCRIPCIÓN: Script genérico de carga para la herramienta k6. Permite ejecutar
//              distintos patrones de prueba especificando el archivo de configuración
//              por parámetro (variable de entorno K6_CONF).
//
// AUTOR: Alejandro Castro Martínez
// FECHA DE MODIFICACIÓN: 08 de abril de 2025
// CONTEXTO:
//   - Utilizado en el estudio `nginx-elasticity-study`.
//   - Facilita la ejecución flexible de múltiples cargas definidas en archivos JSON.
//   - Cada archivo de configuración se encuentra en `k6_configs/LXX_config.json`.
// ------------------------------------------------------------------------------

import http from 'k6/http';    // Módulo para solicitudes HTTP
import { sleep } from 'k6';    // Simulación de espera entre iteraciones

// ------------------------------------------------------------------------------
// LECTURA DEL NOMBRE DE CONFIGURACIÓN DESDE VARIABLE DE ENTORNO
// ------------------------------------------------------------------------------
const configFile = __ENV.K6_CONF || 'k6_configs/L01_config.json'; // Valor por defecto

// ------------------------------------------------------------------------------
// CARGA DE CONFIGURACIÓN DESDE ARCHIVO JSON
// ------------------------------------------------------------------------------
const config = JSON.parse(open(configFile));

// ------------------------------------------------------------------------------
// OPCIONES DE CARGA DINÁMICAS
// ------------------------------------------------------------------------------
export let options = {
  stages: config.stages,
  thresholds: config.thresholds,
};

// ------------------------------------------------------------------------------
// FUNCIÓN PRINCIPAL
// ------------------------------------------------------------------------------
export default function () {
    // Realiza una petición HTTP GET al servicio expuesto en el clúster
    // NOTA: Reemplaza '<IP_DEL_CLUSTER>' con la IP externa del nodo Kubernetes
    http.get('http://10.195.20.20:30080');  // Reemplazar IP si es necesario
    
    // Pausa entre solicitudes, simulando comportamiento real de un usuario
    sleep(1);
}
