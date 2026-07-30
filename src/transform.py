import os
import logging
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_and_transform(df: pl.DataFrame) -> pl.DataFrame:
    """
    Realiza a limpeza e transformação do DataFrame usando Polars.
    """

    df = df.unique()

    colunas_int = ['Age', 'Num_of_Loan', 'Num_of_Delayed_Payment']
    colunas_double = [
        'Annual_Income', 'Changed_Credit_Limit', 
        'Outstanding_Debt', 'Amount_invested_monthly', 'Monthly_Balance'
    ]


    exprs = []

    for coluna in colunas_int:
        if coluna in df.columns:
            exprs.append(
                pl.col(coluna)
                .cast(pl.Utf8)
                .str.replace_all(r"[^0-9]", "")
                .cast(pl.Int32, strict=False)
            )

    for coluna in colunas_double:
        if coluna in df.columns:
            exprs.append(
                pl.col(coluna)
                .cast(pl.Utf8)
                .str.replace_all(r"[^0-9.]", "")
                .cast(pl.Float64, strict=False)
            )

    if exprs:
        df = df.with_columns(exprs)


    if 'Age' in df.columns:
        mediana_idade = df['Age'].median()
        val_mediana = int(mediana_idade) if mediana_idade is not None else 0
        df = df.with_columns(pl.col('Age').fill_null(val_mediana))


    colunas_double_presentes = [col for col in colunas_double if col in df.columns]
    if colunas_double_presentes:
        df = df.with_columns(
            [pl.col(col).fill_null(0.0) for col in colunas_double_presentes]
        )

    return df


def run_transformation(input_paths: dict, output_base_path: str = "data/processed") -> dict:
    """
    Lê os arquivos de entrada, aplica a transformação e grava os resultados em formato Parquet.
    """
    os.makedirs(output_base_path, exist_ok=True)
    processed_paths = {}

    for dataset_name, file_path in input_paths.items():
        logger.info("Processando transformações na base de %s com Polars...", dataset_name)
        
        df_bruto = pl.read_csv(file_path, infer_schema_length=10000, ignore_errors=True)
        
        df_limpo = clean_and_transform(df_bruto)
        
        output_path = os.path.join(output_base_path, f"{dataset_name}_cleaned.parquet")
        df_limpo.write_parquet(output_path)
        
        logger.info("✔ Base %s limpa e gravada em Parquet em: %s", dataset_name, output_path)
        processed_paths[dataset_name] = output_path

    return processed_paths