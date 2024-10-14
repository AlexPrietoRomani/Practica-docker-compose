# Dockerfile
FROM apache/airflow:2.10.2

# Ejecutar como root para instalar dependencias
USER root

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Volver al usuario airflow para ejecutar Airflow
USER airflow

# Copiar el archivo requirements.txt
COPY requirements.txt /requirements.txt

# Actualizar pip e instalar dependencias desde requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
