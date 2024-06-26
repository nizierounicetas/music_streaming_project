import os
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.operators.dummy_operator import DummyOperator
import datetime

PROJECT_ID = os.environ.get("PROJECT_ID", "music-streaming-project")
DAG_ID = "stage_to_core"
CLUSTER_NAME = os.environ.get(
    "DATAPROC_CLUSTER_NAME", "music_dataproc_cluster")
REGION = os.environ.get("REGION", "us-central1")

loading_date = (datetime.date.today() -
                datetime.timedelta(days=1)).strftime("%d.%m.%Y")

with DAG(
        DAG_ID,
        schedule_interval=datetime.timedelta(days=1),
        start_date=datetime.datetime(2024, 3, 1),
        catchup=False
) as dag:
    start_task = DummyOperator(
        task_id='start-task',
        dag=dag,
    )

    listen_events = DataprocSubmitJobOperator(
        task_id='listen_events',
        project_id=PROJECT_ID,
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": "file:///home/nikben2105/music_streaming_project/spark/core_main.py",
                "args": ["listen_events", loading_date],
                "jar_files_uris": ["gs://spark-lib/bigquery/spark-bigquery-latest.jar"]}
        },
        region=REGION)

    auth_events = DataprocSubmitJobOperator(
        task_id='auth_events',
        project_id=PROJECT_ID,
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": "file:///home/nikben2105/music_streaming_project/spark/core_main.py",
                "args": ['auth_events', loading_date],
                "jar_files_uris": ["gs://spark-lib/bigquery/spark-bigquery-latest.jar"]}
        },
        region=REGION)

    page_views = DataprocSubmitJobOperator(
        task_id='page_views',
        project_id=PROJECT_ID,
        job={
            "reference": {"project_id": PROJECT_ID},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": "file:///home/nikben2105/music_streaming_project/spark/core_main.py",
                "args": ['page_view_events', loading_date],
                "jar_files_uris": ["gs://spark-lib/bigquery/spark-bigquery-latest.jar"]}
        },
        region=REGION)

    end_task = DummyOperator(
        task_id='end-task',
        dag=dag,
    )

    start_task >> [listen_events, auth_events, page_views] >> end_task
