from datetime import timedelta

import pendulum
from airflow.sdk import dag, task

from scripts.taxi_pipeline import run_pipeline
from scripts.validate_taxi_data import validate_taxi_data
from scripts.answer_workshop_questions import answer_workshop_questions

@dag(
    dag_id="zoomcamp_taxi_pipeline",
    description="Loads NYC taxi data from the Zoomcamp API into S3",
    start_date=pendulum.datetime(2026, 7, 14, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["zoomcamp", "dlt", "s3"],
)
def zoomcamp_taxi_pipeline():
    @task
    def ingest_taxi_data() -> None:
        run_pipeline()

    @task
    def validate_parquet_data() -> None:
        validate_taxi_data()

    @task
    def answer_workshop_questions_task() -> None:
        answer_workshop_questions()

    ingestion = ingest_taxi_data()
    validation = validate_parquet_data()
    workshop_answers = answer_workshop_questions_task()

    ingestion >> validation >> workshop_answers


zoomcamp_taxi_pipeline()
