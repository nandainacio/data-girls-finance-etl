import os
import logging
from dotenv import load_dotenv

load_dotenv()
import kaggle

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATASET_SLUG = "parisrohan/credit-score-classification"
EXPECTED_FILES = ["train.csv", "test.csv"]

def extract_data(output_path: str = "data/raw") -> dict:
    os.makedirs(output_path, exist_ok=True)
    logger.info("Autenticando na API do Kaggle...")
    kaggle.api.authenticate()

    logger.info("Baixando dataset '%s'...", DATASET_SLUG)
    kaggle.api.dataset_download_files(DATASET_SLUG, path=output_path, unzip=True)

    file_paths = {}
    for expected_file in EXPECTED_FILES:
        file_path = os.path.join(output_path, expected_file)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            logger.info("✔ %s encontrado (%.1f KB)", expected_file, size_kb)
            file_paths[expected_file.replace(".csv", "")] = file_path
            
    if len(file_paths) < len(EXPECTED_FILES):
        raise FileNotFoundError("Estrutura do dataset divergente do esperado.")
    return file_paths

if __name__ == "__main__":
    extract_data()