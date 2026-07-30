import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.extract import extract_data
from src.load import run_loading
from src.transform import run_transformation

default_args = {
    'owner': 'Data Girls Finance',
    'depends_on_past': False,
    'start_date': datetime(2026, 7, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dag_credit_score_etl',
    default_args=default_args,
    description='Pipeline ETL automatizado de score de crédito usando Polars e AWS S3',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Extração dos dados brutos do Kaggle
    task_extract = PythonOperator(
        task_id='extract_raw_data',
        python_callable=extract_data,
        op_kwargs={'output_path': 'data/raw'},
    )

    # Task 2: Transformação e limpeza com Polars
    def trigger_transformation():
        caminhos_entrada = {
            "train": "data/raw/train.csv",
            "test": "data/raw/test.csv"
        }
        return run_transformation(input_paths=caminhos_entrada, output_base_path="data/processed")

    task_transform = PythonOperator(
        task_id='transform_polars_data',
        python_callable=trigger_transformation,
    )

    # Task 3: Carga dos arquivos Parquet no AWS S3
    def trigger_loading():
        arquivos_processados = {
            "train": "data/processed/train_cleaned.parquet",
            "test": "data/processed/test_cleaned.parquet"
        }
        bucket_env = os.getenv("S3_BUCKET_NAME", "data-girls-credit-score-701799127351-sa-east-1-an")
        return run_loading(processed_files=arquivos_processados, bucket_name=bucket_env)

    task_load = PythonOperator(
        task_id='load_to_s3_parquet',
        python_callable=trigger_loading,
    )

    # Fluxo de execução
    task_extract >> task_transform >> task_load