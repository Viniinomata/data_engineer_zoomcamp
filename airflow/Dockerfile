ARG AIRFLOW_IMAGE_NAME=apache/airflow:3.3.0

FROM ${AIRFLOW_IMAGE_NAME}

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt