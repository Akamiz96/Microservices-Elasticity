# 📂 Carpeta `manifests/`

Esta carpeta contiene todos los manifiestos necesarios para desplegar y configurar el microservicio NGINX y su autoscalador (HPA) dentro del estudio de elasticidad `nginx-elasticity-study`.

## 📊 Combinaciones generadas por el script

La siguiente tabla resume las configuraciones utilizadas para generar los archivos `C1_hpa.yaml` a `C9_hpa.yaml`:

| ID  | `minReplicas` | `maxReplicas` | `averageUtilization` | Descripción breve                          |
|-----|----------------|----------------|------------------------|--------------------------------------------|
| C1  | 1              | 1              | 5                      | Sin elasticidad, reacción muy rápida       |
| C2  | 1              | 1              | 50                     | Sin elasticidad, sensibilidad media        |
| C3  | 1              | 1              | 100                    | Sin elasticidad, muy conservador           |
| C4  | 1              | 5              | 5                      | Elasticidad media, reacción rápida         |
| C5  | 1              | 5              | 50                     | Elasticidad media, sensibilidad equilibrada|
| C6  | 1              | 5              | 100                    | Elasticidad media, conservadora            |
| C7  | 1              | 100            | 5                      | Elasticidad máxima, reacción muy rápida    |
| C8  | 1              | 100            | 50                     | Elasticidad máxima, equilibrada            |
| C9  | 1              | 100            | 100                    | Elasticidad máxima, reacción muy conservadora |

---

## 🧱 Estructura del directorio

```
manifests/
├── base/                 # Plantillas base con placeholders para generar manifiestos
│   └── hpa_template.yaml
├── generated/            # Archivos YAML generados automáticamente (C1_hpa.yaml, ..., C9_hpa.yaml)
├── nginx-deployment.yaml # Manifiesto del Deployment y Service de NGINX (estático)
└── generate_hpa_yamls.py # Script para generar los HPA a partir de la plantilla
```

---

## 📄 `nginx-deployment.yaml`

Este manifiesto define:

- Un `Deployment` para correr una instancia de NGINX con recursos controlados.
- Un `Service` tipo `NodePort` para exponer el microservicio a pruebas de carga externas.

El número de réplicas será controlado dinámicamente por el HPA.

---

## 📄 `base/hpa_template.yaml`

Archivo plantilla que contiene los siguientes **placeholders**:

- `__MIN_REPLICAS__`: mínimo de réplicas permitidas.
- `__MAX_REPLICAS__`: máximo de réplicas permitidas.
- `__TARGET_CPU__`: porcentaje de uso de CPU que activa el escalamiento.

Fragmento ejemplo del template:

```yaml
minReplicas: __MIN_REPLICAS__
maxReplicas: __MAX_REPLICAS__
averageUtilization: __TARGET_CPU__
```

---

## ⚙️ `generate_hpa_yamls.py`

Script que genera automáticamente 9 archivos YAML (`C1_hpa.yaml` a `C9_hpa.yaml`) para distintas combinaciones de:

- `minReplicas`
- `maxReplicas`
- `averageUtilization`

Estas combinaciones corresponden a un diseño factorial \(3^2 = 9\) para el análisis experimental.

### 🔸 Cómo ejecutar

Desde la raíz del repositorio o desde dentro de `manifests/`, ejecutar:

```bash
cd manifests/
python generate_hpa_yamls.py
```

Esto generará los manifiestos en la carpeta `generated/`, por ejemplo:

```
generated/
├── C1_hpa.yaml   # min=1, max=1, target=5
├── C2_hpa.yaml   # ...
└── C9_hpa.yaml   # min=1, max=100, target=100
```

### 🔍 Fragmento del script

```python
combinations = {
    "C1": (1, 1, 5),
    "C5": (1, 5, 50),
    "C9": (1, 100, 100),
}
```

El script lee `base/hpa_template.yaml`, reemplaza los valores y guarda los archivos listos para desplegar.

---

## 📌 Recomendación de uso del script

1. Asegurarse de tener el archivo `hpa_template.yaml` en la carpeta `base/`.
2. Ejecutar el script para generar los manifiestos:

```bash
python generate_hpa_yamls.py
```

3. Verificar que los archivos `C1_hpa.yaml` a `C9_hpa.yaml` se hayan generado en la carpeta `generated/`.

---

