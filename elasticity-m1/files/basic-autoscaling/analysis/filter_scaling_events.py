# ------------------------------------------------------------------------------
# ARCHIVO: filter_scaling_events.py
# DESCRIPCIÓN: Limpia el archivo scaling_events.csv eliminando duplicados
#              de eventos de escalado (por timestamp y dirección).
#
# AUTOR: Alejandro Castro Martínez
# FECHA DE MODIFICACIÓN: 28 de marzo de 2025
# CONTEXTO:
#   - Se utiliza para asegurar que solo se marque un escalado por dirección y momento.
#   - Esto mejora la visualización en la curva de elasticidad.
# ------------------------------------------------------------------------------

import pandas as pd
import os

# Ruta del archivo original
input_path = "output/scaling_events.csv"
output_path = "output/scaling_events_clean.csv"

# Cargar los datos
df = pd.read_csv(input_path)

# Convertir timestamp a datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Eliminar duplicados (por timestamp + scaling_direction)
df_clean = df.drop_duplicates(subset=["timestamp", "scaling_direction"])

# Ordenar por tiempo
df_clean = df_clean.sort_values("timestamp")

# Guardar archivo limpio
df_clean.to_csv(output_path, index=False)

print(f"[✔] Eventos limpios guardados en: {output_path}")
