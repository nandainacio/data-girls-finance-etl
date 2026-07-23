FROM apache/airflow:2.7.3-python3.10

USER root

# Instala o Java (JRE) necessário para o PySpark
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-11-jre-headless \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Define a variável de ambiente para o Java
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Instala as suas dependências do Python de uma vez
RUN pip install --no-cache-dir kaggle pyspark boto3