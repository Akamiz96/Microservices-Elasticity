# ------------------------------------------------------------------------------
# ARCHIVO: generate_hpa_yamls.py
# DESCRIPCIÓN: Script para generar automáticamente los manifiestos HPA en YAML
#              para 9 combinaciones experimentales de elasticidad, usando una
#              plantilla base con marcadores reemplazables.
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 08 de abril de 2025
# CONTEXTO:
#   - Este script debe ubicarse dentro de la carpeta `manifests/`.
#   - Utilizado en el estudio `nginx-elasticity-study` para generar automáticamente
#     los manifiestos `HorizontalPodAutoscaler` para cada combinación experimental (C1 a C9).
#   - Facilita la creación de variantes del HPA ajustando:
#       * minReplicas
#       * maxReplicas
#       * averageUtilization (target de CPU)
# ------------------------------------------------------------------------------

import os

# ---------------------------------------------------------------
# DEFINICIÓN DE COMBINACIONES EXPERIMENTALES
# Cada clave representa un caso (C1 a C9) con los parámetros:
# (minReplicas, maxReplicas, averageUtilization)
# ---------------------------------------------------------------
combinations = {
    "C1": (1, 1, 5),
    "C2": (1, 1, 50),
    "C3": (1, 1, 100),
    "C4": (1, 5, 5),
    "C5": (1, 5, 50),
    "C6": (1, 5, 100),
    "C7": (1, 100, 5),
    "C8": (1, 100, 50),
    "C9": (1, 100, 100),
}

# ---------------------------------------------------------------
# RUTAS RELATIVAS (considerando que este script está en `manifests/`)
# ---------------------------------------------------------------
TEMPLATE_PATH = "base/hpa_template.yaml"     # Plantilla base con placeholders
OUTPUT_DIR = "generated"                     # Carpeta donde se almacenan los YAML generados

# Crea la carpeta de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------
# LECTURA DEL ARCHIVO DE PLANTILLA
# ---------------------------------------------------------------
with open(TEMPLATE_PATH, "r") as file:
    template_content = file.read()

# ---------------------------------------------------------------
# GENERACIÓN DE ARCHIVOS PERSONALIZADOS PARA CADA COMBINACIÓN
# ---------------------------------------------------------------
for case_id, (min_r, max_r, target_cpu) in combinations.items():
    # Reemplazo de los marcadores dentro del contenido de la plantilla
    hpa_yaml = (
        template_content
        .replace("__MIN_REPLICAS__", str(min_r))
        .replace("__MAX_REPLICAS__", str(max_r))
        .replace("__TARGET_CPU__", str(target_cpu))
    )

    # Ruta del archivo de salida
    output_path = os.path.join(OUTPUT_DIR, f"{case_id}_hpa.yaml")

    # Escritura del archivo generado
    with open(output_path, "w") as f:
        f.write(hpa_yaml)

    print(f"✔️ Archivo generado: {output_path}")

# ---------------------------------------------------------------
# FIN DEL SCRIPT
# ---------------------------------------------------------------
