# dmc_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import os
import json
import zipfile
import pandas as pd
import subprocess
from ml import MLSystem

# Función para cargar las credenciales de Kaggle desde el archivo JSON
def load_kaggle_credentials():
    with open('/opt/airflow/dags/kaggle.json', 'r') as f:
        kaggle_creds = json.load(f)
    os.environ['KAGGLE_USERNAME'] = kaggle_creds['username']
    os.environ['KAGGLE_KEY'] = kaggle_creds['key']

# Definimos el DAG y sus argumentos
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_pipeline_with_MLSystem',
    default_args=default_args,
    description='Pipeline ML con MLSystem y pruebas unitarias',
    schedule_interval=timedelta(days=1),
)

# Función para descargar y descomprimir los archivos de la competición de Kaggle
def download_data():
    load_kaggle_credentials()
    competition_name = 'playground-series-s4e10'
    download_path = '/opt/airflow/dags/data/'
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    api.competition_download_files(competition_name, path=download_path)
    for item in os.listdir(download_path):
        if item.endswith('.zip'):
            with zipfile.ZipFile(os.path.join(download_path, item), 'r') as zip_ref:
                zip_ref.extractall(download_path)
                print(f"Unzipped {item}")

# Función para entrenar el modelo usando la clase MLSystem de ml.py
def train_with_ml_system():
    ml_system = MLSystem()
    data_path = '/opt/airflow/dags/data/train.csv'
    
    # Cargar y preprocesar los datos
    data = ml_system.load_data(data_path)
    X_train, X_test, y_train, y_test = ml_system.preprocess_data(data, target_column='loan_status')
    
    # Entrenar el modelo
    ml_system.train(X_train, y_train)
    
    # Evaluar el modelo
    accuracy = ml_system.evaluate(X_test, y_test)
    ml_system.save_model('/opt/airflow/dags/data/best_model.joblib')

    return accuracy

# Función para ejecutar las pruebas unitarias de test.py
def run_tests():
    result = subprocess.run(['pytest', '/opt/airflow/dags/ml/test.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception("Test failed")

# Función para subir los resultados a Kaggle
def submit_kaggle():
    load_kaggle_credentials()
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    submission_file = '/opt/airflow/dags/data/submission.csv'
    competition_name = 'playground-series-s4e10'
    api.competition_submit(file_name=submission_file,
                            message="Submission with MLSystem",
                            competition=competition_name)

# Tarea para verificar que PostgreSQL esté disponible
check_postgres = PostgresOperator(
    task_id='check_postgres',
    postgres_conn_id='airflow_db',  # ID de conexión para PostgreSQL en Airflow
    sql='SELECT 1;',  # Consulta simple para verificar la conexión
    dag=dag,
)

# Definición de las tareas del DAG
task_get_data = PythonOperator(
    task_id='GetDataKaggle',
    python_callable=download_data,
    dag=dag,
)

task_train_model = PythonOperator(
    task_id='TrainModelWithMLSystem',
    python_callable=train_with_ml_system,
    dag=dag,
)

task_run_tests = PythonOperator(
    task_id='RunTests',
    python_callable=run_tests,
    dag=dag,
)

task_submit_kaggle = PythonOperator(
    task_id='SubmitKaggle',
    python_callable=submit_kaggle,
    dag=dag,
)

# Definir el flujo de tareas
check_postgres >> task_get_data >> task_train_model >> task_run_tests >> task_submit_kaggle
