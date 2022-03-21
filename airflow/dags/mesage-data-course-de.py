from datetime import datetime
import os
import logging
from glob import glob
import ast

from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator

from google.cloud import storage


PATH_TO_LOCAL_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
DATA_SOURCE_ROOT = "assets/slack-data" 
CHANNEL_NAME = "course-data-engineering"

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", 'dtc-capstone-344019')
BUCKET = os.environ.get("GCP_GCS_BUCKET", 'dtc_capstone_344019_data-lake')
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'dtc_capstone_344019_all_data')

def find_files(logical_date:str, **kwargs):
    prefix_yy_mm = "-".join(logical_date.split('-')[:-2])
    files = glob(f'{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix_yy_mm}-*.json')

    task_instance = kwargs['ti']
    task_instance.xcom_push(key="files", value=files)
    logging.info("XCOM variable files is successfully pushed..")

def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

def upload_to_gcs_month(bucket, object_prefix ,files):
    files=ast.literal_eval(files)
    for file in files:
        filename = file.split("/")[-1]
        upload_to_gcs(bucket, f'{object_prefix}/{filename}', file)


# Read files from the GCS and store locally.
# Read with spark, clean the unwanted columns
# big question tbh ?? How to handle with complex data structure, are we going to create new files for them or not?


# Store in DWH


default_args = {
    "owner": "airflow",
    "start_date": datetime(2020, 11, 22),
    "end_date": datetime(2022, 4, 22),
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="course-data-engineering-V1",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=['dtc-capstone'],
) as dag:

    with TaskGroup("upload-raw-data") as upload_raw_data:

        files_for_month = PythonOperator(
                            task_id="files_for_month",
                            python_callable=find_files,
                            provide_context=True,
                            op_kwargs={
                                "logical_date": '{{ ds }}'
                            },
                        )
        upload_raw_files = PythonOperator(
                            task_id="upload_files",
                            python_callable=upload_to_gcs_month,
                            provide_context=True,
                            op_kwargs={
                                "bucket": BUCKET,
                                "object_prefix": "raw/messages/data-engineering",
                                "files": f'{{{{ ti.xcom_pull(key="files") }}}}',
                            },
                        )
        files_for_month >> upload_raw_files


    upload_raw_data
