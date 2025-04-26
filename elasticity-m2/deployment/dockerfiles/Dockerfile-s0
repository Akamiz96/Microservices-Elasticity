# Dockerfile-s0
FROM python:3.10-slim

WORKDIR /app

# Copia el código de s0
COPY ../code/service-s0.py .

# Instala Flask
RUN pip install --no-cache-dir flask

# Expone el puerto en el que corre s0
EXPOSE 5000

# Punto de entrada
CMD ["python", "service-s0.py"]
