# 📂 Carpeta `scripts/`

Esta carpeta contiene los scripts utilizados para:

- Capturar eventos de escalamiento y uso de recursos durante la ejecución del experimento.
- Configurar distintos patrones de carga para el generador K6, los cuales son utilizados como variable experimental dentro del estudio `nginx-elasticity-study`.

La subcarpeta `k6_configs/` incluye múltiples archivos `config.json`, cada uno correspondiente a un patrón de carga específico.

---

## 📁 Archivos de configuración de carga (`k6_configs/`)

Cada archivo `LXX_config.json` define un escenario de carga mediante una serie de etapas (`stages`) que representan la evolución de usuarios virtuales (VUs) a lo largo del tiempo. Estos patrones están diseñados para inducir diferentes comportamientos en el escalamiento automático del microservicio NGINX.

Además de los `stages`, cada archivo define un conjunto de `thresholds` que establecen condiciones mínimas de calidad de servicio, tales como latencia y tasa de errores permitida.

A continuación, se detallan los 6 patrones definidos:

| ID   | Archivo                     | Descripción técnica                                                                 |
|------|-----------------------------|-------------------------------------------------------------------------------------|
| L01  | [L01_config.json](k6_configs/L01_config.json) | Carga baja controlada, útil como línea base para comparación experimental.         |
| L02  | [L02_config.json](k6_configs/L02_config.json) | Escalamiento en pasos con cargas altas, permite evaluar reacción progresiva.       |
| L03  | [L03_config.json](k6_configs/L03_config.json) | Pico repentino de carga seguido de una bajada abrupta, prueba de sensibilidad.     |
| L04  | [L04_config.json](k6_configs/L04_config.json) | Ondas de carga alternante, evalúa estabilidad frente a cambios frecuentes.         |
| L05  | [L05_config.json](k6_configs/L05_config.json) | Carga alta sostenida, mide comportamiento bajo presión prolongada.                 |
| L06  | [L06_config.json](k6_configs/L06_config.json) | Patrón tipo montaña: subida gradual y descenso rápido, simula escenarios reales.   |

Estos patrones se seleccionaron cuidadosamente para representar una diversidad de condiciones que permiten observar diferentes respuestas de elasticidad. Su correcta ejecución permite analizar tanto el escalamiento vertical como el desescalamiento en función del comportamiento de la carga.

---

# 📄 Script de carga genérico: `load_test_runner.js`

Este archivo contiene el script genérico para ejecutar pruebas de carga con K6 dentro del estudio `nginx-elasticity-study`. Su objetivo es facilitar la reutilización del código permitiendo seleccionar dinámicamente diferentes patrones de carga definidos en archivos de configuración JSON externos.

---

## 🧩 Descripción general del funcionamiento

El script está diseñado para ser utilizado sin necesidad de edición manual entre pruebas. La carga se configura mediante una variable de entorno llamada `K6_CONF`, que apunta al archivo de configuración deseado dentro de la carpeta `k6_configs/`.

Si no se proporciona esta variable, el script utiliza por defecto `L01_config.json`.

---

## 🔍 Explicación del código `load_test_runner.js`

```javascript
import http from 'k6/http';    // Importa el módulo de K6 para enviar solicitudes HTTP
import { sleep } from 'k6';    // Importa la función sleep para simular pausas entre iteraciones

// LECTURA DEL NOMBRE DEL ARCHIVO DE CONFIGURACIÓN
// Usa la variable de entorno K6_CONF, o un valor por defecto si no se define
const configFile = __ENV.K6_CONF || 'k6_configs/L01_config.json';

// CARGA DE PARÁMETROS EXPERIMENTALES DESDE ARCHIVO JSON
// El archivo contiene los 'stages' (evolución de la carga) y 'thresholds' (condiciones mínimas)
const config = JSON.parse(open(configFile));

// CONFIGURACIÓN DEL EXPERIMENTO
// Se pasan los valores obtenidos desde el archivo al bloque de opciones de K6
export let options = {
  stages: config.stages,
  thresholds: config.thresholds,
};

// FUNCIÓN QUE EJECUTA LA CARGA POR CADA USUARIO VIRTUAL
// Cada VU ejecuta esta función una vez por iteración
export default function () {
  http.get('http://10.195.20.20:30080');  // Enviar una solicitud HTTP al servicio NGINX
  sleep(1);                               // Espera de 1 segundo entre iteraciones
}
```

---

## 🧪 Ejemplo de ejecución

```bash
K6_CONF=k6_configs/L04_config.json k6 run load_test_runner.js
```

Este comando ejecutará el patrón de carga definido en el archivo `L04_config.json`, permitiendo evaluar la elasticidad del microservicio frente a una carga ondulante intensa.

---

## 📊 Recolección de métricas: `metric_collector_basic.sh`

Este script se encarga de recolectar métricas de uso de CPU y memoria de los pods del deployment `nginx-basic` durante la ejecución de un experimento de elasticidad.

- Requiere dos parámetros: el ID del HPA (`C1` a `C9`) y el ID del patrón de carga (`L01` a `L06`).
- Ejecuta un muestreo cada 10 segundos utilizando `kubectl top`.
- Calcula el porcentaje de uso de CPU en relación con el valor solicitado (`resources.requests.cpu`).
- Guarda los resultados en el archivo:

```
nginx-elasticity-study/output/HPA_CX_LOAD_LYY_metrics.csv
```

📌 **Ejemplo de uso**:
```bash
./metric_collector_basic.sh C3 L05
```

---

## 📋 Captura de eventos: `capture_deployment_events.sh`

Este script guarda en un log plano todos los eventos generados por el deployment `nginx-basic` en Kubernetes, registrando cada línea con un timestamp real del sistema.

- Requiere dos parámetros: el ID del HPA (`C1` a `C9`) y el ID del patrón de carga (`L01` a `L06`).
- Extrae eventos usando `kubectl get events` y filtra por el nombre del deployment.
- El archivo resultante puede ser procesado posteriormente para extraer eventos de escalamiento u otros relevantes.

Guarda los eventos en:

```
nginx-elasticity-study/output/HPA_CX_LOAD_LYY_events.log
```

📌 **Ejemplo de uso**:
```bash
./capture_deployment_events.sh C3 L05
```

---


