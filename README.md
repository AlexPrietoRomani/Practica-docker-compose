# Practica-docker-compose
 
## Instrucciones de Uso

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/AlexPrietoRomani/Practica-docker-compose.git
   cd Practica-docker-compose
   ```

2. Crear un archivo `.env` con las siguientes variables:
   ```bash
   AIRFLOW_IMAGE_NAME=apache/airflow:2.10.2
   AIRFLOW_UID=50000
   ```

3. Ejecutar Docker Compose:
   ```bash
   docker-compose up --build
   ```
