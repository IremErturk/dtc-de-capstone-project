from datetime import datetime

from config import BIGQUERY_DATASET, BUCKET, PROJECT_ID

from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryUpsertTableOperator,
)

# BigQueryExecuteQueryOperator
# BigQueryCreateExternalTableOperator


# Configure parameters:
CHANNEL_NAME = "course-data-engineering"

channels = {
    "course-data-engineering": [
        "_reactions",
        "_root_messages",
        "_thread_replies",
    ],  # parquet, csv, csv
    "course-ml-zoomcamps": [
        "_reactions",
        "_root_messages",
        "_thread_replies",
    ],  # parquet, csv, csv
}


START_DATE = datetime(2021, 6, 18)
END_DATE = datetime(2022, 5, 18)

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 3, 24),
    # "end_date": END_DATE,
    "depends_on_past": False,
    "retries": 3,
}


with DAG(
    dag_id="gcs-2-dwh2",
    schedule_interval="@once",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=["dtc-capstone"],
) as dag:

    create_root_messages_table = BigQueryUpsertTableOperator(
        task_id="root_messages_table",
        dataset_id=BIGQUERY_DATASET,
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": f"root_messages_{CHANNEL_NAME}",
            },
            "schema": {
                "fields": [
                    {"name": "client_msg_id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "user", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "ts", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "text", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "reply_count", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "channel_name", "type": "STRING", "mode": "NULLABLE"},
                ]
            },
            # "clustering":
            # "rangePartition" :
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [
                    f"gs://{BUCKET}/clean/message-data/{CHANNEL_NAME}*_rootmessages.parquet"
                ],
            },
        },
    )

    create_thread_replies_table = BigQueryUpsertTableOperator(
        task_id="thread_replies_table",
        dataset_id=BIGQUERY_DATASET,
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": f"thread_replies_{CHANNEL_NAME}",
            },
            "schema": {
                "fields": [
                    {"name": "client_msg_id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "user", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "parent_user_id", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "text", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "ts", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "thread_ts", "type": "STRING", "mode": "NULLABLE"},
                    {"name": "reply_count", "type": "FLOAT", "mode": "NULLABLE"},
                    {"name": "channel_name", "type": "STRING", "mode": "NULLABLE"},
                ]
            },
            # "clustering":
            # "rangePartition" :
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [
                    f"gs://{BUCKET}/clean/message-data/{CHANNEL_NAME}*_threadreplies.parquet"
                ],
            },
        },
    )

    create_reactions_table = BigQueryUpsertTableOperator(
        task_id="reactions_table",
        dataset_id=BIGQUERY_DATASET,
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "reactions",
            },
            # "schema" :
            #     { "fields": [
            #         {"name": "client_msg_id", "type":"STRING", "mode":"REQUIRED"},
            #         {"name":"name","type":"STRING", "mode":"REQUIRED"},
            #         {"name":"count","type":"INTEGER", "mode":"REQUIRED"},
            #         {"name":"users","type":"STRING", "mode":"REQUIRED"},
            #     ]},
            # "clustering":
            # "rangePartition" :
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [
                    f"gs://{BUCKET}/clean/message-data/{CHANNEL_NAME}*_reactions.parquet"
                ],
            },
        },
    )
