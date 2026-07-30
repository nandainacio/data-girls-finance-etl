FROM apache/airflow:2.7.3-python3.10

USER root

# Instala o Java + procps (necessário para o PySpark gerenciar os processos Java)
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-11-jre-headless procps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Aponta para o link simbólico padrão do Java no Debian
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

# Instala as dependências Python
RUN pip install --no-cache-dir kaggle polars boto3