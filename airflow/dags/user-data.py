import os
from datetime import datetime

from config import (
    BIGQUERY_DATASET,
    BUCKET,
    DATA_SOURCE_ROOT,
    PATH_TO_LOCAL_HOME,
    PROJECT_ID,
    user_schema,
)
from google.cloud import storage
from pyspark.sql import SparkSession, types
from pyspark.sql.functions import col

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateExternalTableOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_local import (
    GCSToLocalFilesystemOperator,
)
from airflow.utils.task_group import TaskGroup

USERS_DATA = "users.json"

# Data Specific Constants
COLS_TO_DROP = [
    "profile",
    "color",
    "who_can_share_contact_card",
    "team_id",
    "_corrupt_record",
]
COLS_BY_TOPIC = {
    "identity": ["name", "real_name"],
    "location": ["tz", "tz_label", "tz_offset"],
    "status": [
        "deleted",
        "is_admin",
        "is_owner",
        "is_primary_owner",
        "is_restricted",
        "is_ultra_restricted",
        "is_bot",
        "is_email_confirmed",
    ],
}

schema = types.StructType(
    [
        types.StructField("deleted", types.BooleanType(), True),
        types.StructField("id", types.StringType(), True),
        types.StructField("is_admin", types.BooleanType(), True),
        types.StructField("is_app_user", types.BooleanType(), True),
        types.StructField("is_bot", types.BooleanType(), True),
        types.StructField("is_email_confirmed", types.BooleanType(), True),
        types.StructField("is_invited_user", types.BooleanType(), True),
        types.StructField("is_owner", types.BooleanType(), True),
        types.StructField("is_primary_owner", types.BooleanType(), True),
        types.StructField("is_restricted", types.BooleanType(), True),
        types.StructField("is_ultra_restricted", types.BooleanType(), True),
        types.StructField("name", types.StringType(), True),
        types.StructField("real_name", types.StringType(), True),
        types.StructField("tz", types.StringType(), True),
        types.StructField("tz_label", types.StringType(), True),
        types.StructField("tz_offset", types.IntegerType(), True),
        types.StructField("updated", types.LongType(), True),
    ]
)


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


def extract_n_transform(spark: SparkSession):
    # Read Local Data and
    try:
        users = spark.read.schema(user_schema).json(
            f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{USERS_DATA}"
        )
        users = users.drop(*COLS_TO_DROP)
        users = users.where(col("id").isNotNull())
        drop_expr = " and ".join('(%s != "")' % col_name for col_name in users.columns)
        users.filter(drop_expr)
        return users
    except IOError as e:
        print(f"{e.message}: on {PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{USERS_DATA}")
        exit


def initialize_spark():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName(f"{PROJECT_ID}-spark")
        .getOrCreate()
    )

    # task_instance = kwargs['ti']
    # task_instance.xcom_push(key="spark_session", value=spark)
    # logging.info("XCOM variables spark_session is successfully pushed..")
    return spark


def stop_spark(spark: SparkSession):
    spark.stop()


def format_dataset_and_save_locally(temp_file):
    spark_session = initialize_spark()
    # extract and transform
    users_df = extract_n_transform(spark_session)
    # save locally
    users_df.toPandas().to_parquet(temp_file, index=False)

    stop_spark(spark=spark_session)


def split_user_data_by_attributes(input_path, bucket, target_objects):
    spark_session = initialize_spark()
    users = spark_session.read.parquet(input_path)

    for topic in target_objects.keys():
        interested_columns = ["id"] + COLS_BY_TOPIC[topic]
        df_topic = users.select(interested_columns)
        temp_file = f"{PATH_TO_LOCAL_HOME}/temp_{topic}.parquet"
        df_topic.toPandas().to_parquet(temp_file, index=False)
        upload_to_gcs(bucket, target_objects[topic], temp_file)

    stop_spark(spark_session)


default_args = {
    "owner": "airflow",
    "start_date": datetime(2019, 1, 1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="users-data",
    schedule_interval="@once",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=["dtc-capstone"],
) as dag:

    upload_raw_data_to_gcs = PythonOperator(
        task_id="upload_raw_data_to_gcs",
        python_callable=upload_to_gcs,
        provide_context=True,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/user-data/{USERS_DATA}",
            "local_file": f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{USERS_DATA}",
        },
    )

    with TaskGroup("transform-and-upload-to-gcs") as transform_and_upload_to_gcs:
        transform_and_save_locally = PythonOperator(
            task_id="transform_and_save_locally",
            python_callable=format_dataset_and_save_locally,
            op_kwargs={
                "temp_file": f"{PATH_TO_LOCAL_HOME}/temp.parquet",
            },
        )

        upload_clean_data_to_gcs = PythonOperator(
            task_id="upload_clean_data_to_gcs",
            python_callable=upload_to_gcs,
            provide_context=True,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": "clean/user-data/users.parquet",
                "local_file": f"{PATH_TO_LOCAL_HOME}/temp.parquet",
            },
        )

        cleanup = BashOperator(
            task_id="cleanup-file-system",
            bash_command=f"rm {PATH_TO_LOCAL_HOME}/temp.parquet",
        )

        transform_and_save_locally >> upload_clean_data_to_gcs >> cleanup

    with TaskGroup("create-data-subsets") as create_data_subsets:

        download_users_file = GCSToLocalFilesystemOperator(
            task_id="download_users_from_gcs",
            object_name="clean/user-data/users.parquet",
            bucket=BUCKET,
            filename=f"{PATH_TO_LOCAL_HOME}/temp.parquet",
        )

        split_user_data_on_attributes = PythonOperator(
            task_id="split_user_attributes",
            python_callable=split_user_data_by_attributes,
            provide_context=True,
            op_kwargs={
                "input_path": f"{PATH_TO_LOCAL_HOME}/temp.parquet",
                "bucket": BUCKET,
                "target_objects": {
                    "identity": "clean/user-data/users_identity.parquet",
                    "location": "clean/user-data/users_location.parquet",
                    "status": "clean/user-data/users_status.parquet",
                },
            },
        )

        cleanup = BashOperator(
            task_id="cleanup-file-system", bash_command=f"rm {PATH_TO_LOCAL_HOME}/temp*"
        )

        download_users_file >> split_user_data_on_attributes >> cleanup

    with TaskGroup("create-external-tables") as create_external_tables:

        external_table_users = BigQueryCreateExternalTableOperator(
            task_id="external_table_users",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": "ext_users",
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [f"gs://{BUCKET}/clean/user-data/users.parquet"],
                },
            },
        )

        external_table_locations = BigQueryCreateExternalTableOperator(
            task_id="external_table_ids",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": "ext_users_identity",
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [
                        f"gs://{BUCKET}/clean/user-data/users_identity.parquet"
                    ],
                },
            },
        )
        external_table_locations = BigQueryCreateExternalTableOperator(
            task_id="external_table_locations",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": "ext_users_location",
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [
                        f"gs://{BUCKET}/clean/user-data/users_location.parquet"
                    ],
                },
            },
        )
        external_table_statuses = BigQueryCreateExternalTableOperator(
            task_id="external_table_statuses",
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": "ext_users_status",
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [
                        f"gs://{BUCKET}/clean/user-data/users_status.parquet"
                    ],
                },
            },
        )

    (
        upload_raw_data_to_gcs
        >> transform_and_upload_to_gcs
        >> create_data_subsets
        >> create_external_tables
    )
