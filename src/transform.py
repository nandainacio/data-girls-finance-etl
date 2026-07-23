import os
import logging
from pyspark.sql import DataFrame, SparkSession
import pyspark.sql.functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def iniciar_spark() -> SparkSession:
    return SparkSession.builder \
        .appName("CreditScoreTransformation") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .getOrCreate()

def clean_and_transform(df: DataFrame) -> DataFrame:
    # 1. Elimina duplicidade total de linhas
    df = df.dropDuplicates()


    # 2. Limpeza profunda da coluna 'Age' (somente inteiros válidos)
    colunas_int = ['Age', 'Num_of_Loan', 'Num_of_Delayed_Payment']
    for coluna in colunas_int:
        if coluna in df.columns:
            df = df.withColumn(coluna, F.regexp_replace(F.col(coluna), r"[^0-9]", "").cast("integer"))

    
    # 3. Limpeza de colunas decimais com o Regex de negação protegendo o ponto flutuante
    colunas_double = [
        'Annual_Income','Changed_Credit_Limit', 
        'Outstanding_Debt', 'Amount_invested_monthly', 'Monthly_Balance'
    ]

    for coluna in colunas_double:
        if coluna in df.columns:
            df = df.withColumn(coluna, F.regexp_replace(F.col(coluna), r"[^0-9.]", "").cast("double"))

    # 4. Tratamento de Valores Nulos gerados pelas strings corrompidas
    # Preenche idades nulas ou fora do padrão com a mediana da idade do dataset
    mediana_idade = df.approxQuantile("Age", [0.5], 0.01)[0]
    df = df.fillna({"Age": int(mediana_idade)})
    
    # Demais numéricas nulas são zeradas para não quebrar agregações matemáticas
    df = df.fillna(0, subset=colunas_double)

    return df

def run_transformation(input_paths: dict, output_base_path: str = "data/processed") -> dict:
    spark = iniciar_spark()
    os.makedirs(output_base_path, exist_ok=True)
    processed_paths = {}

    for dataset_name, file_path in input_paths.items():
        logger.info("Processando transformações na base de %s...", dataset_name)
        df_bruto = spark.read.csv(file_path, header=True, inferSchema=True)
        
        df_limpo = clean_and_transform(df_bruto)
        
        output_path = os.path.join(output_base_path, f"{dataset_name}_cleaned.parquet")
        # Gravando em formato colunar Parquet otimizado para consultas [cite: 18]
        df_limpo.write.mode("overwrite").parquet(output_path)
        logger.info("✔ Base %s limpa e gravada em Parquet.", dataset_name)
        processed_paths[dataset_name] = output_path
        
    return processed_paths