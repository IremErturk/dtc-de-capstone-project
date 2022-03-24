import logging
import os
import re
import time
from datetime import datetime
from glob import glob

from google.cloud import storage
from pyspark.sql import SparkSession, types
from pyspark.sql.functions import col, explode

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.task_group import TaskGroup

PATH_TO_LOCAL_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
DATA_SOURCE_ROOT = "assets/slack-data"
CHANNEL_NAME = "course-data-engineering"

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "dtc-capstone-344019")
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc_capstone_344019_data-lake")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "dtc_capstone_344019_all_data")

message_schema = types.StructType(
    [
        types.StructField("client_msg_id", types.StringType(), False),
        types.StructField("parent_user_id", types.StringType(), True),
        types.StructField("text", types.StringType(), True),  # ->
        types.StructField("type", types.StringType(), True),
        types.StructField("subtype", types.StringType(), True),
        types.StructField("user", types.StringType(), True),  # -> id and user fk.
        types.StructField(
            "ts", types.StringType(), True
        ),  # -> epoch to human readable format
        types.StructField("thread_ts", types.StringType(), True),
        types.StructField("reply_count", types.IntegerType(), True),
        types.StructField(
            "reactions",
            types.ArrayType(
                types.StructType(
                    [
                        types.StructField("count", types.LongType(), True),
                        types.StructField("name", types.StringType(), True),
                        types.StructField(
                            "users", types.ArrayType(types.StringType(), True), True
                        ),
                    ]
                )
            ),
            True,
        ),
    ]
)


def check_condition(logical_date: str, **kwargs):
    prefix_yy_mm = "-".join(logical_date.split("-")[:-1])
    # Push prefix to avoid re-calculation
    task_instance = kwargs["ti"]
    task_instance.xcom_push(key="prefix", value=prefix_yy_mm)
    logging.info("XCOM variable files is successfully pushed..")

    files = glob(
        f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix_yy_mm}-*.json"
    )

    if len(files) == 0 or files is None:
        return "skip"
    else:
        return "upload-raw-data.upload_files"


def upload_file_to_gcs(bucket, object_name, local_file):
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


def upload_files_to_gcs(bucket, object_prefix, prefix, **kwargs):
    files = glob(
        f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix}-*.json"
    )
    for file in files:
        filename = file.split("/")[-1]
        upload_file_to_gcs(bucket, f"{object_prefix}/{filename}", file)


def upload_local_directory_to_gcs(bucket_name, gcs_path, local_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    assert os.path.isdir(local_path)  # Works only with local_paths that are directory
    for local_file in glob(local_path + "/**", recursive=True):
        if os.path.isfile(local_file):
            remote_path = os.path.join(gcs_path, local_file[1 + len(local_path) :])
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


def upload_df_to_gcs(bucket_obj, object_name, df):
    blob = bucket_obj.blob(object_name)
    blob.upload_from_string(df, "text/csv")


def initialize_gcp(bucket_name):
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
    bucket = client.bucket(bucket_name)
    return bucket


def initialize_spark():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName(f"{PROJECT_ID}-spark")
        .getOrCreate()
    )
    return spark


def stop_spark(spark: SparkSession):
    spark.stop()


# Transformation  Functions
def epoch_2_datetime(epoch):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))


def clean_message_text(text):
    user_pattern = re.compile(r"<@(.+?)>")
    link_pattern_text = re.compile(r"<(http.+?)\|(.+?)>")
    link_pattern = re.compile(r"<(http.+?)>")

    text = (
        text.replace("\xa0", " ")
        .replace("•", "-")
        .replace("\n\n", "\n")
        .replace("'", "")
        .replace("`", "")
    )
    text = re.sub("\n", " ", text)
    text = user_pattern.sub("", text)
    text = link_pattern_text.sub("", text)
    text = link_pattern.sub("", text)
    return text.strip()


def tokenize_text(text):
    # todo
    pass


def extract_reactions_data(df):
    reactions_df = df.where((col("reactions").isNotNull()))
    reactions_df = reactions_df.select(["client_msg_id", "reactions"])
    reactions_df = reactions_df.withColumn("reaction", explode("reactions")).drop(
        "reactions"
    )
    reactions_df = reactions_df.select(
        ["client_msg_id", "reaction.name", "reaction.count", "reaction.users"]
    )
    return reactions_df


def transform_message_data(bucket_name, object_prefix, prefix):

    # file-names
    source_data_path = f"{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix}-*.json"
    target_reactions = f"{PATH_TO_LOCAL_HOME}/assets/temp/{CHANNEL_NAME}/{prefix}/{prefix}_reactions.parquet"
    target_messages = f"{object_prefix}/{prefix}_messages.csv"
    target_root_messages = f"{object_prefix}/{prefix}_root_messages.csv"
    target_thread_replies = f"{object_prefix}/{prefix}_thread_replies.csv"

    spark_session = initialize_spark()
    bucket = initialize_gcp(bucket_name)

    # transform 1: all_message_data for given year-month
    message_data = spark_session.read.schema(message_schema).json(
        source_data_path, multiLine=True
    )

    # transform 2: clean unwanted subtype (thread_broadcast, channel_join)
    # this step cause, all values for 'inviter' and 'root' become null
    message_data = message_data.where(
        (col("subtype").isNull())
        | ((col("subtype") != "thread_broadcast") & (col("subtype") != "channel_join"))
    )

    # transform 3: Extract reactions data
    # if "reactions" in existing_columns:
    reactions_data = extract_reactions_data(message_data)
    reactions_data.write.format("parquet").mode("overwrite").save(target_reactions)

    # --> convert message_data pyspark dataframe to pandas dataframe
    message_data = message_data.toPandas()

    # transform 4: cleanup the text column in messages.
    message_data["text"] = message_data["text"].apply(lambda x: clean_message_text(x))
    upload_df_to_gcs(
        bucket,
        target_messages,
        message_data.to_csv(header=True, index=False),
    )

    # transform 6: split messages in : root_level and thread_replies messages
    thread_replies = message_data[message_data.parent_user_id.notnull()]
    root_messages = message_data[message_data.parent_user_id.isnull()]

    # transform 7: epoch to datetime.. for ts and thread_ts columns
    root_messages = root_messages.astype({"ts": float, "thread_ts": float})
    root_messages["ts"] = root_messages["ts"].apply(lambda x: epoch_2_datetime(x))

    thread_replies = thread_replies.astype({"ts": float, "thread_ts": float})
    thread_replies["ts"] = thread_replies["ts"].apply(lambda x: epoch_2_datetime(x))
    thread_replies["thread_ts"] = thread_replies["thread_ts"].apply(
        lambda x: epoch_2_datetime(x)
    )

    upload_df_to_gcs(
        bucket, target_root_messages, root_messages.to_csv(header=True, index=False)
    )
    upload_df_to_gcs(
        bucket, target_thread_replies, thread_replies.to_csv(header=True, index=False)
    )

    stop_spark(spark_session)


default_args = {
    "owner": "airflow",
    "start_date": datetime(2020, 10, 22),
    "end_date": datetime(2022, 5, 22),
    "depends_on_past": False,
    "retries": 3,
}


with DAG(
    dag_id="messages-pipeline",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=["dtc-capstone"],
) as dag:

    prep_tasks = BranchPythonOperator(
        task_id="check-data-availability",
        python_callable=check_condition,
        provide_context=True,
        op_kwargs={"logical_date": "{{ ds }}"},
    )

    to_skip = DummyOperator(dag=dag, task_id="skip")

    with TaskGroup("upload-raw-data") as upload_raw_data:
        upload_raw_files = PythonOperator(
            task_id="upload_files",
            python_callable=upload_files_to_gcs,
            provide_context=True,
            op_kwargs={
                "bucket": BUCKET,
                "object_prefix": f"raw/messages/{CHANNEL_NAME}",
                "prefix": f'{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

    with TaskGroup(
        "data-cleanup-and-transformation"
    ) as data_cleanup_and_transformation:

        prep = BashOperator(
            task_id="prep",
            bash_command=f'mkdir -p {PATH_TO_LOCAL_HOME}/assets/temp/{CHANNEL_NAME}/{{{{ ti.xcom_pull(key="prefix") }}}}',
        )

        transform_data = PythonOperator(
            task_id="transform_data",
            python_callable=transform_message_data,
            provide_context=True,
            op_kwargs={
                "bucket_name": BUCKET,
                "object_prefix": f"clean/messages/{CHANNEL_NAME}",
                "prefix": f'{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

        prep >> transform_data

    with TaskGroup("upload-transfered-data-to-gcs") as upload_transfered_data_to_gcs:
        upload_messages = PythonOperator(
            task_id="messages",
            python_callable=upload_local_directory_to_gcs,
            provide_context=True,
            op_kwargs={
                "bucket_name": BUCKET,
                "gcs_path": f"clean/messages/{CHANNEL_NAME}/",
                "local_path": f'{PATH_TO_LOCAL_HOME}/assets/temp/{CHANNEL_NAME}/{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

    cleanup = BashOperator(
        task_id="cleanup-temporary-files",
        bash_command=f'rm -rf {PATH_TO_LOCAL_HOME}/assets/temp/{CHANNEL_NAME}/{{{{ ti.xcom_pull(key="prefix") }}}}/',
    )

    (
        prep_tasks
        >> upload_raw_data
        >> data_cleanup_and_transformation
        >> upload_transfered_data_to_gcs
        >> cleanup
    )
    prep_tasks >> to_skip
