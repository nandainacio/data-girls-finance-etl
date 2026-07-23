from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Importando as funções que você já escreveu nos seus módulos de src!
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# O Airflow consegue importar os seus scripts se eles estiverem no PYTHONPATH.
from src.extract import extract_data
from src.transform import run_transformation
from src.load import run_loading

# Configurações padrão da DAG
default_args = {
    'owner': 'Data Girls Finance',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 1), # Data de início simulada para o projeto
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definição da DAG com agendamento diário (simulado)
with DAG(
    'dag_credit_score_etl',
    default_args=default_args,
    description='Pipeline ETL automatizado de score de crédito usando PySpark e AWS S3',
    schedule_interval='@daily', # Agendamento simulado periódico
    catchup=False,
) as dag:

    # Task 1: Extração dos dados brutos do Kaggle
    task_extract = PythonOperator(
        task_id='extract_raw_data',
        python_callable=extract_data,
        op_kwargs={'output_path': 'data/raw'},
    )

    # Task 2: Transformação de tipos e limpeza com PySpark
    # Usamos uma função auxiliar que define os caminhos de entrada e executa o transform
    def trigger_transformation():
        caminhos_entrada = {
            "train": "data/raw/train.csv",
            "test": "data/raw/test.csv"
        }
        return run_transformation(input_paths=caminhos_entrada, output_base_path="data/processed")

    task_transform = PythonOperator(
        task_id='transform_pyspark_data',
        python_callable=trigger_transformation,
    )

    # Task 3: Carga dos arquivos limpos (.parquet) no AWS S3
    def trigger_loading():
        arquivos_processados = {
            "train": "data/processed/train_cleaned.parquet",
            "test": "data/processed/test_cleaned.parquet"
        }
        return run_loading(processed_files=arquivos_processados, bucket_name="datagirls-finance-credit-data")

    task_load = PythonOperator(
        task_id='load_to_s3_parquet',
        python_callable=trigger_loading,
    )

    # Definição do fluxo/dependências das Tasks (Orquestração sequencial)
    task_extract >> task_transform >> task_load