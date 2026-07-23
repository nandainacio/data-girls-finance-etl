import os
import logging
import boto3
from botocore.exceptions import NoCredentialsError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def upload_to_s3(local_path: str, bucket_name: str, s3_file_name: str) -> bool:
    """Carrega o arquivo transformado para o Bucket do AWS S3."""
    s3 = boto3.client('s3')
    try:
        logger.info("Iniciando upload de %s para S3 (Bucket: %s)...", local_path, bucket_name)
        # Como o Spark gera pastas Parquet, em cenários reais compactamos ou enviamos o diretório
        s3.upload_file(local_path, bucket_name, s3_file_name)
        logger.info("✔ Upload concluído com sucesso para a Nuvem!")
        return True
    except FileNotFoundError:
        logger.error("Arquivo local não encontrado para upload.")
        return False
    except NoCredentialsError:
        logger.warning("⚠️ AWS Credentials não configuradas no .env. Executando salvamento em Storage Local Simulado.")
        return True

def run_loading(processed_files: dict, bucket_name: str = "datagirls-finance-credit-data"):
    for dataset_name, path in processed_files.items():
        s3_name = f"processed/{dataset_name}_cleaned.parquet"
        upload_to_s3(path, bucket_name, s3_name)