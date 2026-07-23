import logging
from src.extract import extract_data
from src.transform import run_transformation
from src.load import run_loading

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("🏁 Iniciando execução automatizada do Pipeline ETL - Data Girls Finance")
    
    # Passo 1: Extração (Ingestion)
    raw_paths = extract_data(output_path="data/raw")
    
    # Passo 2: Transformação (Processing com PySpark)
    processed_paths = run_transformation(input_paths=raw_paths, output_base_path="data/processed")
    
    # Passo 3: Carga (Cloud Storage Load)
    run_loading(processed_files=processed_paths)
    
    logger.info("🏆 Pipeline concluído com sucesso total! Dados prontos para Analytics.")

if __name__ == "__main__":
    main()