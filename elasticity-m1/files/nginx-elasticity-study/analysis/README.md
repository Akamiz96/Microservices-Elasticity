# 📂 Carpeta `analysis/`

Esta carpeta contiene todo el procesamiento automatizado que se realiza al final de cada experimento del estudio `exp2_nginx-elasticity-study`. Su propósito es transformar las métricas crudas recolectadas en resultados visuales y métricas cuantitativas de elasticidad.

Incluye:
- Scripts Python para limpieza, análisis, visualización y cálculo de métricas.
- Un `Dockerfile` para ejecutar todo el flujo de análisis de manera automática y aislada.
- Salidas generadas como gráficas (`images/`) y archivos procesados (`files/`).

---

## 🐍 Scripts de análisis incluidos

Los siguientes scripts son ejecutados automáticamente en orden desde el contenedor:

1. `filter_scaling_events.py` — Limpia los eventos de escalamiento para análisis.
2. `plot_cpu_usage.py` — Gráfico base del uso de CPU por pod.
3. `plot_cpu_usage_with_events.py` — Gráfico de CPU incluyendo líneas verticales para eventos.
4. `plot_pod_count.py` — Evolución del número de pods durante la prueba.
5. `plot_pod_count_with_events.py` — Evolución de pods con líneas de escalamiento.
6. `plot_elasticity_curve.py` — Curva de elasticidad basada en la demanda.
7. `plot_elasticity_curve_with_events.py` — Curva de elasticidad con eventos superpuestos.
8. `plot_indirect_elasticity_metrics.py` — Métricas indirectas como errores o latencia.
9. `calculate_elasticity_metrics.py` — Cálculo cuantitativo de métricas como precisión de escalamiento y elasticidad.

Todos los scripts deben estar ubicados en la raíz del contenedor (por eso se copian desde la carpeta `code/`).

---

## 🐳 Ejecución con Docker

El `Dockerfile` está preparado para aceptar dos variables de entorno:

- `HPA_ID` → Identificador de configuración del HPA (valores como `C1`, `C2`, ... `C9`)
- `LOAD_ID` → Identificador del patrón de carga utilizado (valores como `L01`, ..., `L06`)

Estas variables permiten que los scripts accedan automáticamente a los archivos de entrada correctos y generen salidas etiquetadas.

### 🔧 Ejemplo de ejecución del contenedor:

```bash
docker run \
  -e HPA_ID=C5 \
  -e LOAD_ID=L03 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/analysis/images:/app/images \
  -v $(pwd)/analysis/files:/app/files \
  nginx-elasticity-analysis
```

Este comando:
- Usa `C5` como configuración del HPA.
- Usa `L03` como patrón de carga.
- Monta los volúmenes necesarios para que los scripts puedan acceder a los datos y guardar resultados.

---

## 📤 Estructura esperada de salida

- `output/HPAC5_LOADL03_metrics.csv` — Entrada principal de métricas crudas.
- `output/HPAC5_LOADL03_events.log` — Eventos crudos de escalamiento.
- `analysis/images/` — Gráficas generadas por los scripts.
- `analysis/files/` — Archivos CSV, JSON u otros con resultados finales de análisis.

---

Este entorno asegura que todos los análisis se realicen de forma reproducible, limpia y desacoplada del sistema operativo anfitrión.

