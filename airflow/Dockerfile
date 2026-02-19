FROM apache/airflow:2.11.0

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
USER airflow

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt